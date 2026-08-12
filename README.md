# 🤖 웹 기반 AI 챗봇 서비스 PoC (Term Project Prototype)

FastAPI와 Google Gemini API 기반으로 구현된 **사용자 인증, 대화 문맥 유지, 대화 이력 DB 저장을 지원하는 웹 AI 챗봇 서비스의 기능 검증용 프로토타입(PoC)**입니다.

팀 프로젝트 본격 착수 전, 백엔드 라우팅부터 DB 연동, 인증, AI API 호출 및 예외 처리까지의 전체 파이프라인이 유기적으로 동작함을 입증하기 위해 선제적으로 제작되었습니다.

> ⚠️ **현재 단계 안내**: 본 문서는 단일 작성자가 진행한 PoC 단계를 기술한 것입니다. 배포(외부 접속 URL), 브랜치 전략, PR 기반 협업, 팀원별 커밋 이력은 팀 본 프로젝트 착수 이후 별도로 진행/기록됩니다.

---

## 1. 프로젝트 개요 및 PoC 목적

- **개발 목적**: 팀원들과의 역할 분담 및 본격 개발에 앞서, **Linux + Web (FastAPI) + DB (SQLite) + AI API (Gemini)** 통합 파이프라인의 핵심 기술 요소를 미리 구현하고 검증
- **타겟 사용자**: 개인화된 대화 기록을 보관하고 연속성 있는 AI 대화를 진행하고자 하는 웹 사용자
- **핵심 기능**:
  1. PBKDF2 암호화 및 JWT 기반의 회원가입/로그인 인증
  2. 인증 상태(JWT Token)에 따른 페이지 라우팅 및 접근 제어 (`/chat` 보호)
  3. Google GenAI SDK 기반 AI API 연동 및 최근 3개 대화 기반 Context 구성
  4. 질문/응답의 DB (`chat_logs`) 자동 축적 및 사용자별 이력 조회
  5. 서버 사이드 로깅, 하드 타임아웃(5초) 및 재시도(retry) 처리로 AI 호출 지연/실패 시 시스템 비정상 종료 방지

---

## 2. 프로토타입 제작 단계 (Development Steps)

이 프로토타입은 아래 5단계에 걸쳐 순차적으로 구축되었습니다.

### Step 1. 개발 환경 설정 및 DB ORM 구축

- Python 가상환경(`.venv`) 구성 및 필수 패키지(`fastapi`, `uvicorn`, `sqlalchemy`, `google-genai`, `python-jose`, `passlib` 등) 설치
- `database.py`에 SQLAlchemy 엔진과 세션 관리 로직 작성
- `models.py`에 사용자 테이블(`User`)과 대화 로그 테이블(`ChatLog`) 1:N 관계 정의

### Step 2. 인증 모듈 및 보안 체계 구현

- `auth.py` 작성: 비밀번호 저장 시 `passlib`의 PBKDF2 해싱 적용
- JWT Access Token 발급(`create_access_token`) 및 API 요청 헤더 토큰 검증 함수(`get_current_user`) 작성
- 환경 변수(`.env`) 기반 `SECRET_KEY` 및 API 키 격리 관리 체계 구축 (`.gitignore` 적용)

### Step 3. 다중 페이지(Multi-Page) UI 및 라우터 설계

- 단일 파일 구조에서 가독성 및 팀 협업 효율을 높이기 위해 HTML 템플릿 분리
  - `templates/login.html`: 로그인 화면
  - `templates/register.html`: 회원가입 화면
  - `templates/chat.html`: 챗봇 메인 대화 화면 (클라이언트 측에서 토큰 부재 시 `/login`으로 리다이렉트)
- `main.py`에 HTML 페이지 렌더링 라우터(`GET /`, `/login`, `/register`, `/chat`)와 비즈니스 REST API 분리 구현

### Step 4. AI API 연동 및 문맥(Context) 구성

- `ai_service.py` 작성: `google-genai` SDK의 비동기 클라이언트(`client.aio.models.generate_content`) 연동, `gemini-3.6-flash` 모델 사용
- DB에서 해당 사용자의 최근 3개 대화 기록을 추출해 모델에 전달하는 Prompt Context 구성 로직 구현
- 클라이언트측 API 키 노출 방지를 위해 모든 AI 호출은 백엔드 서버에서 수행하도록 격리

### Step 5. 타임아웃, 예외 처리 및 로깅 작성

