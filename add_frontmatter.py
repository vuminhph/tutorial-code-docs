import os
from argparse import ArgumentParser

def get_files(doc_path):
    file_paths = []
    
    for root, _, files in os.walk(doc_path):
        for file in files: 
            if not file.endswith(".md"):
                continue

            file_path = os.path.join(root, file)
            file_paths.append(file_path)
    
    return file_paths

def add_frontmatter(file_path, doc_name, nav_order):
    file_name = os.path.basename(file_path)
    
    if file_name == "index.md":
        title = doc_name
        nav_order = nav_order

        frontmatter = f"""
---
layout: default
title: "{doc_name}"
nav_order: {nav_order}
has_children: true
---
"""

    else:
        with open(file_path, "r") as f:
            content = f.read()
        
        for line in content.splitlines():
            if line.startswith("# Chapter"):
                title = line.split(":")[1].strip()
                nav_order = int(line.split(":")[0].split(" ")[-1])
                break

        frontmatter = f"""
---
layout: default
title: "{title}"
parent: "{doc_name}"
nav_order: {nav_order}
---
"""

    with open(file_path, "r+") as f:
        content = f.read()
        if content.strip().startswith("---"):
            print("Front matter already exists, skipping")
            return 
        f.seek(0)
        f.write(frontmatter + "\n" + content)
        print(f"Wrote frontmatter for {file_path}")

def main():
    parser = ArgumentParser()
    parser.add_argument("--doc-name", type=str, required=True)
    parser.add_argument("--doc-path", type=str, required=True)
    parser.add_argument("--nav-order", type=int, required=True)
    args = parser.parse_args()

    doc_name = args.doc_name
    doc_path = args.doc_path
    nav_order = args.nav_order

    files = get_files(doc_path)
    for file in files:
        add_frontmatter(file, doc_name, nav_order)


if __name__ == "__main__":
    main()