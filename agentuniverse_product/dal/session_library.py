# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/7/25 19:34
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: session_library.py
import datetime
from typing import Any

from sqlalchemy import JSON, Integer, String, DateTime, Column, Index
from sqlalchemy.orm import declarative_base, sessionmaker

from agentuniverse.base.annotation.singleton import singleton
from agentuniverse.database.sqldb_wrapper_manager import SQLDBWrapperManager
from agentuniverse_product.dal.model.session_do import SessionDO

SESSION_TABLE_NAME = 'session'
Base = declarative_base()


class SessionORM(Base):
    """Sqlalchemy orm Model for session table."""
    __tablename__ = SESSION_TABLE_NAME
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(50), nullable=False)
    agent_id = Column(String(50), nullable=False)
    ext_info = Column(JSON)
    gmt_created = Column(DateTime, default=datetime.datetime.now)
    gmt_modified = Column(DateTime, default=datetime.datetime.now,
                          onupdate=datetime.datetime.now)
    __table_args__ = (
        Index('session_ix_session_id', 'session_id'),
        Index('session_ix_agent_id', 'agent_id'),
    )


@singleton
class SessionLibrary:

    @staticmethod
    def get_db_session():
        system_sqldb_wrapper = SQLDBWrapperManager().get_instance_obj('__system_db__')
        return system_sqldb_wrapper.get_session()

    def add_session(self, session_do: SessionDO) -> str:
        with self.get_db_session() as db_session:
            session_orm = SessionORM(**session_do.model_dump())
            db_session.add(session_orm)
            db_session.commit()
            return session_orm.session_id

    def delete_session(self, session_id: str) -> str | None:
        with self.get_db_session() as db_session:
            session_orm = db_session.query(SessionORM).filter(
                SessionORM.session_id == session_id).one_or_none()
            if session_orm:
                db_session.delete(session_orm)
                db_session.commit()
                return session_orm.session_id
            else:
                return None

    def get_session_list(self, agent_id: str) -> list[SessionDO]:
        with self.get_db_session() as db_session:
            session_orm_list = db_session.query(SessionORM).filter(
                SessionORM.agent_id == agent_id)
            res = []
            if session_orm_list:
                for session_orm in session_orm_list:
                    res.append(self.__session_orm_to_do(session_orm))
            return res

    def get_session_detail(self, session_id: str) -> SessionDO | None:
        with self.get_db_session() as db_session:
            session_orm = db_session.query(SessionORM).filter(
                SessionORM.session_id == session_id).first()
            if session_orm:
                return self.__session_orm_to_do(session_orm)
            else:
                return None

    @staticmethod
    def __session_orm_to_do(session_orm: SessionORM) -> SessionDO:
        session_do = SessionDO(
            session_id="",
            agent_id='',
            ext_info=dict(),
        )
        for column in session_orm.__table__.columns:
            setattr(session_do, column.name,
                    getattr(session_orm, column.name))
        return session_do