- `asyncio.wait_for`로 AI API 호출에 **5초 하드 타임아웃(`TIMEOUT_SECONDS`)**을 적용해, 응답이 지연되는 상황에서도 서버가 무한 대기하지 않도록 처리
- 타임아웃 및 재시도 가능한 오류(503 UNAVAILABLE, 429 RESOURCE_EXHAUSTED)에 대해 최대 3회 지수적 백오프(exponential backoff) 재시도를 적용하고, 최종 실패 시 서버가 다운되지 않고 클라이언트에 안내 에러 메시지를 반환하도록 예외 포착(`try-except`) 처리
- 요청 수신, AI 호출 시작/성공/실패(타임아웃 포함), DB 저장 유무를 기록하는 서버 로깅(`logging`, `app_logger`) 추가
- `GET /api/me/chats` 이력 조회 API 완성

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
├──── AI Service (ai_service.py) ─── Google GenAI SDK (gemini-3.6-flash), 5s hard timeout
└──── Database Layer (database.py) ─ SQLAlchemy ORM
        │
        ▼
[ SQLite DB (chatbot.db) ]
```

### 3.2 주요 컴포넌트 역할

| 파일명             | 역할 및 주요 기능                                             |
| --------------- | ------------------------------------------------------ |
| `main.py`       | FastAPI 앱 엔트리포인트, HTML 라우터, REST API 엔드포인트, 로깅         |
| `auth.py`       | PBKDF2 해싱, JWT 토큰 생성 및 토큰 검증 미들웨어 (`get_current_user`) |
| `ai_service.py` | Google GenAI SDK 연동, 최근 대화 맥락(Context) 구성, 하드 타임아웃 및 재시도/예외 처리 |
| `database.py`   | SQLite DB 엔진 연결 및 세션 관리 (`get_db`, `init_db`)          |
| `models.py`     | SQLAlchemy ORM 스키마 정의 (`User`, `ChatLog`)              |
| `templates/`    | 프론트엔드 UI (`login.html`, `register.html`, `chat.html`)  |

---

## 4. API 명세서

### 4.1 인증 API

#### 1) 회원가입 (`POST /api/auth/register`)

- **Request Body:**

```json
{
  "username": "testuser",
  "password": "password123"
}
```

- **Response (201 Created):**

```json
{
  "message": "회원가입 완료"
}
```

#### 2) 로그인 (`POST /api/auth/login`)

- **Request Body:**

```json
{
  "username": "testuser",
  "password": "password123"
}
```

- **Response (200 OK):**

```json
{
  "access_token": "eyJhbGciOiJIUzI1Ni...",
  "token_type": "bearer"
}
```

---

### 4.2 AI 챗봇 및 대화 이력 API (인증 필요)

- **Common Header:** `Authorization: Bearer <access_token>`

#### 1) 챗봇 질문 전송 (`POST /api/chat`)

- **Request Body (Pydantic 검증 적용, 1~500자):**

```json
{
  "question": "FastAPI의 장점이 뭐야?"
}
```

- **Response (200 OK):**

```json
{
  "question": "FastAPI의 장점이 뭐야?",
  "response": "FastAPI는 비동기 처리 지원, Pydantic 기반 입력 검증, 빠른 실행 속도가 장점입니다."
}
```

- **Response (지연/오류 시, 200 OK 내 안내 메시지):**

```json
{
  "question": "긴 글 요약해줘",
  "response": "현재 응답이 지연되고 있어요. 잠시 후 다시 시도해 주세요. (error: AI_TIMEOUT)"
}
```

#### 2) 내 대화 이력 조회 (`GET /api/me/chats`)

- **Response (200 OK):**

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

```
SECRET_KEY=your_secret_key_here
ALGORITHM=HS256
GEMINI_API_KEY=your_gemini_api_key_here
```

### `.gitignore` 설정 내역

```
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

> ⚠️ 현재는 로컬 실행 환경만 검증되었습니다. 외부 네트워크에서 접속 가능한 배포 URL은 팀 프로젝트 배포 단계에서 추가될 예정입니다.

---

## 8. 대화 로그 확인 가이드

현재 대화 로그는 아래 방법으로 확인할 수 있습니다.

### 8.1 서버 로깅 예시

```
INFO:app_logger:request_received user_id=2 question=hi
INFO:uvicorn.error:ai_call_start prompt_length=2
INFO:uvicorn.error:ai_call_success
INFO:app_logger:db_save_success user_id=2 chat_id=12
INFO: 127.0.0.1:52151 - "POST /api/chat HTTP/1.1" 200 OK
```

### 8.2 API를 통한 로그 조회

인증 토큰으로 `GET /api/me/chats`를 호출하면 로그인한 사용자 기준의 전체 대화 이력(질문/응답/시간)을 JSON으로 확인할 수 있습니다.

