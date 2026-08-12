# 🤖 웹 기반 AI 챗봇 서비스 PoC (Term Project Prototype)

FastAPI와 Google Gemini API 기반으로 구현된 **사용자 인증, 대화 문맥 유지, 대화 이력 DB 저장을 지원하는 웹 AI 챗봇 서비스의 기능 검증용 프로토타입(PoC)**입니다. 

팀 프로젝트 본격 착수 전, 백엔드 라우팅부터 DB 연동, 인증, AI API 호출 및 예외 처리까지의 전체 파이프라인이 유기적으로 동작함을 입증하기 위해 선제적으로 제작되었습니다.

---

## 1. 프로젝트 개요 및 PoC 목적

* **개발 목적**: 팀원들과의 역할 분담 및 본격 개발에 앞서, **Linux + Web (FastAPI) + DB (SQLite) + AI API (Gemini)** 통합 파이프라인의 핵심 기술 요소를 미리 구현하고 검증
* **타겟 사용자**: 개인화된 대화 기록을 보관하고 연속성 있는 AI 대화를 진행하고자 하는 웹 사용자
* **핵심 기능**:
  1. PBKDF2 암호화 및 JWT 기반의 회원가입/로그인 인증
  2. 인증 상태(JWT Token)에 따른 페이지 라우팅 및 접근 제어 (`/chat` 보호)
  3. Google GenAI SDK 기반 AI API 연동 및 최근 3개 대화 기반 Context 구성
  4. 질문/응답의 DB (`chat_logs`) 자동 축적 및 사용자별 이력 조회
  5. 서버 사이드 로깅, 타임아웃, 예외 처리로 시스템 비정상 종료 방지

---

## 2. 프로토타입 제작 단계 (Development Steps)

이 프로토타입은 아래 5단계에 걸쳐 순차적으로 구축되었습니다.

### Step 1. 개발 환경 설정 및 DB ORM 구축
* Python 가상환경(`.venv`) 구성 및 필수 패키지(`fastapi`, `uvicorn`, `sqlalchemy`, `google-genai`, `python-jose`, `passlib` 등) 설치
* `database.py`에 SQLAlchemy 엔진과 세션 관리 로직 작성
* `models.py`에 사용자 테이블(`User`)과 대화 로그 테이블(`ChatLog`) 1:N 관계 정의

### Step 2. 인증 모듈 및 보안 체계 구현
* `auth.py` 작성: 비밀번호 저장 시 `passlib`의 PBKDF2 해싱 적용
* JWT Access Token 발급(`create_access_token`) 및 API 요청 헤더 토큰 검증 함수(`get_current_user`) 작성
* 환경 변수(`.env`) 기반 `SECRET_KEY` 및 API 키 격리 관리 체계 구축 (`.gitignore` 적용)

### Step 3. 다중 페이지(Multi-Page) UI 및 라우터 설계
* 단일 파일 구조에서 가독성 및 팀 협업 효율을 높이기 위해 HTML 템플릿 분리
  * `templates/login.html`: 로그인 화면
  * `templates/register.html`: 회원가입 화면
  * `templates/chat.html`: 챗봇 메인 대화 화면
* `main.py`에 HTML 페이지 렌더링 라우터(`GET /`, `/login`, `/register`, `/chat`)와 비즈니스 REST API 분리 구현

### Step 4. AI API 연동 및 문맥(Context) 구성
* `ai_service.py` 작성: `google-genai` SDK의 비동기 클라이언트(`client.aio.models.generate_content`) 연동
* DB에서 해당 사용자의 최근 3개 대화 기록을 추출해 `gemini-1.5-flash` 모델에 전달하는 Prompt Context 구성 로직 구현
* 클라이언트측 API 키 노출 방지를 위해 모든 AI 호출은 백엔드 서버에서 수행하도록 격리

### Step 5. 예외 처리, 로깅 및 DB 검증 스크립트 작성
* API 타임아웃 및 호출 실패 시 서버가 다운되지 않고 클라이언트에 안내 에러 메시지를 반환하도록 예외 포착(`try-except`) 처리
* 요청 수신, AI 호출 시작/성공, DB 저장 유무를 기록하는 서버 로깅(`logging`, `app_logger`) 추가
* 데이터 검증용 SQL 스크립트(`scripts/check_logs.sql`) 및 `GET /api/me/chats` 이력 조회 API 완성

---

## 3. 시스템 아키텍처 및 구성 요소

### 3.1 아키텍처 구조

```
[ Client (Browser) ]
        │
        │ (1) HTML/JS Page Request (/login, /register, /chat)
        │ (2) REST API Request + JWT Authorization Header
        ▼
[ FastAPI Server (main.py) ]
├──── Auth Module (auth.py) ──────── Password Hash (PBKDF2) & JWT Verification
├──── Input Validation (Pydantic) ── Length limit & Empty check
├──── AI Service (ai_service.py) ─── Google GenAI SDK (gemini-1.5-flash)
└──── Database Layer (database.py) ─ SQLAlchemy ORM
        │
        ▼
[ SQLite DB (app.db) ]
```

### 3.2 주요 컴포넌트 역할

