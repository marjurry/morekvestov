from sqlalchemy.orm import Session
from . import models, schemas
from .models import Quest, Challenge, quest_challenge_association
from sqlalchemy import or_, and_, Boolean
from typing import List, Optional, Dict, Any
from .schemas import UserCreate
from .utils import get_password_hash
from sqlalchemy.orm import joinedload
from sqlalchemy import func

# User CRUD operations
'''def create_user(db: Session, phone_number: int, password: str) -> models.User:
    """Create a new user"""
    db_user = models.User(phone_number=phone_number)
    db_user.set_password(password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user'''

def get_user(db: Session, phone_number: int) -> Optional[models.User]:
    """Get user by phone number"""
    return db.query(models.User).filter(models.User.phone_number == phone_number).first()


def create_user(db: Session, user: UserCreate):
    password_hash = get_password_hash(user.password)
    db_user = user(phone_number=user.phone_number, password_hash =password_hash)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[models.User]:
    """Get list of users with pagination"""
    return db.query(models.User).offset(skip).limit(limit).all()

def update_user(db: Session, phone_number: int, update_data: Dict[str, Any]) -> Optional[models.User]:
    """Update user data"""
    db_user = get_user(db, phone_number)
    if db_user:
        for key, value in update_data.items():
            if key == 'password':
                db_user.set_password(value)
            else:
                setattr(db_user, key, value)
        db.commit()
        db.refresh(db_user)
    return db_user

def delete_user(db: Session, phone_number: int) -> bool:
    """Delete user by phone number"""
    db_user = get_user(db, phone_number)
    if db_user:
        db.delete(db_user)
        db.commit()
        return True
    return False

# AgeGroup CRUD operations
def create_age_group(db: Session, id: id, name: str, min_age: int, max_age: int) -> models.AgeGroup:
    """Create a new age group"""
    db_age_group = models.AgeGroup(id=id, name=name, min_age=min_age, max_age=max_age)
    db.add(db_age_group)
    db.commit()
    db.refresh(db_age_group)
    return db_age_group

def get_age_group(db: Session, age_group_id: int) -> Optional[models.AgeGroup]:
    """Get age group by ID"""
    return db.query(models.AgeGroup).filter(models.AgeGroup.id == age_group_id).first()

def get_age_groups(db: Session, skip: int = 0, limit: int = 100) -> List[models.AgeGroup]:
    """Get list of age groups with pagination"""
    return db.query(models.AgeGroup).offset(skip).limit(limit).all()

def get_age_groups_by_age(db: Session, age: int) -> List[models.AgeGroup]:
    """Get age groups suitable for specified age"""
    return db.query(models.AgeGroup).filter(
        and_(
            models.AgeGroup.min_age <= age,
            models.AgeGroup.max_age >= age
        )
    ).all()

def update_age_group(db: Session, age_group_id: int, update_data: Dict[str, Any]) -> Optional[models.AgeGroup]:
    """Update age group data"""
    db_age_group = get_age_group(db, age_group_id)
    if db_age_group:
        for key, value in update_data.items():
            setattr(db_age_group, key, value)
        db.commit()
        db.refresh(db_age_group)
    return db_age_group

def delete_age_group(db: Session, age_group_id: int) -> bool:
    """Delete age group by ID"""
    db_age_group = get_age_group(db, age_group_id)
    if db_age_group:
        db.delete(db_age_group)
        db.commit()
        return True
    return False

# Challenge CRUD operations
from typing import List, Optional, Dict, Any
from sqlalchemy import and_
from sqlalchemy.orm import Session
from app import models
from app.models import quest_challenge_association

# В файле crud.py
def create_challenge(db: Session, challenge_data: schemas.ChallengeCreate):
    max_id = db.query(func.max(models.Challenge.id)).scalar() or 0
    new_id = max_id + 1
    db_challenge = models.Challenge(
        id=new_id,
        title=challenge_data.title,
        type=challenge_data.type,
        location_type=challenge_data.location_type,
        duration_min=challenge_data.duration_min,
        age_group_id=challenge_data.age_group_id,
        rules=challenge_data.rules
    )
    db.add(db_challenge)
    db.commit()
    db.refresh(db_challenge)
    return db_challenge
# Challenge CRUD operations (updated to handle quest relationships)
'''def create_challenge(db: Session, id: int, title: str, type: str, location_type: str, 
                   duration_min: int, age_group_id: int, rules: str):
    """Create a new challenge with optional quest associations"""
    db_challenge = models.Challenge(
        id=id,
        title=title,
        type=type,
        location_type=location_type,
        duration_min=duration_min,
        age_group_id=age_group_id,
        rules=rules
    )
    db.add(db_challenge)
    db.commit()
    db.refresh(db_challenge)
    return db_challenge'''

