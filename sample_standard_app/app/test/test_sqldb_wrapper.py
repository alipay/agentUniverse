# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/5/24 01:23
# @Author  : fanen.lhy
# @Email   : fanen.lhy@antgroup.com
# @FileName: test_sqldb_wrapper.py
import unittest

from agentuniverse.base.agentuniverse import AgentUniverse
from agentuniverse.database.sqldb_wrapper_manager import \
            SQLDBWrapperManager

class SQLDBWrapperTest(unittest.TestCase):
    """
    Test cases for the SQLDBWrapper
    """

    def setUp(self) -> None:
        AgentUniverse().start(config_path='../../config/config.toml')


    def test_sqldb_wrapper(self):
        manager: SQLDBWrapperManager = SQLDBWrapperManager()
        demo_sqldb_wrapper = manager.get_instance_obj("demo_sqldb_wrapper")
        insert_statement = """
                INSERT INTO users (name, age)
                VALUES
                    ('Alice', 30),
                    ('Bob', 25);
                """
        demo_sqldb_wrapper.run("DROP TABLE IF EXISTS users")
        demo_sqldb_wrapper.run(
            "CREATE TABLE IF NOT EXISTS users ( id INTEGER PRIMARY KEY, name TEXT NOT NULL, age INTEGER)"
        )
        demo_sqldb_wrapper.run(insert_statement)
        result = demo_sqldb_wrapper.run("select * from users")
        demo_sqldb_wrapper.run("select * from users")
        assert len(result) == 2


if __name__ == '__main__':
    unittest.main()