from fastapi import FastAPI, Depends, HTTPException, status, APIRouter, Response
from sqlalchemy.orm import Session
from sqlalchemy import Boolean
from typing import List, Optional, Union
from app.database import SessionLocal, engine
from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from . import models, crud, utils, schemas
from .database import get_db
from fastapi import Request, Form
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from starlette.middleware.sessions import SessionMiddleware
from fastapi import Query
import os
from fastapi.exception_handlers import (
    http_exception_handler,
    request_validation_exception_handler,
)
import traceback
from fastapi.exceptions import RequestValidationError

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Настройка Jinja2
BASE_DIR = Path(__file__).resolve().parent


static_path = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=static_path), name="static")
templates = Jinja2Templates(directory="app/templates")

# Добавьте после создания app
app.add_middleware(GZipMiddleware)
    
SECRET_KEY = "1234"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Создаем основной роутер для аутентификации
auth_router = APIRouter(prefix="/auth", tags=["Authentication"])
security = HTTPBearer(auto_error=False)

# Схема для входа через JSON
class LoginRequest(BaseModel):
    phone_number: int
    password: str

# Хранилище для токенов
token_blacklist = set()

def add_token_to_blacklist(token: str):
    token_blacklist.add(token)

def is_token_blacklisted(token: str) -> bool:
    return token in token_blacklist

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(
    request: Request,
    db: Session = Depends(get_db)
) -> models.User:
    token = request.cookies.get("access_token")
    if not token or not token.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    token = token[7:]  # Remove "Bearer "
    
    if token in token_blacklist:
        raise HTTPException(status_code=401, detail="Token revoked")
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        phone_number = payload.get("sub")
        if not phone_number:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user = crud.get_user(db, phone_number=int(phone_number))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    return user

async def get_current_user_optional(
    request: Request,
    db: Session = Depends(get_db)
) -> Optional[models.User]:
    try:
        return await get_current_user(request, db)
    except HTTPException:
        return None

@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException):
    if "text/html" in request.headers.get("accept", ""):

        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "error": f"Ошибка {exc.status_code}",
                "detail": exc.detail,
            },
            status_code=exc.status_code,
            
        )
    return await http_exception_handler(request, exc)


@auth_router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("auth/register.html", {"request": request})