'''def get_challenges_query_by_filters(
    db: Session,
    age_group_id: Optional[int] = None,
    challenge_type: Optional[str] = None,
    location_type: Optional[str] = None,
    min_duration: Optional[int] = None,
    max_duration: Optional[int] = None,
):
    query = db.query(models.Challenge).join(models.AgeGroup)
    
    if age_group_id is not None:
        query = query.filter(models.Challenge.age_group_id == age_group_id)
    
    if challenge_type is not None:
        query = query.filter(models.Challenge.challenge_type == challenge_type)
    
    if location_type is not None:
        query = query.filter(models.Challenge.location_type == location_type)
    
    if min_duration is not None:
        query = query.filter(models.Challenge.duration >= min_duration)
    
    if max_duration is not None:
        query = query.filter(models.Challenge.duration <= max_duration)
    
    return query
'''
def get_challenge(db: Session, challenge_id: int) -> Optional[models.Challenge]:
    """Get challenge by ID including its quest relationships"""
    return db.query(models.Challenge).filter(models.Challenge.id == challenge_id).first()

def get_challenges(db: Session, skip: int = 0, limit: int = 100) -> List[models.Challenge]:
    """Get list of challenges with pagination, including quest relationships"""
    return db.query(models.Challenge).offset(skip).limit(limit).all()

def get_challenges_by_filters(
    db: Session, 
    age_group_id: Optional[int] = None,
    type: Optional[str] = None,
    location_type: Optional[str] = None,
    min_duration: Optional[int] = None,
    max_duration: Optional[int] = None
) -> List[models.Challenge]:
    """Get challenges filtered by various criteria, including quest relationships"""
    query = db.query(models.Challenge)
    
    filters = []
    if age_group_id:
        filters.append(models.Challenge.age_group_id == age_group_id)
    if type:
        filters.append(models.Challenge.type == type)
    if location_type:
        filters.append(models.Challenge.location_type == location_type)
    if min_duration is not None:
        filters.append(models.Challenge.duration_min >= min_duration)
    if max_duration is not None:
        filters.append(models.Challenge.duration_min <= max_duration)
    
    if filters:
        query = query.filter(and_(*filters))
    
    return query.all()

def update_challenge(db: Session, challenge_id: int, update_data: Dict[str, Any]) -> Optional[models.Challenge]:
    """Update challenge data and maintain quest relationships"""
    db_challenge = get_challenge(db, challenge_id)
    if db_challenge:
        for key, value in update_data.items():
            setattr(db_challenge, key, value)
        db.commit()
        db.refresh(db_challenge)
    return db_challenge

def get_quests_by_challenge(db: Session, challenge_id: int):
    """Получает все квесты, содержащие указанное задание"""
    return db.query(models.Quest)\
        .join(models.quest_challenge_association)\
        .filter(models.quest_challenge_association.c.challenge_id == challenge_id)\
        .all()

def delete_challenge(db: Session, challenge_id: int) -> bool:
    """Delete challenge by ID, automatically handling quest associations"""
    db_challenge = get_challenge(db, challenge_id)
    if db_challenge:
        # Clear all quest associations first
        db.execute(
            quest_challenge_association.delete().where(
                quest_challenge_association.c.challenge_id == challenge_id
            )
        )
        db.delete(db_challenge)
        db.commit()
        return True
    return False

def create_quest(db: Session, user_id: int, total_duration: int, 
                location_type: str, age_group_id: int, 
                challenge_ids: Optional[List[int]] = None) -> models.Quest:
    """Create a new quest with optional challenge associations"""
    
    # Получаем максимальный текущий ID и увеличиваем на 1
    max_id = db.query(func.max(models.Quest.id)).scalar() or 0
    new_id = max_id + 1
    
    db_quest = models.Quest(
        id=new_id,
        user_id=user_id,
        total_duration=total_duration,
        location_type=location_type,
        age_group_id=age_group_id
    )
    db.add(db_quest)
    db.commit()
    
    if challenge_ids:
        for challenge_id in challenge_ids:
            add_challenge_to_quest(db, db_quest.id, challenge_id)
    
    db.refresh(db_quest)
    return db_quest
# Quest CRUD operations (updated to handle challenge relationships)
'''def create_quest(db: Session, id: int, user_id: int, total_duration: int, 
                location_type: str, age_group_id: int, 
                challenge_ids: Optional[List[int]] = None) -> models.Quest:
    """Create a new quest with optional challenge associations"""
    db_quest = models.Quest(
        id=id,
        user_id=user_id,
        total_duration=total_duration,
        location_type=location_type,
        age_group_id=age_group_id
    )
    db.add(db_quest)
    db.commit()
    
    if challenge_ids:
        for challenge_id in challenge_ids:
            add_challenge_to_quest(db, db_quest.id, challenge_id)
    
    db.refresh(db_quest)
    return db_quest'''

