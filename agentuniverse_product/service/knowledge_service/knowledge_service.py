# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/8/6 15:39
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: knowledge_service.py
import os
import shutil

from typing import List

from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse_product.base.product import Product
from agentuniverse_product.base.product_manager import ProductManager
from agentuniverse_product.service.model.knowledge_dto import KnowledgeDTO
from agentuniverse.agent.action.knowledge.knowledge_manager import KnowledgeManager
from agentuniverse.agent.action.knowledge.knowledge import Knowledge
from agentuniverse_product.base.util.yaml_util import (
    write_yaml_file,
    delete_yaml_file,
    update_nested_yaml_value,
    read_yaml_file,
)
from agentuniverse_product.service.util.common_util import get_core_path, get_resources_path
from agentuniverse_product.service.util.knowledge_util import (
    register_knowledge,
    unregister_knowledge,
    register_store,
    assemble_knowledge_product_config_data,
    assemble_knowledge_config,
)
from agentuniverse_product.service.util.agent_util import register_product, unregister_product


class KnowledgeService:
    """Knowledge Service for aU-product."""

    @staticmethod
    def get_knowledge_list() -> List[KnowledgeDTO]:
        """Get all knowledge."""
        res = []
        product_list: List[Product] = ProductManager().get_instance_obj_list()
        if len(product_list) < 1:
            return res
        for product in product_list:
            if product.type == ComponentEnum.KNOWLEDGE.value:
                knowledge_dto = KnowledgeDTO(nickname=product.nickname, id=product.id)
                knowledge = product.instance
                knowledge_dto.description = knowledge.description
                res.append(knowledge_dto)
        return res

    @staticmethod
    def create_knowledge(knowledge_dto: KnowledgeDTO) -> str:
        """ Create knowledge with name and desc, then return knowledge ID.

        Args:
            knowledge_dto(KnowledgeDTO): The knowledge DTO containing the knowledge attributes.

        Returns:
            str: The ID of the created knowledge.
        """
        # write product YAML file
        knowledge_id = knowledge_dto.id

        product_file_name = f"{knowledge_id}_product"

        path = get_core_path()
        product_file_path = path / 'product' / 'knowledge' / f"{product_file_name}.yaml" if path\
            else os.path.join("..", "..", "platform", "difizen", "product", "knowledge", f"{product_file_name}.yaml")

        product_config_data = assemble_knowledge_product_config_data(knowledge_dto)

        try:
            write_yaml_file(str(product_file_path), product_config_data)
        except Exception as e:
            raise e

        knowledge_file_path = path / 'knowledge' / f"{knowledge_id}.yaml" if path\
            else os.path.join("..", "..", "intelligence", "agentic", "knowledge", f"{knowledge_id}.yaml")

        knowledge_config = assemble_knowledge_config(knowledge_dto)

        try:
            write_yaml_file(str(knowledge_file_path), knowledge_config)
        except Exception as e:
            raise e

        register_knowledge(str(knowledge_file_path))
        register_product(str(product_file_path))

        return knowledge_id

    @staticmethod
    def update_knowledge(knowledge_dto: KnowledgeDTO) -> str:
        """Update knowledge attributes.

        Args:
            knowledge_dto (KnowledgeDTO): The knowledge DTO containing the knowledge attributes.

        Returns:
            str: The ID of the updated knowledge.
        """

        if knowledge_dto.id is None:
            raise ValueError("knowledge_id is None.")

        knowledge: Knowledge = KnowledgeManager().get_instance_obj(component_instance_name=knowledge_dto.id)
        if knowledge is None:
            raise ValueError("The knowledge instance corresponding to the knowledge_id cannot be found.")

        product: Product = ProductManager().get_instance_obj(component_instance_name=knowledge_dto.id)
        if product is None:
            raise ValueError("The knowledge product instance corresponding to the knowledge_id cannot be found.")

        knowledge_update_config = {"description": knowledge_dto.description}
        product_update_config = {"nickname": knowledge_dto.nickname}
        # Update the knowledge attributes if they are provided
        knowledge_updated_fields = {key: value for key, value in knowledge_update_config.items() if value is not None}
        product_updated_fields = {key: value for key, value in product_update_config.items() if value is not None}

        # set knowledge attributes
        for key, value in knowledge_updated_fields.items():
            setattr(knowledge, key, value)
        for key, value in product_updated_fields.items():
            setattr(product, key, value)

        update_nested_yaml_value(knowledge.component_config_path, knowledge_updated_fields)
        update_nested_yaml_value(product.component_config_path, product_updated_fields)

        return knowledge_dto.id

    @staticmethod
    def delete_knowledge(knowledge_id: str) -> bool:
        """Delete knowledge, then return the result.

        Args:
            knowledge_id (str): The ID of the knowledge to be deleted.

        Returns:
            bool: True if the knowledge is deleted successfully, False otherwise.
        """

        knowledge: Knowledge = KnowledgeManager().get_instance_obj(component_instance_name=knowledge_id)
        if knowledge is None:
            raise ValueError("The knowledge instance corresponding to the knowledge_id cannot be found.")

        product: Product = ProductManager().get_instance_obj(component_instance_name=knowledge_id)
        if product is None:
            raise ValueError("The knowledge product instance corresponding to the knowledge_id cannot be found.")

        knowledge_file_path = knowledge.component_config_path
        product_file_path = product.component_config_path

        try:
            unregister_knowledge(knowledge_file_path)
            unregister_product(product_file_path)
            delete_yaml_file(knowledge_file_path)
            delete_yaml_file(product_file_path)
            return True
        except Exception as e:
            raise e

    @staticmethod
    def upload_knowledge_file(knowledge_id: str, file) -> bool:
        """Upload the knowledge file.

        Args:
            knowledge_id (str): The ID of the knowledge.
            file: The file to be uploaded.

        Returns:
            bool: True if the file is uploaded successfully, False otherwise.
        """
        path = get_core_path()

        upload_file_path = get_resources_path()

        try:
            if not os.path.exists(upload_file_path):
                os.makedirs(upload_file_path, exist_ok=True)

            file_location = os.path.join(upload_file_path, file.filename)

            with open(file_location, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

        except Exception as e:
            print(f"upload file failed: {e}")
            raise e

        knowledge_store_file_path = path / 'store' / f"{knowledge_id}_store.yaml" if path\
            else str(os.path.join("..", "..", "intelligence",
                                  "agentic", "knowledge", "store", f"{knowledge_id}_store.yaml"))
        knowledge_store_name = f"{knowledge_id}_chroma_store"

        knowledge = KnowledgeManager().get_instance_obj(component_instance_name=knowledge_id)

        try:
            # If the store YAML file does not exist, create and register the store, and update the knowledge YAML.
            if not os.path.isfile(knowledge_store_file_path):
                knowledge_store_config = {
                    "name": knowledge_store_name,
                    "description": knowledge_store_name,
                    "persist_path": f"../../intelligence/db/{knowledge_store_name}.db",
                    "metadata": {
                        "type": "STORE",
                        "module": "agentuniverse.agent.action.knowledge.store.chroma_store",
                        "class": "ChromaStore",
                    },
                }
                write_yaml_file(str(knowledge_store_file_path), knowledge_store_config)
                register_store(str(knowledge_store_file_path))

                knowledge_path = knowledge.component_config_path

                knowledge_config = read_yaml_file(knowledge_path)
                knowledge_store = knowledge_config.get("stores", [])

                update_nested_yaml_value(
                    knowledge.component_config_path, {"stores": [*knowledge_store, knowledge_store_name]}
                )

        except Exception as e:
            raise e
        stores = knowledge.stores
        stores.append(knowledge_store_name)
        knowledge.insert_knowledge(source_path=file_location, stores=[knowledge_store_name])

        return True
