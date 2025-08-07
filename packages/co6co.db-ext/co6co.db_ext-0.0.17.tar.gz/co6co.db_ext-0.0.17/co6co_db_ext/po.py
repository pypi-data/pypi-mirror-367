from __future__ import annotations
from sqlalchemy import func, MetaData, INTEGER, Column, ForeignKey, String, BigInteger, DateTime
from sqlalchemy.orm import DeclarativeBase, declarative_base, relationship, QueryPropertyDescriptor, Query
from co6co.utils.tool_util import to_camelcase
from datetime import datetime
from typing import Optional
# 与属性库实体相关，所有实体集成 BasePO类

metadata = MetaData()
# class BasePO(declarative_base(metadata=metadata)):


class BasePO(DeclarativeBase):
    __abstract__ = True

    @property
    def query() -> Query:
        return None

    def to_dict(self):
        return dict(filter(lambda k: k[0] != "_sa_instance_state", self.__dict__.items()))
        # return {to_camelcase(c.name): getattr(self, c.name, None) for c in self.__table__.columns}

    def to_dict2(self):
        return {to_camelcase(c.name): getattr(self, to_camelcase(c.name), None) for c in self.__table__.columns}
    @property
    def sqlItem(self):
        """
        1. 完整的sql语句
        Insert(xxPo).values(**self.sqlItem)
        2. sql与参数分开
        sql=Update(xxPO).where(xxPO.id == id) 
        db_tools.execSQL(session, sql, sql.sqlItem)
        """
        return {k: v for k, v in self.__dict__.items() if not k.startswith('_')} 
    
    def update(self, po: DeclarativeBase):
        pass

    def add_assignment(self,  userId: Optional[int] = None):
        if isinstance(self, UserTimeStampedModelPO):
            self.createTime = datetime.now()
            self.createUser = userId
        elif isinstance(self, TimeStampedModelPO):
            self.createTime = datetime.now()

    def edit_assignment(self,   userId: Optional[int] = None):
        if isinstance(self, UserTimeStampedModelPO):
            self.updateTime = datetime.now()
            self.updateUser = userId
        elif isinstance(self, TimeStampedModelPO):
            self.updateTime = datetime.now()


class TimeStampedModelPO(BasePO):
    __abstract__ = True

    createTime = Column("create_time", DateTime, server_default=func.now(), comment="创建时间")
    updateTime = Column("update_time", DateTime, comment="更新时间")


class CreateUserStampedModelPO(BasePO):
    __abstract__ = True
    createUser = Column("create_user", BigInteger, comment="创建人")
    createTime = Column("create_time", DateTime, server_default=func.now(), comment="创建时间")


class UserTimeStampedModelPO(TimeStampedModelPO):
    __abstract__ = True

    createUser = Column("create_user", BigInteger, comment="创建人")
    updateUser = Column("update_user", BigInteger, comment="修改人")