def get_quest(db: Session, quest_id: int) -> Optional[models.Quest]:
    """Get quest by ID including its challenge relationships"""
    return db.query(models.Quest).filter(models.Quest.id == quest_id).first()

def get_quests(db: Session, skip: int = 0, limit: int = 100) -> List[models.Quest]:
    """Get list of quests with pagination, including challenge relationships"""
    return db.query(models.Quest).offset(skip).limit(limit).all()


def get_quests_by_filters(
    db: Session,
    user_id: Optional[str] = None,
    age_group_id: Optional[int] = None,
    location_type: Optional[str] = None,
    challenge_id: Optional[int] = None,
    total_duration: Optional[int] = None
):
    query = db.query(models.Quest).options(
        joinedload(models.Quest.age_group),
        joinedload(models.Quest.user))
    
    if user_id is not None:
        query = query.filter(models.Quest.user_id == user_id)
    if age_group_id is not None:
        query = query.filter(models.Quest.age_group_id == age_group_id)
    if location_type is not None:
        query = query.filter(models.Quest.location_type == location_type)
    if total_duration is not None:
        query = query.filter(models.Quest.total_duration == total_duration)  # Точное совпадение
    
    if challenge_id is not None:
        query = query.join(models.Quest.challenges).filter(
            models.Challenge.id == challenge_id
        )
    
    return query.order_by(models.Quest.id).all()

def update_quest(db: Session, quest_id: int, update_data: Dict[str, Any]) -> Optional[models.Quest]:
    """Update quest data and maintain challenge relationships"""
    db_quest = get_quest(db, quest_id)
    if db_quest:
        for key, value in update_data.items():
            setattr(db_quest, key, value)
        db.commit()
        db.refresh(db_quest)
    return db_quest

def delete_quest(db: Session, quest_id: int) -> bool:
    """Delete quest by ID, automatically handling challenge associations"""
    db_quest = get_quest(db, quest_id)
    if db_quest:
        # Clear all challenge associations first
        db.execute(
            quest_challenge_association.delete().where(
                quest_challenge_association.c.quest_id == quest_id
            )
        )
        db.delete(db_quest)
        db.commit()
        return True
    return False

# Quest-Challenge Association operations (enhanced)
def get_quest_challenges(db: Session, quest_id: int) -> List[schemas.ChallengeWithAgeGroup]:
    """Get all challenges for a specific quest"""
    quest = db.query(models.Quest).filter(models.Quest.id == quest_id).first()
    #return quest.challenges if quest else []
    if not quest:
        return []

    return [
        schemas.ChallengeWithAgeGroup(
            **challenge.__dict__,
            age_group_name=challenge.age_group.name
        )
    for challenge in quest.challenges
    ]
    '''for challenge in quest.challenges:
        result.append({
            "title": challenge.title,
            "age_group": challenge.age_group.name  
        })
    return result'''

def get_challenge_quests(db: Session, challenge_id: int) -> List[models.Quest]:
    """Get all quests that include a specific challenge"""
    challenge = db.query(models.Challenge).filter(models.Challenge.id == challenge_id).first()
    return challenge.quests if challenge else []
    

def add_challenge_to_quest(db: Session, quest_id: int, challenge_id: int) -> bool:
    """Add challenge to quest if not already associated"""
    # Check if association already exists
    existing = db.execute(
        quest_challenge_association.select().where(
            and_(
                quest_challenge_association.c.quest_id == quest_id,
                quest_challenge_association.c.challenge_id == challenge_id
            )
        )
    ).first()
    
    if not existing:
        stmt = quest_challenge_association.insert().values(
            quest_id=quest_id,
            challenge_id=challenge_id
        )
        db.execute(stmt)
        db.commit()
    return True

def remove_challenge_from_quest(db: Session, quest_id: int, challenge_id: int) -> bool:
    """Remove challenge from quest"""
    stmt = quest_challenge_association.delete().where(
        and_(
            quest_challenge_association.c.quest_id == quest_id,
            quest_challenge_association.c.challenge_id == challenge_id
        )
    )
    result = db.execute(stmt)
    db.commit()
    return result.rowcount > 0

def set_quest_challenges(db: Session, quest_id: int, challenge_ids: List[int]) -> bool:
    """Set the complete list of challenges for a quest (replaces existing)"""
    # First remove all existing associations
    db.execute(
        quest_challenge_association.delete().where(
            quest_challenge_association.c.quest_id == quest_id
        )
    )
    
    # Add new associations
    for challenge_id in challenge_ids:
        add_challenge_to_quest(db, quest_id, challenge_id)
    
    db.commit()
    return True