# DB 테이블 설계
# database.py: 사용자 식별, 생성 시각, 질문, 응답을 저장하는 SQLite 데이터베이스를 구축
# 로컬에서는 ./chatbot.db를 사용하고,
# 배포 환경에서는 DATABASE_URL 환경 변수를 통해 DB 경로를 설정

import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import Base


# -------------------------------------------------------------------
# Database URL 설정
#
# 로컬 환경:
#   DATABASE_URL 환경 변수가 없으면 기존과 동일하게
#   ./chatbot.db 파일을 사용
#
# Railway 배포 환경:
#   DATABASE_URL=sqlite:////data/chatbot.db
#   Persistent Volume에 DB 파일 저장
# -------------------------------------------------------------------
SQLALCHEMY_DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./chatbot.db"
)


# -------------------------------------------------------------------
# SQLAlchemy Engine 생성
#
# SQLite는 기본적으로 생성된 스레드 외부에서
# 같은 DB 연결을 사용하는 것을 제한하기 때문에
# FastAPI 환경에서는 check_same_thread=False를 적용
# -------------------------------------------------------------------
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)


# -------------------------------------------------------------------
# DB Session 생성
# -------------------------------------------------------------------
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


# -------------------------------------------------------------------
# DB 테이블 초기화
# -------------------------------------------------------------------
def init_db():
    Base.metadata.create_all(bind=engine)


# -------------------------------------------------------------------
# FastAPI Dependency용 DB Session 관리
#
# 요청 처리 중 Session을 제공하고,
# 요청이 끝나면 반드시 close()
# -------------------------------------------------------------------
def get_db():
    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()