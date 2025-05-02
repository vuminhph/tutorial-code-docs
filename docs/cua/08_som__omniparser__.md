---
layout: default
title: "SOM (OmniParser)"
parent: "Computer Use Agent (CUA)"
nav_order: 8
---

# Chapter 8: SOM (OmniParser)

In [Chapter 7: PyLume](07_pylume_.md), we saw how `PyLume` manages the virtual machines where our agent operates. We have the environment set up, but how does the agent actually _understand_ what's happening inside that environment? When the [Computer Interface](02_computer_interface__basecomputerinterface___macoscomputerinterface__.md) takes a screenshot, the agent gets a picture, like a photograph. But just looking at a photo isn't enough.

Imagine you're trying to follow cooking instructions that say "Click the 'Start Timer' button." If you just have a photo of the oven controls, how do you know _exactly where_ that button is? You need a way to identify the button within the photo and locate it. Our AI agent faces the same challenge with screenshots. It needs more than just pixels; it needs to recognize the different parts of the screen – the buttons, icons, text fields, and the text itself.

This is where **SOM (OmniParser)** comes in. It acts like specialized glasses for the agent, allowing it to not just see the screen, but _understand_ its structure.

## What is SOM (OmniParser)?

**SOM** stands for "**S**et-**o**f-**M**ark". Think of it as the agent's advanced **vision system**, specifically designed to work with the `OmniLoop` strategy we briefly mentioned in [Chapter 4: Agent Loop (BaseLoop / Provider Loops)](04_agent_loop__baseloop___provider_loops__.md).

While the basic [Computer Interface](02_computer_interface__basecomputerinterface___macoscomputerinterface__.md) provides the raw `screenshot()`, SOM takes that screenshot and analyzes it deeply. It's like putting on glasses that automatically highlight and label everything important on the screen.

Here's what SOM does:

1.  **Receives Screenshot:** It takes the image data provided by the [Computer Interface](02_computer_interface__basecomputerinterface___macoscomputerinterface__.md).
2.  **Analyzes with AI:** It uses sophisticated computer vision models:
    - **YOLO (You Only Look Once):** A fast object detection model trained to find common UI elements like icons, buttons, input fields, checkboxes, etc.
    - **OCR (Optical Character Recognition):** A technology (like EasyOCR) used to read and extract any visible text on the screen.
