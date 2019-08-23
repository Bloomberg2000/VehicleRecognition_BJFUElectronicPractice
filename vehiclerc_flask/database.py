from sqlalchemy import create_engine, Boolean, Time, Column, Integer, String
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine('mysql+pymysql://root:root@127.0.0.1:3306/vehiclerc', max_overflow=5)
db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()


# 初始化数据库
def init_db():
    import models
    Base.metadata.create_all(bind=engine)
