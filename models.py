# DB 테이블 설계
# models.py: 사용자, 인증 정보 및 대화 기록을 저장하는 SQLite 데이터베이스 모델 정의

from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    ForeignKey
)
from sqlalchemy.orm import declarative_base, relationship


Base = declarative_base()


# -------------------------------------------------------------------
# 사용자 테이블
# -------------------------------------------------------------------
class User(Base):
    __tablename__ = "users"

    # 사용자 고유 식별자
    # Primary Key이므로 각 사용자마다 고유한 값이 자동 생성됨
    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    # 로그인 아이디
    #
    # unique=True:
    # 같은 username을 가진 사용자를 중복 생성할 수 없음
    #
    # nullable=False:
    # NULL username을 가진 사용자를 생성할 수 없음
    #
    # index=True:
    # 로그인 시 username 검색 성능 향상
    username = Column(
        String(50),
        unique=True,
        nullable=False,
        index=True
    )

    # 사용자의 실제 비밀번호가 아니라
    # PBKDF2-SHA256으로 해싱된 비밀번호를 저장
    hashed_password = Column(
        String(255),
        nullable=False
    )

    # 계정 생성 시각
    #
    # default=datetime.utcnow:
    # 생성 시 별도의 시간이 전달되지 않으면
    # 현재 UTC 시간을 자동으로 저장
    #
    # nullable=False:
    # 모든 사용자에게 생성 시각이 반드시 존재하도록 보장
    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    # User 1명 ↔ ChatLog 여러 개의 1:N 관계
    chats = relationship(
        "ChatLog",
        back_populates="owner"
    )


# -------------------------------------------------------------------
# 대화 기록 테이블
# -------------------------------------------------------------------
class ChatLog(Base):
    __tablename__ = "chat_logs"

    # 각 대화 기록의 고유 식별자
    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    # 이 대화가 어떤 사용자의 것인지 연결
    #
    # users.id를 Foreign Key로 참조
    # nullable=False이므로 소유자가 없는 대화는 저장할 수 없음
    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    # 사용자가 입력한 질문
    question = Column(
        Text,
        nullable=False
    )

    # AI가 생성한 응답
    response = Column(
        Text,
        nullable=False
    )

    # 대화 생성 시각
    #
    # UTC로 저장한 뒤 Frontend에서 KST로 변환하여 표시
    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    # ChatLog → 해당 대화의 User 객체 연결
    owner = relationship(
        "User",
        back_populates="chats"
    )