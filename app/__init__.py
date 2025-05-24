import os
import psycopg2
from pathlib import Path
from sqlalchemy import create_engine, MetaData, text, Boolean
from sqlalchemy.orm import sessionmaker
from app import models
from app.database import Base, engine
from app.crud import *
import random
from typing import List, Dict, Any
from dotenv import load_dotenv
from alembic.config import Config
from alembic import command



from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


DATABASE_URL = "postgresql://postgres:postgres@postgres:5432/quest_app"

try:
    engine = create_engine(DATABASE_URL)
    connection = engine.connect()
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    print("✅ Успешное подключение к базе данных!")

except Exception as e:
    print(f"❌ Ошибка подключения: {e}")
def apply_migrations():
    """Применяет все pending миграции Alembic"""
    try:
        base_dir = Path(__file__).resolve().parent
        alembic_cfg = Config(os.path.join(base_dir, "alembic.ini"))
        
        print("🔄 Применение миграций...")
        command.upgrade(alembic_cfg, "head")
        print("✅ Миграции успешно применены!")
    except Exception as e:
        print(f"❌ Ошибка при применении миграций: {e}")
        raise

def ensure_tables_exist():
    """Гарантирует, что таблицы существуют в базе данных"""
    try:
        print("🔄 Проверка существования таблиц...")
        Base.metadata.create_all(bind=engine)
        print("✅ Таблицы успешно созданы/проверены")
    except Exception as e:
        print(f"❌ Ошибка при создании таблиц: {e}")
        raise

def create_tables_if_not_exist():
    """Создаёт таблицы напрямую (если Alembic не используется)"""
    try:
        print("🔄 Создание таблиц...")
        Base.metadata.create_all(bind=engine)
        print("✅ Таблицы успешно созданы!")
    except Exception as e:
        print(f"❌ Ошибка при создании таблиц: {e}")
        raise

def init_db(use_alembic: bool = True):
    """Инициализация базы данных"""
    if use_alembic:
        apply_migrations()
    else:
        create_tables_if_not_exist()
    
    ensure_tables_exist()

#def clear_db():
   # """Очистка базы данных"""
   # print("⚠️ Очистка базы данных...")
    #Base.metadata.drop_all(bind=engine)
  #  print("🗑️ База данных очищена")

def clear_database_tables():
    
    # 2. Список таблиц для очистки (в правильном порядке)
    tables = [
    '"quest_challenge_association"',
    '"Challenge"',
    '"Quest"',
    '"AgeGroup"',
    '"User"'
    ]
    
    # 3. Выполняем очистку
    with engine.connect() as connection:
        # Отключаем проверку внешних ключей для удобства
        connection.execute(text("SET session_replication_role = 'replica'"))
        
        # Очищаем все таблицы одной командой
        truncate_command = f"TRUNCATE TABLE {', '.join(tables)} CASCADE"
        connection.execute(text(truncate_command))
        
        # Включаем проверку обратно
        connection.execute(text("SET session_replication_role = 'origin'"))
        connection.commit()
    
    print("✅ Все данные из таблиц успешно удалены")

def populate_test_data(db: Session) -> Dict[str, List]:
    """Заполнение базы тестовыми данными"""
    print("🛠️ Создание тестовых данных...")
    
    # Создаем возрастные группы
    age_groups = [
        {"id": 1, "name": "Дети", "min_age": 5, "max_age": 12},
        {"id": 2, "name": "Подростки", "min_age": 13, "max_age": 17},
        {"id": 3, "name": "Взрослые", "min_age": 18, "max_age": 99}
    ]
    
    created_age_groups = [create_age_group(db, **group) for group in age_groups]
    
    # Создаем пользователей
    users = [
        {"phone_number": 1234567, "password": "password1"},
        {"phone_number": 7654321, "password": "password2"},
        {"phone_number": 5553535, "password": "securepass123"}
    ]
    
    created_users = [create_user(db, **user) for user in users]
    


# 1. Create challenges
    challenge_types = ["интеллектуальный", "творческий", "спортивный", "социальный"]
    location_types = ["дома", "на улице", "везде"]

    challenges = []
    challenge_data = [
    {
        "id": 1, 
        "title": "Шифр",
        "type": random.choice(challenge_types),
        "location_type": random.choice(location_types),
        "duration_min": random.randint(5, 60),
        "age_group_id": random.choice([g.id for g in created_age_groups]),
        "rules": "Подробные правила для челленджа 1",
    },
    {
        "id": 2, 
        "title": "Квиз",
        "type": random.choice(challenge_types),
        "location_type": random.choice(location_types),
        "duration_min": random.randint(5, 60),
        "age_group_id": random.choice([g.id for g in created_age_groups]),
        "rules": "Подробные правила для челленджа 2"
    },
    {
        "id": 3, 
        "title": "Прятки",
        "type": random.choice(challenge_types),
        "location_type": random.choice(location_types),
        "duration_min": random.randint(5, 60),
        "age_group_id": random.choice([g.id for g in created_age_groups]),
        "rules": "Подробные правила для челленджа 3"
    },
    {
        "id": 4, 
        "title": "Догонялки",
        "type": random.choice(challenge_types),
        "location_type": random.choice(location_types),
        "duration_min": random.randint(5, 60),
        "age_group_id": random.choice([g.id for g in created_age_groups]),
        "rules": "Подробные правила для челленджа 4"
    }
]