@auth_router.post("/register", response_class=HTMLResponse)
async def register_user_form(
    request: Request,
    phone_number: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    try:
        if crud.get_user(db, phone_number=int(phone_number)):
            return templates.TemplateResponse("auth/register.html", 
                {"request": request, "error": "Номер телефона уже зарегистрирован"})
        
        user_data = schemas.UserCreate(
            phone_number=int(phone_number),
            password=password,
        )
        
        db_user = models.User(
            phone_number=user_data.phone_number,
            is_active=user_data.is_active
        )
        db_user.set_password(user_data.password)
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        return RedirectResponse(url="/auth/login", status_code=status.HTTP_303_SEE_OTHER)
    except Exception as e:
        return templates.TemplateResponse("auth/register.html", 
            {"request": request, "error": str(e)})

@auth_router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("auth/login.html", {"request": request})
@auth_router.post("/token", response_class=HTMLResponse)
async def login_for_access_token(
    request: Request,
    phone_number: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    try:
        user = crud.get_user(db, phone_number=int(phone_number))
        if not user or not utils.verify_password(password, user.password_hash):
            return templates.TemplateResponse("auth/login.html", {
                "request": request,
                "error": "Неверный номер телефона или пароль"
            })
        
        access_token = create_access_token(data={"sub": str(user.phone_number)})
        
        response = RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
        response.set_cookie(
            key="access_token",
            value=f"Bearer {access_token}",
            httponly=True,
            secure=True,  # Для HTTPS
            samesite='lax'
        )
        return response
    except Exception as e:
        return templates.TemplateResponse("auth/login.html", {
            "request": request,
            "error": str(e)
        })

@auth_router.get("/me", response_class=HTMLResponse)
async def get_current_user_profile(
    request: Request,
    current_user: models.User = Depends(get_current_user)
):
    return templates.TemplateResponse("users/profile.html", {
        "request": request,
        "current_user": current_user
    })

@auth_router.post("/logout", response_class=HTMLResponse)
async def logout(request: Request):
    # Проверяем токен из куки
    token = request.cookies.get("access_token")
    if token and token.startswith("Bearer "):
        token = token[7:]  # Удаляем "Bearer "
        token_blacklist.add(token)
    
    response = RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie("access_token")
    return response

@auth_router.get("/logout", response_class=HTMLResponse)
async def logout_page(request: Request):
    return await logout(request)

# Подключаем роутер аутентификации
app.include_router(auth_router)


# роут для главной страницы
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request, current_user: Optional[models.User] = Depends(get_current_user_optional)):
    return templates.TemplateResponse("index.html", {"request": request, "current_user": current_user})


@app.get("/profile", response_class=HTMLResponse)
async def user_profile(
    request: Request,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user_quests = crud.get_quests_by_filters(db, user_id=current_user.phone_number)
    return templates.TemplateResponse("users/profile.html", {
        "request": request,
        "current_user": current_user,
        "user_quests": user_quests
    })

@auth_router.get("/users/{phone_number}/edit", response_class=HTMLResponse)
async def edit_user_page(
    request: Request,
    phone_number: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    if current_user.phone_number != phone_number and not getattr(current_user, 'is_admin', False):
        raise HTTPException(status_code=403, detail="Недостаточно прав")
    
    user = crud.get_user(db, phone_number=phone_number)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    
    return templates.TemplateResponse("users/edit.html", {
        "request": request,
        "current_user": current_user,
        "user": user
    })
@app.get("/quests/new", response_class=HTMLResponse)  # Новый маршрут для формы
async def show_create_quest_form(
    request: Request,
    db: Session = Depends(get_db),
    current_user: Optional[models.User] = Depends(get_current_user_optional)
):
    age_groups = crud.get_age_groups(db)
    challenges = crud.get_challenges(db)
    
    return templates.TemplateResponse("quests/create.html", {
        "request": request,
        "current_user": current_user,
        "age_groups": age_groups,
        "challenges": challenges,
        "error": None
    })

@app.post("/quests", response_class=HTMLResponse)
async def create_quest_form(
    request: Request,
    #id: int = Form(...),
    total_duration: int = Form(...),
    location_type: str = Form(...),
    age_group_id: int = Form(...),
    challenge_ids: List[int] = Form([]),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_optional)
):
    try:
        quest_data = schemas.QuestCreate(
            #id=id,
            user_id=current_user.phone_number,
            total_duration=total_duration,
            location_type=location_type,
            age_group_id=age_group_id,
            challenge_ids=challenge_ids
        )
        
        quest = crud.create_quest(
            db=db,
            #id=id,
            user_id=quest_data.user_id,
            total_duration=quest_data.total_duration,
            location_type=quest_data.location_type,
            age_group_id=quest_data.age_group_id,
            challenge_ids=quest_data.challenge_ids
        )
        
        return RedirectResponse(url=f"/quests/{quest.id}", status_code=status.HTTP_303_SEE_OTHER)
    except Exception as e:
        age_groups = crud.get_age_groups(db)
        challenges = crud.get_challenges(db)
        
        return templates.TemplateResponse("quests/create.html", {
            "request": request,
            "current_user": current_user,
            "age_groups": age_groups,
            "challenges": challenges,
            "error": str(e)
        })

@app.get("/quests", response_class=HTMLResponse)
async def read_quests_page(
    request: Request,
    user_id: Optional[str] = Query(None),
    age_group_id: Optional[str] = Query(None),
    location_type: Optional[str] = Query(None),
    challenge_id: Optional[str] = Query(None),
    total_duration: Optional[str] = Query(None),  # Только один параметр длительности
    db: Session = Depends(get_db),
    current_user: Optional[models.User] = Depends(get_current_user_optional)
):
    # Валидация и преобразование параметров
    def parse_int_param(param: Optional[str], param_name: str) -> Optional[int]:
        if param is None or param.strip() == "":
            return None
        try:
            return int(param)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid {param_name} value: must be integer"
            )

    try:
        age_group_id_int = parse_int_param(age_group_id, "age_group_id")
        challenge_id_int = parse_int_param(challenge_id, "challenge_id")
        total_duration_int = parse_int_param(total_duration, "total_duration")
        
        # Валидация продолжительности
        if total_duration_int is not None and total_duration_int < 0:
            raise HTTPException(
                status_code=400,
                detail="total_duration must be positive"
            )
        
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid parameters: {str(e)}"
        )

    # Применение фильтров
    filters = {
        'user_id': user_id,  # Оставляем как строку (phone_number)
        'age_group_id': age_group_id_int,
        'location_type': location_type,
        'challenge_id': challenge_id_int,
        'total_duration': total_duration_int
    }
    filters = {k: v for k, v in filters.items() if v is not None}
    
    quests = crud.get_quests_by_filters(db, **filters)
    
    age_groups = crud.get_age_groups(db)
    challenges = crud.get_challenges(db)
    users = crud.get_users(db) if current_user and getattr(current_user, 'is_admin', False) else None
    
    return templates.TemplateResponse("quests/list.html", {
        "request": request,
        "current_user": current_user,
        "quests": quests,
        "age_groups": age_groups,
        "challenges": challenges,
        "users": users
    })

