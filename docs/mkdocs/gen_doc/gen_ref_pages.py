# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/5/1 14:32
# @Author  : jerry.zzw 
# @Email   : jerry.zzw@antgroup.com
# @FileName: mkdocs_gen_files.py

"""Generate the code reference pages."""

from pathlib import Path

import mkdocs_gen_files

nav = mkdocs_gen_files.Nav()

package_list = [
    "agentuniverse",
    "agentuniverse_connector",
    "agentuniverse_extension"
]

TUTORIAL = "[1] Tutorial"
API_REFERENCE = "[2] API Reference"

with mkdocs_gen_files.open(f"{TUTORIAL}/Index.md", "w") as nav_file:
    with open('docs/guidebook/en/0_index.md', 'r', encoding='utf-8') as file:
        markdown_text = file.read()
        nav_file.writelines(markdown_text)

with mkdocs_gen_files.open(f"{TUTORIAL}/QuickStart.md", "w") as nav_file:
    with open('docs/guidebook/en/1_3_Quick_Start.md', 'r', encoding='utf-8') as file:
        markdown_text = file.read()
        nav_file.writelines(markdown_text)

with mkdocs_gen_files.open(f"{TUTORIAL}/Installation.md", "w") as nav_file:
    with open('docs/guidebook/en/1_2_Installation.md', 'r', encoding='utf-8') as file:
        markdown_text = file.read()
        nav_file.writelines(markdown_text)

with mkdocs_gen_files.open(f"{TUTORIAL}/ApplicationStructureExplanation.md", "w") as nav_file:
    with open('docs/guidebook/en/1_4_Application_Engineering_Structure_Explanation.md', 'r', encoding='utf-8') as file:
        markdown_text = file.read()
        nav_file.writelines(markdown_text)

for package_path in package_list:
    for path in sorted(Path(package_path).rglob("*.py")):
        module_path = path.relative_to("./").with_suffix("")
        doc_path = path.relative_to(package_path).with_suffix(".md")
        full_doc_path = Path(f"{API_REFERENCE}/{package_path}", doc_path)

        parts = tuple(module_path.parts)

        if parts[-1] == "__init__":  #
            # parts = parts[:-1]
            # doc_path = doc_path.with_name("index.md")
            # full_doc_path = full_doc_path.with_name("index.md")
            continue
        elif parts[-1] == "__main__":
            continue

        nav[parts] = doc_path.as_posix()

        with mkdocs_gen_files.open(full_doc_path, "w") as fd:
            identifier = ".".join(parts)
            print("::: " + identifier, file=fd)

        mkdocs_gen_files.set_edit_path(full_doc_path, Path("../../") / path)

# with mkdocs_gen_files.open(f"{API_REFERENCE}/API Content.md", "w") as nav_file:
#     nav_file.writelines(nav.build_literate_nav())


if __name__ == "__main__":
    pass