# Create challenges and save real objects
    for data in challenge_data:
        challenge = create_challenge(db, **data)
        challenges.append(challenge)

    print(f"✅ Создано {len(challenges)} челленджей")

# 2. Create quests
    quests = []
    quest_data = [
    {
        "id": 1,
        "user_id": created_users[0].phone_number,  # Using existing user
        "total_duration": random.randint(30, 180),
        "location_type": random.choice(location_types),
        "age_group_id": random.choice([g.id for g in created_age_groups]),
        "challenge_ids": [challenges[0].id, challenges[1].id]  # Pre-selected challenges
    },
    {
        "id": 2,
        "user_id": created_users[1].phone_number if len(created_users) > 1 else created_users[0].phone_number,
        "total_duration": random.randint(30, 180),
        "location_type": random.choice(location_types),
        "age_group_id": random.choice([g.id for g in created_age_groups]),
        "challenge_ids": [challenges[2].id]  # Pre-selected challenges
    }
    ]

# Create quests with challenges
    for data in quest_data:
    # Extract challenge_ids if present
        challenge_ids = data.pop("challenge_ids", [])
    
    # Create quest
        quest = create_quest(db, **data)
    
    # Add challenges to quest
        if challenge_ids:
            set_quest_challenges(db, quest.id, challenge_ids)
            print(f"➡️ Добавлены челленджи {challenge_ids} в квест {quest.id}")
    
        quests.append(quest)
        print(f"✅ Создан квест ID: {quest.id}")

# 3. Optionally add random challenges to some quests
    for quest in quests:
        if random.choice([True, False]):  # 50% chance to add more challenges
            available_challenges = [c for c in challenges if c.id not in [ch.id for ch in quest.challenges]]
            if available_challenges:
                challenge_to_add = random.choice(available_challenges)
                add_challenge_to_quest(db, quest.id, challenge_to_add.id)
                print(f"➡️ Дополнительно добавлен челлендж {challenge_to_add.id} в квест {quest.id}")

    print(f"✅ Всего создано {len(quests)} квестов")
    print("✅ Тестовые данные созданы")

    return {
    "users": created_users,
    "age_groups": created_age_groups,
    "challenges": challenges,
    "quests": quests
    }

def test_user_crud(db: Session, test_user: models.User):
    """Тестирование CRUD операций для пользователей"""
    print("\n=== ТЕСТИРОВАНИЕ ПОЛЬЗОВАТЕЛЕЙ ===")
    
    # Тест создания
    new_user = create_user(db, phone_number=9998877, password="newuserpass")
    print(f"Создан новый пользователь: {new_user.phone_number}")
    
    # Тест чтения
    db_user = get_user(db, test_user.phone_number)
    print(f"Найден пользователь: {db_user.phone_number if db_user else 'не найден'}")
    
    # Тест обновления
    #updated_user = update_user(db, test_user.phone_number, {"phone_number": 12243})
    #print(f"Обновлен номер: {test_user.phone_number} -> {updated_user.phone_number}")
    
    # Тест удаления
    if delete_user(db, new_user.phone_number):
        print(f"Пользователь {new_user.phone_number} удален")

def test_age_group_crud(db: Session, test_age_group: models.AgeGroup):
    """Тестирование CRUD операций для возрастных групп"""
    print("\n=== ТЕСТИРОВАНИЕ ВОЗРАСТНЫХ ГРУПП ===")
    
    # Тест создания
    new_group = create_age_group(db, id=4, name="Новая группа", min_age=25, max_age=40)
    print(f"Создана новая возрастная группа: {new_group.name}")
    
    # Тест чтения
    db_group = get_age_group(db, test_age_group.id)
    print(f"Найдена группа: {db_group.name if db_group else 'не найдена'}")
    
    # Тест обновления
    updated_group = update_age_group(db, new_group.id, {"name": "Обновленная группа", "max_age": 50})
    print(f"Обновлена группа: ID {updated_group.id}, новое имя: {updated_group.name}")
    
    # Тест фильтрации
    suitable_groups = get_age_groups_by_age(db, age=15)
    print(f"Группы для возраста 15: {[g.name for g in suitable_groups]}")
    
    # Тест удаления
    if delete_age_group(db, new_group.id):
        print(f"Группа {new_group.name} удалена")

