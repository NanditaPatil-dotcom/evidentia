from sqlalchemy import Column, Integer, String, Text

try:
    from backend.database import Base
except ModuleNotFoundError:
    from database import Base

class Record(Base):
    __tablename__ = "records"

    id = Column(Integer, primary_key=True, index=True)

    regional_text = Column(Text)
    english_text = Column(Text)
    events = Column(Text)
    entities = Column(Text)
    laws = Column(Text)
    statements = Column(Text)

    logged_at = Column(String)
    coordinates = Column(Text)

    encrypted_audio_path = Column(String)