3.  **Generates Structured Data:** Instead of just giving back a picture, SOM outputs a structured description of the screen. This includes:
    - **Bounding Boxes:** Rectangular coordinates (`[x1, y1, x2, y2]`) drawn around each detected element (icon or text).
    - **Element Type:** Labels identifying whether an element is an `icon` or `text`.
    - **Text Content:** For text elements, the actual text that was read.
    - **IDs:** A unique number assigned to each bounding box (e.g., Box #1, Box #2).
    - **Annotated Image:** A copy of the screenshot with the bounding boxes and IDs drawn directly onto it, making it easy for humans (and potentially the AI) to visualize the detected elements.

This structured information allows the agent (specifically, the AI model guiding the agent) to understand the screen layout and refer to elements precisely. For example, instead of guessing where a button is, the AI can say, "Perform a left click inside the bounding box with ID 5," which corresponds to the 'Submit' button.

## Key Concepts Breakdown

Let's break down how SOM works:

- **Screenshot Analysis:** SOM starts with the raw pixel data from a screenshot captured by the [Computer Interface](02_computer_interface__basecomputerinterface___macoscomputerinterface__.md).

- **Icon/Element Detection (YOLO):** SOM uses a pre-trained YOLO model (specifically, the `microsoft/OmniParser-v2.0` model, see `libs/som/som/detection.py`) to quickly scan the image and identify regions that _look like_ typical UI elements. It draws bounding boxes around these potential icons or buttons.

- **Text Recognition (OCR):** Simultaneously or subsequently, SOM uses an OCR engine (like EasyOCR, see `libs/som/som/ocr.py`) to find and read text blocks within the image. It also gets bounding boxes for these text regions.

- **Combining and Refining (NMS):** Often, the initial YOLO and OCR detections might overlap significantly (e.g., a button icon and the text label on it). SOM uses a technique called Non-Maximum Suppression (NMS) to merge or filter out highly overlapping boxes, keeping the most relevant ones. It also cleverly filters out detected "icon" boxes if their center falls within a detected text box, prioritizing the recognized text in those cases.

- **Assigning IDs:** Each final, unique bounding box (whether for an icon or text) is assigned a sequential ID number (starting from 1).

- **Output (`ParseResult`):** All this information – the list of identified elements (`UIElement` objects, each with an ID, type, bounding box, and text content if applicable) along with the annotated screenshot image – is packaged into a `ParseResult` object (defined in `libs/som/som/models.py`).

## How is SOM Used? (Inside the OmniLoop)

You typically don't call SOM directly in your agent script. Instead, it's a component used internally by specific agent loops, most notably the `OmniLoop` (found in `libs/agent/agent/providers/omni/loop.py`).

Here’s the simplified flow during the "Observe" phase of the `OmniLoop`:

1.  **Loop Needs to See:** The `OmniLoop` decides it's time to look at the screen.
2.  **Get Screenshot:** It calls `await computer.interface.screenshot()` via the [Computer Interface](02_computer_interface__basecomputerinterface___macoscomputerinterface__.md).
3.  **Analyze with SOM:** It takes the screenshot bytes and passes them to its internal `OmniParser` instance (which uses the SOM library). It calls a method like `parser.parse_screen(computer)`. (See `libs/agent/agent/providers/omni/parser.py`)
4.  **SOM Does Its Magic:** The SOM parser performs the YOLO detection, OCR, filtering, and ID assignment as described above.
5.  **Loop Receives Results:** The `OmniLoop` gets back the `ParseResult` object containing the list of `UIElement`s and the annotated image.
6.  **Inform the AI:** The `OmniLoop` then prepares the prompt for the AI model (like GPT-4o or Claude 3). This prompt usually includes:
    - The task description.
    - The conversation history.
    - **Crucially:** The annotated screenshot image _and_ the list of detected elements with their IDs and text content.

Now, when the AI reasons about the next step, it can refer to the visual elements using their IDs. It might respond with an action like: "Click the element with ID 7 (which is the 'Login' button)". The `OmniLoop` then uses the bounding box information from the `ParseResult` to calculate the coordinates for the click.

## Internal Implementation: A Look Under the Hood

Let's trace the `parse` call within SOM:

1.  **Input:** The `OmniParser.parse` method in `libs/som/som/detect.py` receives the raw screenshot bytes.
2.  **Image Prep:** It converts the bytes into a usable image format (PIL Image).
3.  **Icon Detection:** It calls its internal `DetectionProcessor` (`libs/som/som/detection.py`), which loads the YOLO model (if not already loaded) and runs `model.predict()` on the image. This yields a list of potential icon/element detections with confidence scores and bounding boxes.
4.  **Text Detection:** If OCR is enabled, it calls its internal `OCRProcessor` (`libs/som/som/ocr.py`), which initializes EasyOCR (if not already loaded) and runs `reader.readtext()` on the image. This yields a list of text detections with content, confidence, and bounding boxes.
5.  **Combine & Filter:** The `OmniParser` takes both sets of detections. It filters out low-confidence text results. It performs Non-Maximum Suppression (NMS) using `torchvision.ops.nms` to remove redundant, highly overlapping boxes from the combined list. It also implements the logic to remove icon boxes whose centers overlap with text boxes.
6.  **Assign IDs & Annotate:** It assigns sequential IDs (1, 2, 3...) to the final list of elements. It uses its `BoxAnnotator` (`libs/som/som/visualization.py`) to draw these numbered boxes onto a copy of the original screenshot.
7.  **Package Result:** It creates `IconElement` and `TextElement` objects (from `libs/som/som/models.py`) for each detection and bundles them into a `ParseResult` object, which also includes the base64-encoded annotated image and metadata (like processing time, device used).
8.  **Return:** The `ParseResult` is returned to the caller (usually the `OmniLoop`).

Here's a simplified sequence diagram:

```mermaid
sequenceDiagram
    participant Loop as AgentLoop (OmniLoop)
    participant Parser as OmniParser (SOM)
    participant Detector as DetectionProcessor (YOLO)
    participant OCR as OCRProcessor (EasyOCR)
    participant Annotator as BoxAnnotator

    Loop->>+Parser: parse(screenshot_bytes)
    Parser->>Parser: Prepare Image
    Parser->>+Detector: detect_icons(image)
    Detector-->>-Parser: Icon Detections
    Parser->>+OCR: detect_text(image)
    OCR-->>-Parser: Text Detections
    Parser->>Parser: Combine & Filter (NMS)
    Parser->>+Annotator: draw_boxes(image, final_detections)
    Annotator-->>-Parser: annotated_image
    Parser->>Parser: Package ParseResult (elements, annotated_image)
    Parser-->>-Loop: ParseResult
```

## Example Output (Conceptual)

After SOM processes a screenshot, the `OmniLoop` might receive a `ParseResult` containing:

- **`elements`**: A list like:
  - `IconElement(id=1, type='icon', bbox=BoundingBox(x1=0.1, y1=0.1, x2=0.15, y2=0.18), confidence=0.92)`
  - `TextElement(id=2, type='text', bbox=BoundingBox(x1=0.2, y1=0.2, x2=0.4, y2=0.25), content='Username:', confidence=0.98)`
  - `IconElement(id=3, type='icon', bbox=BoundingBox(x1=0.2, y1=0.3, x2=0.8, y2=0.35), confidence=0.85)` (Maybe a text input field)
  - `TextElement(id=4, type='text', bbox=BoundingBox(x1=0.4, y1=0.4, x2=0.6, y2=0.45), content='Login', confidence=0.99)` (Maybe on a button)
- **`annotated_image_base64`**: A base64 string representing the screenshot PNG image, but with colored rectangles drawn around the elements, labeled "1", "2", "3", "4".

This structured data is much more useful for the AI than just the raw image.

## Code Snippets

**1. The Parser Entry Point (`libs/som/som/detect.py`)**

This shows the main `parse` method that orchestrates the process.

```python
# Simplified from libs/som/som/detect.py
class OmniParser:
    # ... (init sets up detector, ocr, visualizer) ...

    def parse(
        self,
        screenshot_data: Union[bytes, str],
        box_threshold: float = 0.3,
        iou_threshold: float = 0.1,
        use_ocr: bool = True,
    ) -> ParseResult:
        start_time = time.time()

        # 1. Load image from bytes or base64
        if isinstance(screenshot_data, str):
            screenshot_data = base64.b64decode(screenshot_data)
        image = Image.open(io.BytesIO(screenshot_data)).convert("RGB")

        # 2. Process image (calls internal method)
        annotated_image, elements = self.process_image(
            image=image,
            box_threshold=box_threshold,
            iou_threshold=iou_threshold,
            use_ocr=use_ocr, # This method calls detector.detect_icons and ocr.detect_text
        )

        # 3. Convert annotated image to base64
        # ... (image saving to buffer and base64 encoding) ...
        annotated_image_base64 = # ... encoded string ...

        # 4. Generate screen info text and assign IDs
        # ... (loop through elements, set IDs, create descriptions) ...
        screen_info = []
        parsed_content_list = []
        for i, elem in enumerate(elements):
            elem.id = i + 1
            # ... create screen_info strings and parsed_content_list dicts ...

        # 5. Calculate metadata
        latency = time.time() - start_time
        width, height = image.size
        metadata = ParserMetadata(...)

        # 6. Create and return ParseResult
        return ParseResult(
            elements=elements,
            annotated_image_base64=annotated_image_base64,
            screen_info=screen_info,
            parsed_content_list=parsed_content_list,
            metadata=metadata,
        )

```

**2. Using the Parser in the Agent (`libs/agent/agent/providers/omni/parser.py`)**

This shows how the agent's `OmniParser` wrapper class uses the SOM library.

```python
# Simplified from libs/agent/agent/providers/omni/parser.py
from som import OmniParser as OmniDetectParser # The SOM library parser
from som.models import ParseResult # The result structure from SOM

class OmniParser: # This is the agent's wrapper, not the SOM library one
    _shared_parser = None # Cache the SOM parser instance

    def __init__(self, force_device: Optional[str] = None):
        # Initialize or reuse the cached SOM library parser
        if OmniParser._shared_parser is None:
            # Create instance of the actual SOM parser from the library
            self.detect_parser = OmniDetectParser(force_device=device)
            # Preload its models if needed
            # ... (detector.load_model()) ...
            OmniParser._shared_parser = self.detect_parser
        else:
            self.detect_parser = OmniParser._shared_parser

    async def parse_screen(self, computer: Any) -> ParseResult:
        """Parse a screenshot using the SOM library."""
        try:
            # Get screenshot from the computer interface
            screenshot = await computer.interface.screenshot()
            # ... (handle if screenshot is base64 string) ...

            # Call the SOM library's parse method
            parse_result: ParseResult = self.detect_parser.parse(
                screenshot_data=screenshot,
                box_threshold=0.3,
                iou_threshold=0.1,
                use_ocr=True
            )
            logger.info(f"Screenshot parsed successfully by SOM")
            return parse_result
        except Exception as e:
            logger.error(f"Error parsing screen using SOM: {str(e)}")
            # Return a minimal error result
            return ParseResult(...) # Minimal error ParseResult
```

This illustrates how the agent framework incorporates and uses the SOM library to get structured screen information.

## Conclusion

You've now learned about **SOM (OmniParser)**, the advanced vision system for the `cua` agent.

- It acts like specialized glasses, analyzing screenshots to identify UI elements (icons, buttons) and text.
- It uses AI models like YOLO and OCR.
- It outputs structured data: a list of elements with bounding boxes, types, text content, and unique IDs, plus an annotated image.
- This structured data is crucial for `OmniLoop`-based agents, allowing the AI model to understand the screen layout and refer to elements precisely (e.g., "Click Box #5").
- It's typically used internally by the `OmniLoop`, processing screenshots during the "Observe" phase.

SOM helps the agent _understand_ a single computer screen. But `cua` is designed to potentially manage _multiple_ agents or components interacting with different virtual computers. How is this coordination managed at a higher level? That's where the **MCP Server** comes in.

Ready to learn about the central coordinator? Let's move on to [Chapter 9: MCP Server](09_mcp_server_.md)!

---

Generated by [AI Codebase Knowledge Builder](https://github.com/The-Pocket/Tutorial-Codebase-Knowledge)