```bash
curl -H "Authorization: Bearer <access_token>" http://127.0.0.1:8000/api/me/chats
```

---

## 9. 팀 협업 및 역할 분담 계획 (Team Roadmap)

본 프로토타입을 프로젝트 베이스라인으로 활용하여 진행할 **예정**인 팀원별 분담 영역입니다. (아래 항목은 실적이 아닌 계획이며, 실제 브랜치 전략·PR 이력·팀원별 커밋은 팀 프로젝트 착수 후 별도로 기록됩니다.)

| 구분                 | 담당 영역          | 예정 작업 내용                                           |
| ------------------ | -------------- | -------------------------------------------------- |
| **팀원 A (PoC 작성자)** | 시스템 아키텍처 & 백엔드 | 프로토타입 구축, 핵심 API 라우팅, DB ORM 연동 및 전체 아키텍처 수립       |
| **팀원 B**           | AI 연동 & 예외 처리  | Prompt 커스텀 기능 추가, 재시도/백오프 전략 고도화, 타임아웃 임계값 튜닝    |
| **팀원 C**           | 인증 & 보안        | JWT Refresh Token 도입, 토큰 만료 예외 처리, 비정상 접근 차단 보안 강화 |
| **팀원 D**           | 프론트엔드 UI/UX    | UI 스타일링 개선, 대화 로딩 애니메이션 추가, 반응형 웹 디자인 적용           |

---

## 10. 팀 브랜치 전략 및 Git 워크플로우 (Git Flow Strategy)

본 프로젝트는 안정적인 메인 코드 관리와 팀원 간 작업 충돌 방지를 위해 **Git Flow에 준하는 브랜치 전략을 채택할 예정입니다.** 모든 기능 개발은 작업 브랜치에서 진행하며, **PR(Pull Request) 검토 후 `develop` 브랜치로 머지**하는 것을 원칙으로 합니다.

> ⚠️ 현재는 PoC 단계로 `main` 브랜치만 존재합니다. 아래 구조는 팀 프로젝트 착수 시점부터 적용됩니다.

```text
main (최종 배포용)
  │
  └── develop (기능 개발 통합용)
        ├── feat/auth (인증/보안 - 팀원 C)
        ├── feat/ai-retry-tuning (재시도/백오프 전략 고도화 - 팀원 B)
        └── feat/ui-redesign (프론트엔드 - 팀원 D)
```

### 10.1 브랜치 구조 및 역할

| 브랜치 명칭 | 역할 및 사용 목적 | 머지 조건 |
| --- | --- | --- |
| `main` | 외부 배포가 가능한 최신 상태의 프로덕션 브랜치 | 최종 검증 후 머지 |
| `develop` | 팀원들의 기능 개발 결과물이 하나로 합쳐지는 통합 브랜치 | PR 승인 후 머지 |
| `feat/<기능명>` | 각 팀원이 담당 기능을 개발하는 기능 단위 작업 브랜치 | `develop` 방향으로 PR 작성 |
| `fix/<버그명>` | 긴급 버그 수정 작업 브랜치 | `develop` 방향으로 PR 작성 |

### 10.2 팀 협업 규칙 (Git Rules)

1. **직접 Commit 금지**: `main` 및 `develop` 브랜치에 직접 커밋 및 푸시하는 것을 금지합니다.
2. **작업 브랜치 생성**: 기능 개발 시 항상 `develop` 브랜치에서 새로운 작업 브랜치를 생성합니다.

```bash
git checkout develop
git pull origin develop
git checkout -b feat/login-ui
```

3. **PR 기반 Merge**: 기능 구현 완료 후 GitHub에서 `develop` 브랜치로 PR을 작성하고, 팀원 코드 리뷰를 거친 후 머지합니다.
4. **커밋 단위 세분화**: 기능을 작은 단위로 나누어 커밋함으로써 변경 이력 추적과 코드 리뷰를 쉽게 합니다. 이 원칙을 따르면 팀원별 커밋도 자연히 여러 건 누적됩니다.

---

## 11. 남은 작업 (본 프로젝트 착수 시 필수)

- [ ] 외부 네트워크에서 접속 가능한 서비스 배포 (배포 URL 확보)
- [ ] `main`/`develop` 브랜치 분리 및 기능 단위 작업 브랜치 운영
- [ ] PR 기반 Merge 워크플로우 적용
- [ ] 팀원별 유의미한 커밋 10회 이상 기록
- [x] AI 호출에 대한 명시적 하드 타임아웃 적용 (`asyncio.wait_for`, 5초)