# Для детальной страницы квеста (GET)
@app.get("/quests/{quest_id}", response_class=HTMLResponse)
async def read_quest_detail(
    request: Request,
    quest_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[models.User] = Depends(get_current_user_optional)
):
    quest = crud.get_quest(db, quest_id=quest_id)
    if not quest:
        raise HTTPException(status_code=404, detail="Quest not found")
    
    return templates.TemplateResponse("quests/detail.html", {
        "request": request,
        "current_user": current_user,
        "quest": quest
    })

@app.post("/quests/{quest_id}/delete", response_class=HTMLResponse)
async def delete_quest_form(
    request: Request,
    quest_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    quest = crud.get_quest(db, quest_id=quest_id)
    if not quest:
        raise HTTPException(status_code=404, detail="Квест не найден")
    
    if quest.user_id != current_user.phone_number:
        raise HTTPException(status_code=403, detail="Недостаточно прав")
    
    crud.delete_quest(db, quest_id=quest_id)
    return RedirectResponse(url="/quests", status_code=status.HTTP_303_SEE_OTHER)

#ЗАДАНИЯ (фильтрация)
@app.get("/challenges", response_class=HTMLResponse)
async def read_challenges_page(
    request: Request,
    age_group_id: Optional[int] = None,
    type: Optional[str] = None,
    location_type: Optional[str] = None,
    min_duration: Optional[int] = None,
    max_duration: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: Optional[models.User] = Depends(get_current_user_optional)
):
    challenges = crud.get_challenges_by_filters(
        db,
        age_group_id=age_group_id,
        type=type,
        location_type=location_type,
        min_duration=min_duration,
        max_duration=max_duration
    )
    
    age_groups = crud.get_age_groups(db)
    
    return templates.TemplateResponse("challenges/list.html", {
        "request": request,
        "current_user": current_user,
        "challenges": challenges,
        "age_groups": age_groups,
        "selected_age_group": age_group_id,
        "type": type,
        "location_type": location_type,
        "min_duration": min_duration,
        "max_duration": max_duration
    })



@app.get("/challenges/create", response_class=HTMLResponse)
async def create_challenge_page(
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    age_groups = crud.get_age_groups(db)
    return templates.TemplateResponse("challenges/create.html", {
        "request": request,
        "current_user": current_user,
        "age_groups": age_groups
    })

@app.post("/challenges", response_class=HTMLResponse)
async def create_challenge_form(
    request: Request,
    #id: int = Form(...),
    title: str = Form(...),
    type: str = Form(...),  # Обратите внимание: name="type" в форме
    location_type: str = Form(...),
    duration_min: int = Form(...),
    age_group_id: int = Form(...),
    rules: str = Form(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    try:
        challenge_data = schemas.ChallengeCreate(
           # id=id,
            title=title,
            type=type,  # Здесь сопоставляем с полем модели
            location_type=location_type,
            duration_min=duration_min,
            age_group_id=age_group_id,
            rules=rules
        )
        
        challenge = crud.create_challenge(db, challenge_data)
        
        return RedirectResponse(url=f"/challenges/{challenge.id}", status_code=status.HTTP_303_SEE_OTHER)
    except Exception as e:
        age_groups = crud.get_age_groups(db)
        
        return templates.TemplateResponse("challenges/create.html", {
            "request": request,
            "current_user": current_user,
            "age_groups": age_groups,
            "error": str(e)
        })
#Конкретное задание
@app.get("/challenges/{challenge_id}", response_class=HTMLResponse)
async def read_challenge_page(
    request: Request,
    challenge_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[models.User] = Depends(get_current_user_optional)
):
    challenge = crud.get_challenge(db, challenge_id=challenge_id)
    if not challenge:
        raise HTTPException(status_code=404, detail="Задание не найдено")
    
    quests_with_challenge = crud.get_quests_by_challenge(db, challenge_id=challenge_id)
    
    return templates.TemplateResponse("challenges/detail.html", {
        "request": request,
        "current_user": current_user,
        "challenge": challenge,
        "quests_with_challenge": quests_with_challenge
    })
'''@app.post("/challenges/{challenge_id}", response_class=HTMLResponse)
async def update_challenge_form(
    request: Request,
    challenge_id: int,
    title: str = Form(...),
    description: str = Form(...),
    challenge_type: str = Form(...),
    location_type: str = Form(...),
    duration: int = Form(...),
    age_group_id: int = Form(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_optional)
):
    try:
        challenge = crud.get_challenge(db, challenge_id=challenge_id)
        if not challenge:
            raise HTTPException(status_code=404, detail="Задание не найдено")
        
        challenge_update = schemas.ChallengeUpdate(
            title=title,
            description=description,
            challenge_type=challenge_type,
            location_type=location_type,
            duration=duration,
            age_group_id=age_group_id
        )
        
        updated_challenge = crud.update_challenge(
            db, 
            challenge_id=challenge_id, 
            update_data=challenge_update.dict(exclude_unset=True)
        )
        
        return RedirectResponse(url=f"/challenges/{challenge_id}", status_code=status.HTTP_303_SEE_OTHER)
    except Exception as e:
        age_groups = crud.get_age_groups(db)
        challenge = crud.get_challenge(db, challenge_id=challenge_id)
        
        return templates.TemplateResponse("challenges/edit.html", {
            "request": request,
            "current_user": current_user,
            "challenge": challenge,
            "age_groups": age_groups,
            "error": str(e)
        })'''

@app.post("/challenges/{challenge_id}/delete", response_class=HTMLResponse)
async def delete_challenge_form(
    request: Request,
    challenge_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    challenge = crud.get_challenge(db, challenge_id=challenge_id)
    if not challenge:
        raise HTTPException(status_code=404, detail="Задание не найдено")
    
    crud.delete_challenge(db, challenge_id=challenge_id)
    return RedirectResponse(url="/challenges", status_code=status.HTTP_303_SEE_OTHER)



# Добавьте этот роут для API быстрого просмотра
@app.get("/api/challenges/{challenge_id}", response_model=schemas.ChallengeWithAgeGroup)
async def read_challenge_api(
    challenge_id: int,
    db: Session = Depends(get_db)
):
    challenge = crud.get_challenge(db, challenge_id=challenge_id)
    if not challenge:
        raise HTTPException(status_code=404, detail="Challenge not found")
    return challenge

@app.post("/age-groups", response_class=HTMLResponse)
async def create_age_group_form(
    request: Request,
    name: str = Form(...),
    min_age: int = Form(...),
    max_age: int = Form(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_optional)
):
    try:
        age_group_data = schemas.AgeGroupCreate(
            name=name,
            min_age=min_age,
            max_age=max_age,
            
        )
        
        age_group = crud.create_age_group(db=db, **age_group_data.dict())
        
        return RedirectResponse(url="/age-groups", status_code=status.HTTP_303_SEE_OTHER)
    except Exception as e:
        return templates.TemplateResponse("age_groups/create.html", {
            "request": request,
            "current_user": current_user,
            "error": str(e)
        })

@app.get("/age-groups/{age_group_id}/edit", response_class=HTMLResponse)
async def edit_age_group_page(
    request: Request,
    age_group_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    age_group = crud.get_age_group(db, age_group_id=age_group_id)
    if not age_group:
        raise HTTPException(status_code=404, detail="Возрастная группа не найдена")
    
    return templates.TemplateResponse("age_groups/edit.html", {
        "request": request,
        "current_user": current_user,
        "age_group": age_group
    })
# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()