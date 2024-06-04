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

doc_list_map = {
    '1_1_Introduction.md': 'Introduction',
    '1_2_Installation.md': 'Installation',
    '1_3_Quick_Start.md': 'Quick Start',
    '1_4_Application_Engineering_Structure_Explanation.md': 'Application Structure Explanation',
    '2_2_Domain_Component_Principles.md': 'Domain Component Principles',
    '2_2_1_Agent.md': 'Agent',
    '2_2_1_Agent_Create_And_Use.md': 'Agent Create And Use',
    '2_2_1_Agent_Related_Domain_Objects.md': 'Agent Related Domain Objects',
    '2_2_2_LLM.md': 'LLM',
    '2_2_2_LLM_component_define_and_usage.md': 'LLM Define And Use',
    '2_2_2_LLM_Related_Domain_Objects.md': 'LLM Related Domain Objects',
    '2_2_3_Tool.md': 'Tool',
    '2_2_3_Tool_Create_And_Use.md': 'Tool Create And Use',
    '2_2_3_Tool_Related_Domain_Objects.md': 'Tool Related Domain Objects',
    '2_4_1_Service_Registration_and_Usage.md': 'Service Registration And Use',
    '2_4_1_Service_Information_Storage.md': 'Service Information Storage',
    '2_4_1_Web_Server.md': 'Web_Server',
    '2_4_1_Web_Api.md': 'Web Api',
    '2_6_Logging_Utils.md': 'Logging Utils',
    '2_7_Framework_Context.md': 'Framework Context',
    '3_1_2_0_List_Of_LLMs.md': 'List Of LLMs',
    '3_1_2_BaiChuan_LLM_Use.md': 'BaiChuan LLM Use',
    '3_1_2_Kimi_LLM_Use.md': 'Kimi LLM Use',
    '3_1_2_OpenAI_LLM_Use.md': 'OpenAI LLM Use',
    '3_1_2_Qwen_LLM_Use.md': 'Qwen LLM Use',
    '3_1_2_WenXin_LLM_Use.md': 'WenXin LLM Use',
    '3_2_1_gRPC.md': 'gRPC',
    '3_2_4_Alibaba_Cloud_SLS.md': 'Alibaba Cloud SLS',
    '5_1_1_Docker_Container_Deployment.md': 'Docker Container Deployment',
    '5_1_2_K8S_Deployment.md': 'K8S Deployment',
    '6_1_Contact_Us.md': 'Contact Us',
}

doc_number_map = {
    '1.1': '1_1_Introduction.md',
    '1.2': '1_2_Installation.md',
    '1.3': '1_3_Quick_Start.md',
    '1.4': '1_4_Application_Engineering_Structure_Explanation.md',
    '2.2': '2_2_Domain_Component_Principles.md',
    '2.2.1': '2_2_1_Agent.md',
    '2.2.1.1': '2_2_1_Agent_Create_And_Use.md',
    '2.2.1.2': '2_2_1_Agent_Related_Domain_Objects.md',
    '2.2.2': '2_2_2_LLM.md',
    '2.2.2.1': '2_2_2_LLM_component_define_and_usage.md',
    '2.2.2.2': '2_2_2_LLM_Related_Domain_Objects.md',
    '2.2.3': '2_2_3_Tool.md',
    '2.2.3.1': '2_2_3_Tool_Create_And_Use.md',
    '2.2.3.2': '2_2_3_Tool_Related_Domain_Objects.md',
    '2.4.1': '2_4_1_Service_Registration_and_Usage.md',
    '2.4.2': '2_4_1_Service_Information_Storage.md',
    '2.4.3': '2_4_1_Web_Server.md',
    '2.4.4': '2_4_1_Web_Api.md',
    '2.6': '2_6_Logging_Utils.md',
    '2.7': '2_7_Framework_Context.md',
    '3.1.2': '3_1_2_0_List_Of_LLMs.md',
    '3.1.2.1': '3_1_2_BaiChuan_LLM_Use.md',
    '3.1.2.2': '3_1_2_Kimi_LLM_Use.md',
    '3.1.2.3': '3_1_2_OpenAI_LLM_Use.md',
    '3.1.2.4': '3_1_2_Qwen_LLM_Use.md',
    '3.1.2.5': '3_1_2_WenXin_LLM_Use.md',
    '3.2.1': '3_2_1_gRPC.md',
    '3.2.4': '3_2_4_Alibaba_Cloud_SLS.md',
    '5.1.1': '5_1_1_Docker_Container_Deployment.md',
    '5.1.2': '5_1_2_K8S_Deployment.md',
    '6.1': '6_1_Contact_Us.md',
}

for number in sorted(doc_number_map.keys()):
    file_name = doc_number_map.get(number)
    content_value = doc_list_map.get(file_name)
    with mkdocs_gen_files.open(f"{TUTORIAL}/{content_value}.md", "w") as nav_file:
        with open(f'docs/guidebook/en/{file_name}', 'r', encoding='utf-8') as file:
            nav_file.writelines(f'{number} {content_value} \n\n')
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
