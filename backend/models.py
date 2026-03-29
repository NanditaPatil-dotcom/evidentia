from sqlalchemy import Column, Integer, String

try:
    from backend.database import Base
except ModuleNotFoundError:
    from database import Base


class Record(Base):
    __tablename__ = "records"

    id = Column(Integer, primary_key=True, index=True)
    record_hash = Column(String, index=True, nullable=False)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String)
    dob = Column(String)
    phone = Column(String)
    email = Column(String, nullable=True)

    location_permission = Column(String)
    password = Column(String, nullable=True)
