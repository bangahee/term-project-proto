# FastAPI 메인 앱 및 API 구현
# main.py: 서버 로깅, 입력 검증(Pydantic), DB 연동, JWT 인증 및 페이지 라우팅 통합

import logging
import uuid

from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field, field_validator

import models
import auth
from database import get_db, init_db
from ai_service import get_ai_response


# -------------------------------------------------------------------
# 로깅 설정
# -------------------------------------------------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("app_logger")


# -------------------------------------------------------------------
# DB 테이블 생성
# -------------------------------------------------------------------
init_db()


# -------------------------------------------------------------------
# FastAPI 앱 및 템플릿 설정
# -------------------------------------------------------------------
app = FastAPI(title="AI Chatbot Service")
templates = Jinja2Templates(directory="templates")


# -------------------------------------------------------------------
# Pydantic Schemas (입력 검증)
# -------------------------------------------------------------------
class UserAuth(BaseModel):
    username: str = Field(
        ...,
        min_length=3,
        max_length=50
    )
    password: str = Field(
        ...,
        min_length=4,
        max_length=100
    )


class ChatRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="빈 입력 차단 및 길이 제한"
    )

    @field_validator("question")
    @classmethod
    def validate_question(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("질문은 공백일 수 없습니다.")

        return value


# -------------------------------------------------------------------
# HTML 페이지 라우터 (다중 페이지 접속)
# -------------------------------------------------------------------

@app.get("/", response_class=HTMLResponse)
@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="login.html"
    )


@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="register.html"
    )


@app.get("/chat", response_class=HTMLResponse)
async def chat_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="chat.html"
    )


# -------------------------------------------------------------------
# API Endpoints
# -------------------------------------------------------------------

# -------------------------------------------------------------------
# 1. 회원가입 API
# -------------------------------------------------------------------
@app.post(
    "/api/auth/register",
    status_code=status.HTTP_201_CREATED
)
async def register(
    user_data: UserAuth,
    db: Session = Depends(get_db)
):
    existing_user = (
        db.query(models.User)
        .filter(models.User.username == user_data.username)
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="이미 존재하는 아이디입니다."
        )

    hashed_pwd = auth.get_password_hash(user_data.password)

    new_user = models.User(
        username=user_data.username,
        hashed_password=hashed_pwd
    )

    db.add(new_user)
    db.commit()

    return {
        "message": "회원가입 완료"
    }


# -------------------------------------------------------------------
# 2. 로그인 API
# -------------------------------------------------------------------
@app.post("/api/auth/login")
async def login(
    user_data: UserAuth,
    db: Session = Depends(get_db)
):
    user = (
        db.query(models.User)
        .filter(models.User.username == user_data.username)
        .first()
    )

    if (
        not user
        or not auth.verify_password(
            user_data.password,
            user.hashed_password
        )
    ):
        raise HTTPException(
            status_code=401,
            detail="아이디 또는 비밀번호가 올바르지 않습니다."
        )

    access_token = auth.create_access_token(
        data={"sub": user.username}
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


# -------------------------------------------------------------------
# 3. 보호된 AI 챗봇 API (로그인 사용자 전용)
# -------------------------------------------------------------------
@app.post("/api/chat")
async def chat_endpoint(
    req: ChatRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    # ---------------------------------------------------------------
    # 각 사용자 요청마다 고유한 request_id 생성
    #
    # 같은 request_id를
    # request_received → ai_call → db_save
    # 전체 과정에서 사용하여 하나의 요청 흐름을 추적할 수 있음
    # ---------------------------------------------------------------
    request_id = str(uuid.uuid4())

    # 요청 수신 로그
    # 실제 질문 내용은 개인정보 보호를 위해 로그에 기록하지 않고
    # 질문 길이만 기록
    logger.info(
        f"request_received "
        f"request_id={request_id} "
        f"user_id={current_user.id} "
        f"question_length={len(req.question)}"
    )

    # ---------------------------------------------------------------
    # 최근 3개 대화 기록 조회
    #
    # 같은 사용자의 최근 대화를 AI에게 전달하여
    # 최소한의 대화 문맥(Context)을 유지
    # ---------------------------------------------------------------
    recent_chats = (
        db.query(models.ChatLog)
        .filter(models.ChatLog.user_id == current_user.id)
        .order_by(models.ChatLog.created_at.desc())
        .limit(3)
        .all()
    )

    # ---------------------------------------------------------------
    # AI API 호출
    #
    # request_id도 함께 전달하여 ai_service.py에서 발생하는
    # AI 관련 로그와 현재 요청을 연결할 수 있도록 함
    # ---------------------------------------------------------------
    ai_response = await get_ai_response(
        req.question,
        recent_chats,
        request_id
    )

    # ---------------------------------------------------------------
    # DB 저장
    # ---------------------------------------------------------------
    try:
        chat_log = models.ChatLog(
            user_id=current_user.id,
            question=req.question,
            response=ai_response
        )

        db.add(chat_log)
        db.commit()

        # DB commit 이후 생성된 id 값을 안정적으로 사용하기 위해 refresh
        db.refresh(chat_log)

        logger.info(
            f"db_save_success "
            f"request_id={request_id} "
            f"user_id={current_user.id} "
            f"chat_id={chat_log.id}"
        )

    except Exception as e:
        # DB 저장 실패 시 실패한 트랜잭션을 되돌림
        db.rollback()

        logger.error(
            f"db_save_failed "
            f"request_id={request_id} "
            f"user_id={current_user.id} "
            f"reason={str(e)}"
        )

    # 사용자에게 질문과 AI 응답 반환
    return {
        "question": req.question,
        "response": ai_response
    }


# -------------------------------------------------------------------
# 4. 내 대화 기록 조회 API
# -------------------------------------------------------------------
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
        {
            "id": log.id,
            "question": log.question,
            "response": log.response,
            "time": log.created_at.isoformat()
        }
        for log in logs
    ]


# -------------------------------------------------------------------
# 5. 내 대화 기록 전체 삭제 API
# -------------------------------------------------------------------
@app.delete("/api/me/chats")
async def delete_my_chats(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    try:
        # -----------------------------------------------------------
        # 현재 로그인한 사용자의 대화 기록만 삭제
        #
        # current_user.id를 조건으로 사용하므로
        # 다른 사용자의 ChatLog는 삭제되지 않음
        # -----------------------------------------------------------
        deleted_count = (
            db.query(models.ChatLog)
            .filter(models.ChatLog.user_id == current_user.id)
            .delete(synchronize_session=False)
        )

        db.commit()

        logger.info(
            f"chat_history_delete_success "
            f"user_id={current_user.id} "
            f"deleted_count={deleted_count}"
        )

        return {
            "message": "대화 기록이 삭제되었습니다.",
            "deleted_count": deleted_count
        }

    except Exception as e:
        db.rollback()

        logger.error(
            f"chat_history_delete_failed "
            f"user_id={current_user.id} "
            f"reason={str(e)}"
        )

        raise HTTPException(
            status_code=500,
            detail="대화 기록 삭제 중 오류가 발생했습니다."
        )