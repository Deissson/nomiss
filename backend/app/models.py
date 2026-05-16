from sqlalchemy import Column, Integer, String, BigInteger
from .database import Base

class SubjectModel(Base):
    __tablename__ = "subjects"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    totalHours = Column(Integer)
    skipped = Column(Integer, default=0)
    last_skipped = Column(BigInteger, nullable=True)
