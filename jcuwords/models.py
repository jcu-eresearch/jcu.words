import datetime
from sqlalchemy import (
    Column,
    Integer,
    Text,
    DateTime,
    )

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    )

from zope.sqlalchemy import ZopeTransactionExtension

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()

class Keyword(Base):
    __tablename__ = 'keywords'
    id = Column(Integer, primary_key=True)
    keyword = Column(Text)
    entered_on = Column(DateTime, default=datetime.datetime.utcnow())
    user_id = Column(Text)
    
    def __init__(self, keyword, user_id):
        self.keyword = keyword
        self.user_id = user_id


