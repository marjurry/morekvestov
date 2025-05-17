from .database import Base
from typing import List
from sqlalchemy import Identity
from sqlalchemy import Table, Column, Integer, String, BigInteger, Text, ForeignKey, CheckConstraint, Boolean
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from passlib.context import CryptContext
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import relationship
Base = declarative_base()
from passlib.context import CryptContext

pwd_context = CryptContext(
    schemes=["pbkdf2_sha256"],
    default="pbkdf2_sha256",
    pbkdf2_sha256__default_rounds=30000
)

quest_challenge_association = Table(
    'quest_challenge_association',
    Base.metadata,
    Column('quest_id', Integer, ForeignKey('Quest.id', ondelete='CASCADE'), primary_key=True),
    Column('challenge_id', Integer, ForeignKey('Challenge.id', ondelete='CASCADE'), primary_key=True),
)
class User(Base):
    __tablename__ = 'User'
    
    phone_number = Column(BigInteger, primary_key=True)
    password_hash = Column(String(300), nullable=False)
    is_active = Column(Boolean, default=True)
    
    quests = relationship("Quest", back_populates="user", 
                         cascade="all, delete-orphan",
                         passive_updates=True)
    def set_password(self, password):
        self.password_hash = pwd_context.hash(password)
    
    def check_password(self, password):
        return pwd_context.verify(password, self.password_hash)
    
class AgeGroup(Base):
    __tablename__ = 'AgeGroup'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False, unique=True)
    min_age = Column(Integer, nullable=False)
    max_age = Column(Integer, nullable=False)
    
    challenges = relationship("Challenge", back_populates="age_group")
    quests = relationship("Quest", back_populates="age_group")

class Challenge(Base):
    __tablename__ = 'Challenge'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(100), nullable=False)
    type = Column(String(20), nullable=False)
    location_type = Column(String(20), nullable=False)
    duration_min = Column(Integer, nullable=False)
    rules = Column(Text, nullable=False)

    age_group_id = Column(Integer, ForeignKey('AgeGroup.id'))
    age_group = relationship("AgeGroup", back_populates="challenges")
    
    quests = relationship(
        "Quest",
        secondary=quest_challenge_association,
        back_populates="challenges"
    )



class Quest(Base):
    __tablename__ = 'Quest'
    
    id = Column(Integer, primary_key=True)
    total_duration = Column(Integer, nullable=False)
    location_type = Column(String(20), nullable=False)
    
    user_id = Column(BigInteger, ForeignKey('User.phone_number', onupdate= 'CASCADE'))
    age_group_id = Column(Integer, ForeignKey('AgeGroup.id'))
    
    user = relationship("User", back_populates="quests")
    age_group = relationship("AgeGroup", back_populates="quests")
    
    challenges = relationship(
        "Challenge",
        secondary=quest_challenge_association,
        back_populates="quests"
    )
'''pwd_context = CryptContext(
    schemes=["pbkdf2_sha256"],
    default="pbkdf2_sha256",
    pbkdf2_sha256__default_rounds=30000
)

class User(Base):
    __tablename__ = 'User'
    
    phone_number = Column(BigInteger, primary_key=True)
    password_hash = Column(String(255), nullable=False)
    
    quests = relationship("Quest", back_populates="user", cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = pwd_context.hash(password)
    
    def check_password(self, password):
        return pwd_context.verify(password, self.password_hash)
    quests = relationship("Quest", back_populates="User", cascade="all, delete-orphan")

class AgeGroup(Base):
    __tablename__ = 'AgeGroup'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False, unique=True)
    min_age = Column(Integer, nullable=False)
    max_age = Column(Integer, nullable=False)
    
    challenges = relationship("Challenge", back_populates="age_group")
    quests = relationship("Quest", back_populates="age_group")

quest_challenge_association = Table(
    'quest_challenge_association',
    Base.metadata,
    Column('quest_id', Integer, ForeignKey('Quest.id', ondelete='CASCADE'), primary_key=True),
    Column('challenge_id', Integer, ForeignKey('Challenge.id', ondelete='CASCADE'), primary_key=True),
)
from typing import List
from sqlalchemy import ForeignKey, Integer, String, Text, BigInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

# Ассоциативная таблица (должна быть объявлена до моделей если используете классический подход)
quest_challenge_association = Table(
    'quest_challenge_association',
    Base.metadata,
    Column('quest_id', Integer, ForeignKey('Quest.id')),
    Column('challenge_id', Integer, ForeignKey('Challenge.id'))
)

class Challenge(Base):
    __tablename__ = 'Challenge'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    type: Mapped[str] = mapped_column(String(20), nullable=False)
    location_type: Mapped[str] = mapped_column(String(20), nullable=False)
    duration_min: Mapped[int] = mapped_column(Integer, nullable=False)
    rules: Mapped[str] = mapped_column(Text, nullable=False)

    age_group_id: Mapped[int] = mapped_column(Integer, ForeignKey('AgeGroup.id'))
    age_group: Mapped["AgeGroup"] = relationship(back_populates="challenges")
    
    # Связь многие-ко-многим с Quest
    quests: Mapped[List["Quest"]] = relationship(
        secondary=quest_challenge_association,
        back_populates="challenges",
        viewonly=True
    )

class Quest(Base):
    __tablename__ = 'Quest'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    total_duration: Mapped[int] = mapped_column(Integer, nullable=False)
    location_type: Mapped[str] = mapped_column(String(20), nullable=False)
    
    # Связи
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('User.phone_number', ondelete='CASCADE'))
    age_group_id: Mapped[int] = mapped_column(Integer, ForeignKey('AgeGroup.id'))
    
    # Отношения
    user: Mapped["User"] = relationship("User", back_populates="quests")
    age_group: Mapped["AgeGroup"] = relationship(back_populates="quests")
    
    # Связь многие-ко-многим с Challenge
    challenges: Mapped[List["Challenge"]] = relationship(
        secondary=quest_challenge_association,
        back_populates="quests",
        viewonly=True
    )

# Дополнительно после всех определений классов
Challenge.quests = relationship(
    "Quest",
    secondary=quest_challenge_association,
    back_populates="challenges"
)

Quest.challenges = relationship(
    "Challenge",
    secondary=quest_challenge_association,
    back_populates="quests"
)'''
'''class Challenge(Base):
    __tablename__ = 'Challenge'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(100), nullable=False)
    type = Column(String(20), nullable=False)
    location_type = Column(String(20), nullable=False)
    duration_min = Column(Integer, nullable=False)
    rules = Column(Text, nullable=False)

    age_group_id = Column(Integer, ForeignKey('AgeGroup.id'))
    age_group = relationship("AgeGroup", back_populates="challenges")
    
    # Связь многие-ко-многим с Quest
    quests = relationship("Quest", 
                         secondary=quest_challenge_association, 
                         back_populates="challenges")'''

'''class Quest(Base):
    __tablename__ = 'Quest'
    
    id = Column(Integer, primary_key=True)
    total_duration = Column(Integer, nullable=False)
    location_type = Column(String(20), nullable=False)
    
    # Связи
    user_id = Column(BigInteger, ForeignKey('User.phone_number', ondelete='CASCADE'))
    age_group_id = Column(Integer, ForeignKey('AgeGroup.id'))
    
    # Отношения
    user = relationship("User", back_populates="quests")
    age_group = relationship("AgeGroup", back_populates="quests")
    
    # Связь многие-ко-многим с Challenge
    challenges = relationship("Challenge", 
                            secondary=quest_challenge_association, 
                            back_populates="quests")'''