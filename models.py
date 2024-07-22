from datetime import datetime
from sqlalchemy import Column, Integer, BigInteger, String, Numeric, Date, Interval, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from database import Base

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False)
    username = Column(String(255))
    payments = relationship('Payment', back_populates='user')

class Payment(Base):
    __tablename__ = 'payments'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', on_delete='CASCADE'))
    title = Column(String(255), nullable=False)
    amount = Column(Numeric, nullable=False)
    payment_date = Column(Date, nullable=False)
    reminder_period = Column(Interval, nullable=False)
    notification_duration = Column(Interval, nullable=False)
    category = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    user = relationship('User', back_populates='payments')
