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
# HTML 페이지 라우터
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
    # 동일한 아이디가 이미 존재하는지 확인
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

    # 비밀번호를 평문으로 저장하지 않고 Hash 처리
    hashed_pwd = auth.get_password_hash(
        user_data.password
    )

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
    # 아이디로 사용자 조회
    user = (
        db.query(models.User)
        .filter(models.User.username == user_data.username)
        .first()
    )

    # 사용자 존재 여부 및 비밀번호 검증
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

    # 로그인 성공 시 JWT Access Token 발급
    access_token = auth.create_access_token(
        data={
            "sub": user.username
        }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


# -------------------------------------------------------------------
# 3. 보호된 AI 챗봇 API
#
# 로그인한 사용자만 접근할 수 있습니다.
#
# 처리 흐름:
#
# 질문 수신
#     ↓
# 사용자 인증
#     ↓
# 최근 대화 조회
#     ↓
# AI API 호출
#     ↓
# AI 응답 수신
#     ↓
# DB 저장
#     ↓
# 질문 + 응답 + 생성 시각 반환
# -------------------------------------------------------------------
@app.post("/api/chat")
async def chat_endpoint(
    req: ChatRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(
        auth.get_current_user
    )
):
    # ---------------------------------------------------------------
    # 각 사용자 요청마다 고유한 request_id 생성
    #
    # 같은 request_id를
    #
    # request_received
    # → ai_call
    # → db_save
    #
    # 전체 과정에서 사용하여 하나의 요청 흐름을
    # 서버 로그에서 추적할 수 있도록 합니다.
    # ---------------------------------------------------------------
    request_id = str(uuid.uuid4())


    # ---------------------------------------------------------------
    # 요청 수신 로그
    #
    # 실제 질문 내용은 개인정보 보호를 위해 기록하지 않고
    # 질문의 길이만 기록합니다.
    # ---------------------------------------------------------------
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
    # 최소한의 대화 Context를 유지합니다.
    # ---------------------------------------------------------------
    recent_chats = (
        db.query(models.ChatLog)
        .filter(
            models.ChatLog.user_id
            == current_user.id
        )
        .order_by(
            models.ChatLog.created_at.desc()
        )
        .limit(3)
        .all()
    )


    # ---------------------------------------------------------------
    # AI API 호출
    #
    # request_id를 ai_service.py에도 전달하여
    # AI 호출 관련 로그와 현재 요청 로그를 연결합니다.
    # ---------------------------------------------------------------
    ai_response = await get_ai_response(
        req.question,
        recent_chats,
        request_id
    )


    # ---------------------------------------------------------------
    # 대화 로그 DB 저장
    #
    # 최소 추적 필드:
    #
    # user_id
    # question
    # response
    # created_at
    #
    # created_at은 models.py의 default 설정에 의해 생성됩니다.
    # ---------------------------------------------------------------
    try:
        chat_log = models.ChatLog(
            user_id=current_user.id,
            question=req.question,
            response=ai_response
        )

        db.add(chat_log)

        # DB에 실제 저장
        db.commit()

        # commit 이후 생성된 id, created_at 등의 값을
        # 현재 객체에 다시 불러옵니다.
        db.refresh(chat_log)


        # -----------------------------------------------------------
        # DB 저장 성공 로그
        # -----------------------------------------------------------
        logger.info(
            f"db_save_success "
            f"request_id={request_id} "
            f"user_id={current_user.id} "
            f"chat_id={chat_log.id}"
        )


    except Exception as e:
        # -----------------------------------------------------------
        # DB 저장 실패
        #
        # 실패한 transaction을 rollback하여
        # DB Session을 정상 상태로 복구합니다.
        # -----------------------------------------------------------
        db.rollback()

        logger.error(
            f"db_save_failed "
            f"request_id={request_id} "
            f"user_id={current_user.id} "
            f"reason={str(e)}"
        )

        # DB 저장이 실패했는데 정상 응답을 반환하지 않고
        # 명확한 HTTP 500 오류를 반환합니다.
        raise HTTPException(
            status_code=500,
            detail="대화 기록 저장 중 오류가 발생했습니다."
        )


    # ---------------------------------------------------------------
    # 사용자에게 결과 반환
    #
    # created_at을 ISO 형식으로 함께 반환하여
    # chat.html에서 메시지 timestamp를 표시할 수 있습니다.
    # ---------------------------------------------------------------
    return {
        "question": req.question,
        "response": ai_response,
        "time": chat_log.created_at.isoformat()
    }


# -------------------------------------------------------------------
# 4. 내 대화 기록 조회 API
#
# 현재 로그인한 사용자의 대화 기록만 조회합니다.
# -------------------------------------------------------------------
@app.get("/api/me/chats")
async def get_my_chats(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(
        auth.get_current_user
    )
):
    logs = (
        db.query(models.ChatLog)
        .filter(
            models.ChatLog.user_id
            == current_user.id
        )
        .order_by(
            models.ChatLog.created_at.asc()
        )
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
#
# 현재 로그인한 사용자의 기록만 삭제하며
# 다른 사용자의 대화 기록에는 영향을 주지 않습니다.
# -------------------------------------------------------------------
@app.delete("/api/me/chats")
async def delete_my_chats(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(
        auth.get_current_user
    )
):
    try:
        # -----------------------------------------------------------
        # 현재 로그인한 사용자의 대화 기록만 삭제
        #
        # current_user.id를 조건으로 사용하기 때문에
        # 다른 사용자의 ChatLog는 삭제되지 않습니다.
        # -----------------------------------------------------------
        deleted_count = (
            db.query(models.ChatLog)
            .filter(
                models.ChatLog.user_id
                == current_user.id
            )
            .delete(
                synchronize_session=False
            )
        )

        db.commit()


        # -----------------------------------------------------------
        # 삭제 성공 로그
        # -----------------------------------------------------------
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
        # -----------------------------------------------------------
        # 삭제 실패 시 rollback
        # -----------------------------------------------------------
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