| 파일명 | 역할 및 주요 기능 |
| :--- | :--- |
| `main.py` | FastAPI 앱 엔트리포인트, HTML 라우터, REST API 엔드포인트, 로깅 |
| `auth.py` | PBKDF2 해싱, JWT 토큰 생성 및 토큰 검증 미들웨어 (`get_current_user`) |
| `ai_service.py` | Google GenAI SDK 연동, 최근 대화 맥락(Context) 구성 및 예외 처리 |
| `database.py` | SQLite DB 엔진 연결 및 세션 관리 (`get_db`, `init_db`) |
| `models.py` | SQLAlchemy ORM 스키마 정의 (`User`, `ChatLog`) |
| `templates/` | 프론트엔드 UI (`login.html`, `register.html`, `chat.html`) |
| `scripts/` | DB 데이터 검증용 SQL 스크립트 (`check_logs.sql`) |

---

## 4. API 명세서

### 4.1 인증 API

#### 1) 회원가입 (`POST /api/auth/register`)

* **Request Body:**
```json
{
  "username": "testuser",
  "password": "password123"
}
```

* **Response (201 Created):**
```json
{
  "message": "회원가입 완료"
}
```

#### 2) 로그인 (`POST /api/auth/login`)

* **Request Body:**
```json
{
  "username": "testuser",
  "password": "password123"
}
```

* **Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1Ni...",
  "token_type": "bearer"
}
```

---

### 4.2 AI 챗봇 및 대화 이력 API (인증 필요)

* **Common Header:** `Authorization: Bearer <access_token>`

#### 1) 챗봇 질문 전송 (`POST /api/chat`)

* **Request Body (Pydantic 검증 적용):**
```json
{
  "question": "FastAPI의 장점이 뭐야?"
}
```

* **Response (200 OK):**
```json
{
  "question": "FastAPI의 장점이 뭐야?",
  "response": "FastAPI는 비동기 처리 지원, Pydantic 기반 입력 검증, 빠른 실행 속도가 장점입니다."
}
```

#### 2) 내 대화 이력 조회 (`GET /api/me/chats`)

* **Response (200 OK):**
```json
[
  {
    "id": 1,
    "question": "FastAPI의 장점이 뭐야?",
    "response": "FastAPI는 비동기 처리 지원...",
    "time": "2026-08-12T17:30:00"
  }
]
```

---

## 5. 데이터베이스 구조 (Database Schema)

SQLite 기반 ORM 구조이며, `User`와 `ChatLog` 간 1:N 관계입니다.

```
+--------------------+       1 : N       +--------------------+
|       Users        | ----------------> |      ChatLogs      |
+--------------------+                   +--------------------+
| id (PK, Integer)   |                   | id (PK, Integer)   |
| username (String)  |                   | user_id (FK, Int)  |
| hashed_password    |                   | question (Text)    |
| created_at         |                   | response (Text)    |
+--------------------+                   | created_at         |
                                          +--------------------+
```

---

## 6. 환경 변수 및 민감정보 관리

API 키 및 JWT 암호화 키 등 민감정보는 `.env` 파일로 관리하며, `.gitignore`를 통해 Git 추적 대상에서 완전히 제외됩니다.

### `.env.example`

```env
SECRET_KEY=your_secret_key_here
ALGORITHM=HS256
GEMINI_API_KEY=your_gemini_api_key_here
```

### `.gitignore` 설정 내역

```gitignore
# 환경 변수 파일
.env

# 데이터베이스 파일
*.db
*.sqlite3

# 파이썬 가상환경 및 캐시
.venv/
venv/
env/
__pycache__/
*.py[cod]

# OS 생성 임시 파일
.DS_Store
```

---

## 7. 로컬 실행 가이드

1. **저장소 클론:**
```bash
git clone https://github.com/bangahee/term-project-proto.git
cd term-project-proto
```

2. **가상환경 생성 및 패키지 설치:**
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

3. **환경 변수 설정:**
```bash
cp .env.example .env
# .env 파일에서 실제 GEMINI_API_KEY 및 SECRET_KEY 입력
```

4. **FastAPI 서버 실행:**
```bash
uvicorn main:app --reload
```

5. **브라우저 접속:** `http://127.0.0.1:8000`

---

## 8. DB 검증 및 로그 확인 가이드

### 8.1 서버 로깅 예시

```text
INFO:app_logger:request_received user_id=2 question=hi
INFO:uvicorn.error:ai_call_start prompt_length=2
INFO:uvicorn.error:ai_call_success
INFO:app_logger:db_save_success user_id=2 chat_id=12
INFO: 127.0.0.1:52151 - "POST /api/chat HTTP/1.1" 200 OK
```

### 8.2 DB 검증 SQL 실행

`scripts/check_logs.sql`을 실행하여 저장된 대화 로그를 직접 조회할 수 있습니다.

```bash
sqlite3 app.db < scripts/check_logs.sql
```

---

## 9. 팀 협업 및 역할 분담 계획 (Team Roadmap)

본 프로토타입을 프로젝트 베이스라인으로 활용하여 진행할 팀원별 분담 영역입니다.

| 구분 | 담당 영역 | 예정 작업 내용 |
| --- | --- | --- |
| **팀원 A (PoC 작성자)** | 시스템 아키텍처 & 백엔드 | 프로토타입 구축, 핵심 API 라우팅, DB ORM 연동 및 전체 아키텍처 수립 |
| **팀원 B** | AI 연동 & 예외 처리 | AI 모델 파라미터 튜닝, Prompt 커스텀 기능 추가, 타임아웃/오류 처리 고도화 |
| **팀원 C** | 인증 & 보안 | JWT Refresh Token 도입, 토큰 만료 예외 처리, 비정상 접근 차단 보안 강화 |
| **팀원 D** | 프론트엔드 UI/UX | UI 스타일링 개선, 대화 로딩 애니메이션 추가, 반응형 웹 디자인 적용 |