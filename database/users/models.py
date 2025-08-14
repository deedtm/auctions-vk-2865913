from sqlalchemy import Column, Integer, Text

from enums.rating import get_name

from ..connect import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False)
    nickname = Column(Text, nullable=True)
    first_name = Column(Text, nullable=True)
    last_name = Column(Text, nullable=True)
    register_date = Column(Text, nullable=True)
    access_level = Column(Integer, default=1, nullable=False)
    balance = Column(Integer, default=0, nullable=False)
    loyal = Column(Integer, default=0, nullable=False)
    rating = Column(Integer, default=0, nullable=False)

    @property
    def full_name(self):
        return f"{self.first_name or ''} {self.last_name or ''}".strip()

    @property
    def rating_name(self):
        return get_name(self.rating)
    