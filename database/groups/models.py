from sqlalchemy import Column, Integer, Text
from ..connect import Base
from ..constants import DEFAULT_AUCTIONS_TEMPLATE


class Group(Base):
    __tablename__ = "groups"

    id = Column(Integer, primary_key=True, autoincrement=True)
    group_id = Column(Integer, unique=True, nullable=False)
    name = Column(Text, nullable=False)
    posts_amount = Column(Integer, nullable=False, default=0)
    waterfalls = Column(Text, nullable=True)  # comma-separated list of group IDs
    commission_percent = Column(Integer, default=0)
    commission_min = Column(Integer, default=0)
    auctions_template = Column(Text, nullable=True, default=DEFAULT_AUCTIONS_TEMPLATE)
