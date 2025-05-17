from typing import List, Optional
from pydantic import BaseModel
from sqlalchemy import Boolean
from typing import Optional, Union

# User schemas
class UserBase(BaseModel):
    phone_number: int
    is_active: bool = True

class UserCreate(UserBase):
    password: str

class User(UserBase):
   

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    phone_number: str | None = None

    
# AgeGroup schemas
class AgeGroupBase(BaseModel):
    name: str
    min_age: int
    max_age: int

class AgeGroupCreate(AgeGroupBase):
    pass

class AgeGroup(AgeGroupBase):
    id: int
    
    class Config:
        orm_mode = True

# Challenge schemas
class ChallengeBase(BaseModel):
    title: str
    type: str
    location_type: str
    duration_min: int
    age_group_id: int
    rules: str

class ChallengeCreate(ChallengeBase):
    id: int
    pass

class Challenge(ChallengeBase):
    id: int
    
    class Config:
        orm_mode = True

class ChallengeWithAgeGroup(BaseModel):
    title: str
    age_group_name: str
    type: str
    location_type: str
    duration_min: int
    rules: str
    
    class Config:
        orm_mode = True

# Quest schemas
class QuestBase(BaseModel):
    user_id: int
    total_duration: int
    location_type: str
    age_group_id: int

class QuestCreate(QuestBase):
    id: int  # Добавляем явное требование ID
    challenge_ids: Optional[List[int]] = None

class Quest(QuestBase):
    id: int
    challenges: List[Challenge] = []
    
    class Config:
        orm_mode = True

# Association schemas
class QuestChallengeLink(BaseModel):
    quest_id: int
    challenge_id: int

class UserUpdate(BaseModel):
    phone_number: Optional[int] = None
    password: Optional[str] = None

class AgeGroupUpdate(BaseModel):
    name: Optional[str] = None
    min_age: Optional[int] = None
    max_age: Optional[int] = None

class ChallengeUpdate(BaseModel):
    title: Optional[str] = None
    type: Optional[str] = None
    location_type: Optional[str] = None
    duration_min: Optional[int] = None
    age_group_id: Optional[int] = None
    rules: Optional[str] = None

class QuestUpdate(BaseModel):
    user_id: Optional[int] = None
    total_duration: Optional[int] = None
    location_type: Optional[str] = None
    age_group_id: Optional[int] = None
    challenge_ids: Optional[List[int]] = None