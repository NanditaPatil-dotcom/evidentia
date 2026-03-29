import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from backend.database import Base
from core.encryption import encrypt_field, decrypt_field
from sqlalchemy import Column, Integer, String, Text


class Record(Base):
    __tablename__ = "records"

    id = Column(Integer, primary_key=True, index=True)

    # ── Private columns (store encrypted blobs in DB) ──────────────────────
    # Column name in DB stays the same (first arg to Column).
    # Python attribute name has underscore prefix.

    _regional_text    = Column("regional_text",    Text)
    _english_text     = Column("english_text",     Text)
    _events           = Column("events",           Text)
    _entities         = Column("entities",         Text)
    _laws             = Column("laws",             Text)
    _statements       = Column("statements",       Text)
    _accused_details  = Column("accused_details",  Text)
    _coordinates      = Column("coordinates",      Text)

    # These two are less sensitive / already protected elsewhere
    # logged_at is a timestamp string — still encrypt for safety
    _logged_at        = Column("logged_at",        String)

    # Audio path just points to an already-encrypted file on disk
    # Encrypting the path itself prevents leaking filenames
    _encrypted_audio_path = Column("encrypted_audio_path", String)

    # ── Public properties (transparent encrypt/decrypt) ────────────────────

    @property
    def regional_text(self):
        return decrypt_field(self._regional_text)

    @regional_text.setter
    def regional_text(self, value):
        self._regional_text = encrypt_field(value)

    # ──────────────────────────────────────────────────────────────────────

    @property
    def english_text(self):
        return decrypt_field(self._english_text)

    @english_text.setter
    def english_text(self, value):
        self._english_text = encrypt_field(value)

    # ──────────────────────────────────────────────────────────────────────
    # events / entities / laws / statements / accused_details / coordinates
    # are stored as JSON strings — we encrypt the whole JSON string.
    # The route is still responsible for json.dumps before setting,
    # and json.loads after getting (same as before).

    @property
    def events(self):
        return decrypt_field(self._events)

    @events.setter
    def events(self, value):
        self._events = encrypt_field(value)

    # ──────────────────────────────────────────────────────────────────────

    @property
    def entities(self):
        return decrypt_field(self._entities)

    @entities.setter
    def entities(self, value):
        self._entities = encrypt_field(value)

    # ──────────────────────────────────────────────────────────────────────

    @property
    def laws(self):
        return decrypt_field(self._laws)

    @laws.setter
    def laws(self, value):
        self._laws = encrypt_field(value)

    # ──────────────────────────────────────────────────────────────────────

    @property
    def statements(self):
        return decrypt_field(self._statements)

    @statements.setter
    def statements(self, value):
        self._statements = encrypt_field(value)

    # ──────────────────────────────────────────────────────────────────────

    @property
    def accused_details(self):
        return decrypt_field(self._accused_details)

    @accused_details.setter
    def accused_details(self, value):
        self._accused_details = encrypt_field(value)

    # ──────────────────────────────────────────────────────────────────────

    @property
    def coordinates(self):
        return decrypt_field(self._coordinates)

    @coordinates.setter
    def coordinates(self, value):
        self._coordinates = encrypt_field(value)

    # ──────────────────────────────────────────────────────────────────────

    @property
    def logged_at(self):
        return decrypt_field(self._logged_at)

    @logged_at.setter
    def logged_at(self, value):
        self._logged_at = encrypt_field(value)

    # ──────────────────────────────────────────────────────────────────────

    @property
    def encrypted_audio_path(self):
        return decrypt_field(self._encrypted_audio_path)

    @encrypted_audio_path.setter
    def encrypted_audio_path(self, value):
        self._encrypted_audio_path = encrypt_field(value)


# ── User model (unchanged — password is already hashed by bcrypt) ──────────

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    name              = Column(String)
    dob               = Column(String)
    phone             = Column(String)
    email             = Column(String, nullable=True)
    location_permission = Column(String)   # "granted" / "denied"
    password          = Column(String, nullable=True)  # bcrypt hash