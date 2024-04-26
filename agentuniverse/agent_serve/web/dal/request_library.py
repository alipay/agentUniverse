# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/3/26 15:18
# @Author  : fanen.lhy
# @Email   : fanen.lhy@antgroup.com
# @FileName: request_library.py

import datetime
import json

from sqlalchemy import JSON, Integer, String, DateTime, Text, Column
from sqlalchemy import create_engine
from sqlalchemy import select
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from .entity.request_do import RequestDO
from agentuniverse.base.util.system_util import get_project_root_path
from agentuniverse.base.config.configer import Configer
from agentuniverse.base.annotation.singleton import singleton

REQUEST_TABLE_NAME = 'request_task'
Base = declarative_base()


class RequestORM(Base):
    """SQLAlchemy ORM Model for RequestDO."""
    __tablename__ = REQUEST_TABLE_NAME
    id = Column(Integer, primary_key=True, autoincrement=True)
    request_id = Column(String(20), nullable=False)
    query = Column(Text)
    session_id = Column(String(50))
    state = Column(String(20))
    result = Column(JSON)
    steps = Column(JSON)
    additional_args = Column(JSON)
    gmt_create = Column(DateTime, default=datetime.datetime.now)
    gmt_modified = Column(DateTime, default=datetime.datetime.now,
                          onupdate=datetime.datetime.now)


@singleton
class RequestLibrary:
    def __init__(self, configer: Configer = None):
        """Init the database connection. Use uri in config file or use sqlite
        as default database."""
        mysql_uri = None
        if Configer:
            mysql_uri = configer.get('DB', {}).get('mysql_uri')
        if mysql_uri and mysql_uri.strip():
            db_uri = mysql_uri
        else:
            db_path = get_project_root_path() / 'DB' / 'agent_framework.db'
            db_path.parent.mkdir(parents=True, exist_ok=True)
            db_uri = f'sqlite:////{db_path}'

        self.db_uri = db_uri
        self.Session = None

    def query_request_by_request_id(self, request_id: str) -> RequestDO | None:
        """Get a RequestDO with given request_id.

        Args:
            request_id(`str`): The unique request id of request task.

        Return:
            The target RequestDO or none when no such data.
        """
        session = self.__get_session()
        try:
            result = session.execute(
                select(RequestORM).where(RequestORM.request_id == request_id)
            ).scalars().first()
            if not result:
                return None
            return self.__request_orm_to_do(result)
        finally:
            session.close()

    def add_request(self, request_do: RequestDO) -> int:
        """Add the given RequestDO to database.

        Args:
            request_do(`RequestDO`): A new RequestDO to be added.

        Return:
            A int stands unique data id in table.
        """
        session = self.__get_session()
        try:
            request_orm = RequestORM(**request_do.model_dump())
            session.add(request_orm)
            session.commit()
            return request_orm.id
        finally:
            session.close()

    def update_request(self, request_do: RequestDO):
        """Update the request data with same request id as the given
        RequestDO."""
        session = self.__get_session()
        try:
            db_request_do = session.query(RequestORM).filter(
                RequestORM.request_id == request_do.request_id).first()
            if db_request_do:
                update_data = request_do.model_dump(exclude_unset=True)
                for key, value in update_data.items():
                    setattr(db_request_do, key, value)
                session.commit()
                session.refresh(db_request_do)
        finally:
            session.close()

    def update_gmt_modified(self, request_id: str):
        """Update the request task latest active time."""
        session = self.__get_session()
        try:
            db_request_do = session.query(RequestORM).filter(
                RequestORM.request_id == request_id).first()
            if db_request_do:
                setattr(db_request_do, "gmt_modified", datetime.datetime.now())
                session.commit()
                session.refresh(db_request_do)
        finally:
            session.close()

    def __get_session(self):
        if self.Session:
            return self.Session()
        # Create database engine
        self.engine = create_engine(
            self.db_uri,
            json_serializer=lambda x: json.dumps(x, ensure_ascii=False)
        )
        self.Session = sessionmaker(bind=self.engine)

        with self.engine.connect() as conn:
            if not conn.dialect.has_table(conn, REQUEST_TABLE_NAME):
                Base.metadata.create_all(self.engine)
        return self.Session()

    def __request_orm_to_do(self, request_orm: RequestORM) -> RequestDO:
        """Transfer a RequestORM to RequestDO."""
        request_obj = RequestDO(
            request_id='',
            session_id="",
            query='',
            state='',
            result=dict(),
            steps=[],
            additional_args=dict(),
            gmt_create=datetime.datetime.now(),
            gmt_modified=datetime.datetime.now(),
        )
        for column in request_orm.__table__.columns:
            setattr(request_obj, column.name,
                    getattr(request_orm, column.name))
        return request_obj