def test_challenge_crud(db: Session, test_challenge: models.Challenge):
    """Тестирование CRUD операций для челленджей"""
    print("\n=== ТЕСТИРОВАНИЕ ЧЕЛЛЕНДЖЕЙ ===")
    
    # Тест создания
    new_challenge = create_challenge(
        db,
        id=6,
        title="Новый челлендж",
        type="спортивный",
        location_type="на улице",
        duration_min=30,
        age_group_id=test_challenge.age_group_id,
        rules="Новые правила"
    )
    print(f"Создан новый челлендж: {new_challenge.title}")
    
    # Тест чтения
    db_challenge = get_challenge(db, test_challenge.id)
    print(f"Найден челлендж: {db_challenge.title if db_challenge else 'не найден'}")
    
    # Тест получения связанных квестов
    challenge_quests = get_challenge_quests(db, test_challenge.id)
    print(f"Челлендж используется в квестах: {len(challenge_quests)}")
    
    # Тест обновления
    updated_challenge = update_challenge(db, new_challenge.id, {"title": "Обновленный челлендж", "duration_min": 45})
    print(f"Обновлен челлендж: {updated_challenge.title}, длительность: {updated_challenge.duration_min} мин")
    
    # Тест фильтрации
    filtered_challenges = get_challenges_by_filters(
        db,
        age_group_id=test_challenge.age_group_id,
        challenge_type=test_challenge.type,
        location_type=test_challenge.location_type
    )
    print(f"Найдено челленджей по фильтру: {len(filtered_challenges)}")
    
    # Тест удаления (проверяем каскадное удаление связей)
    if delete_challenge(db, new_challenge.id):
        print(f"Челлендж {new_challenge.title} удален")
        # Проверяем что связи удалились
        remaining_quests = get_challenge_quests(db, new_challenge.id)
        #print(f"Осталось связей с квестами: {len(remaining_quests)} (должно быть 0)")

def test_quest_crud(db: Session, test_quest: models.Quest, test_challenges: List[models.Challenge]):
    """Тестирование CRUD операций для квестов"""
    print("\n=== ТЕСТИРОВАНИЕ КВЕСТОВ ===")
    
    # Тест создания с сразу заданными челленджами
    new_quest = create_quest(
        db,
        id=5,
        user_id=test_quest.user_id,
        total_duration=90,
        location_type="везде",
        age_group_id=test_quest.age_group_id
    )
    print(f"Создан новый квест: ID {new_quest.id}")
    
    # Добавляем челленджи (3 случайных)
    selected_challenges = random.sample(test_challenges, min(3, len(test_challenges)))
    for challenge in selected_challenges:
        add_challenge_to_quest(db, new_quest.id, challenge.id)
    print(f"Добавлено челленджей в квест: {len(selected_challenges)}")
    
    # Тест чтения
    db_quest = get_quest(db, test_quest.id)
    print(f"Найден квест: ID {db_quest.id if db_quest else 'не найден'}")
    
    # Тест получения челленджей
    quest_challenges = get_quest_challenges(db, new_quest.id)
    print(f"Квест содержит челленджей: {len(quest_challenges)}")
    if hasattr(new_quest, 'challenges') and new_quest.challenges:
        print("\nЧелленджи:")
        for challenge in new_quest.challenges:
            print(f"- {challenge.title} (ID: {challenge.id})")
    
    # Тест массового обновления челленджей
    if len(test_challenges) > 1:
        new_challenge_ids = [test_challenges[0].id, test_challenges[-1].id]
        set_quest_challenges(db, new_quest.id, new_challenge_ids)
        updated_challenges = get_quest_challenges(db, new_quest.id)
        print(f"Обновлено челленджей в квесте: {len(updated_challenges)}")
    
    # Тест обновления параметров квеста
    updated_quest = update_quest(db, new_quest.id, {"total_duration": 120})
    print(f"Обновлено время квеста: {updated_quest.total_duration} мин")
    
    # Тест удаления челленджа из квеста
    if quest_challenges:
        removed = remove_challenge_from_quest(db, new_quest.id, quest_challenges[0].id)
        print(f"Челлендж удален из квеста: {'успешно' if removed else 'ошибка'}")
    
    # Тест удаления квеста (проверяем каскадное удаление связей)
    if delete_quest(db, new_quest.id):
        print(f"Квест ID {new_quest.id} удален")
        # Проверяем что связи удалились
        remaining_challenges = get_quest_challenges(db, new_quest.id)
        

def run_tests():
    """Запуск всех тестов"""
    db = TestingSessionLocal()
    
    try:
        clear_database_tables()
        init_db()
        
        test_data = populate_test_data(db)
        
        test_user_crud(db, test_data["users"][1])
        test_age_group_crud(db, test_data["age_groups"][2])
        test_challenge_crud(db, test_data["challenges"][1])
        test_quest_crud(db, test_data["quests"][0], test_data["challenges"])
        
        print("\n✅ ВСЕ ТЕСТЫ УСПЕШНО ЗАВЕРШЕНЫ")
    except Exception as e:
        print(f"\n❌ ОШИБКА: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    run_tests()