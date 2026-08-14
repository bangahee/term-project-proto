# FastAPI 메인 앱 및 API 구현
# main.py: 서버 로깅, 입력 검증(Pydantic), DB 연동, JWT 인증 및 페이지 라우팅 통합

import logging
from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

import models
import auth
from database import engine, get_db, init_db
from ai_service import get_ai_response

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("app_logger")

# DB 테이블 생성
init_db()

app = FastAPI(title="AI Chatbot Service")
templates = Jinja2Templates(directory="templates")


# -------------------------------------------------------------------
# Pydantic Schemas (입력 검증)
# -------------------------------------------------------------------
class UserAuth(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=4, max_length=100)

class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=500, description="빈 입력 차단 및 길이 제한")


# -------------------------------------------------------------------
# HTML 페이지 라우터 (다중 페이지 접속)
# -------------------------------------------------------------------
@app.get("/", response_class=HTMLResponse)
@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse(request=request, name="login.html")

@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse(request=request, name="register.html")

@app.get("/chat", response_class=HTMLResponse)
async def chat_page(request: Request):
    return templates.TemplateResponse(request=request, name="chat.html")


# -------------------------------------------------------------------
# API Endpoints
# -------------------------------------------------------------------

# 1. 회원가입 API
@app.post("/api/auth/register", status_code=status.HTTP_201_CREATED)
async def register(user_data: UserAuth, db: Session = Depends(get_db)):
    existing_user = db.query(models.User).filter(models.User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="이미 존재하는 아이디입니다.")
    
    hashed_pwd = auth.get_password_hash(user_data.password)
    new_user = models.User(username=user_data.username, hashed_password=hashed_pwd)
    db.add(new_user)
    db.commit()
    return {"message": "회원가입 완료"}


# 2. 로그인 API
@app.post("/api/auth/login")
async def login(user_data: UserAuth, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == user_data.username).first()
    if not user or not auth.verify_password(user_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="아이디 또는 비밀번호가 올바르지 않습니다.")
    
    access_token = auth.create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


# 3. 보호된 AI 챗봇 API (로그인 사용자 전용)
@app.post("/api/chat")
async def chat_endpoint(
    req: ChatRequest, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    logger.info(f"request_received user_id={current_user.id} question={req.question[:20]}")

    # 최근 3개 대화 기록 조회 (Context 구성용)
    recent_chats = (
        db.query(models.ChatLog)
        .filter(models.ChatLog.user_id == current_user.id)
        .order_by(models.ChatLog.created_at.desc())
        .limit(3)
        .all()
    )

    # AI API 호출
    ai_response = await get_ai_response(req.question, recent_chats)

    # DB 저장
    try:
        chat_log = models.ChatLog(
            user_id=current_user.id,
            question=req.question,
            response=ai_response
        )
        db.add(chat_log)
        db.commit()
        logger.info(f"db_save_success user_id={current_user.id} chat_id={chat_log.id}")
    # except Exception as e:
    #     logger.error(f"db_save_failed reason={str(e)}")
    except Exception as e:
        db.rollback()
        logger.error(f"db_save_failed reason={str(e)}")

    return {"question": req.question, "response": ai_response}


# 4. 내 대화 기록 조회 API
@app.get("/api/me/chats")
async def get_my_chats(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    logs = (
        db.query(models.ChatLog)
        .filter(models.ChatLog.user_id == current_user.id)
        .order_by(models.ChatLog.created_at.asc())
        .all()
    )
    return [
        {"id": l.id, "question": l.question, "response": l.response, "time": l.created_at.isoformat()}
        for l in logs
    ]