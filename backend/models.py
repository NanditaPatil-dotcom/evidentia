from sqlalchemy import Column, Integer, String, Text
from database import Base

class Record(Base):
    __tablename__ = "records"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)

    transcript = Column(Text)
    events = Column(Text)
    entities = Column(Text)
    laws = Column(Text)
    statements = Column(Text)

    timestamp = Column(String)
    location = Column(Text)

    encrypted_audio_path = Column(String)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True)
    password = Column(String)