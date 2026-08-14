# 🤖 웹 기반 AI 챗봇 서비스 PoC (Term Project Prototype)

FastAPI와 Google Gemini API를 기반으로 구현한 **사용자 인증, 대화 문맥 유지, 대화 이력 DB 저장, AI API 예외 처리 및 외부 배포를 지원하는 웹 기반 AI 챗봇 서비스 프로토타입(PoC)**입니다.

팀 프로젝트 본격 착수 전, 다음 전체 서비스 파이프라인이 실제 환경에서 정상적으로 연결되고 동작하는지 검증하기 위해 선제적으로 제작했습니다.

```text
Web UI
→ FastAPI Backend
→ JWT Authentication
→ Input Validation
→ Conversation Context
→ Google Gemini API
→ AI Response
→ SQLite DB
→ User-specific Chat History
→ Railway Deployment
```

현재 PoC는 로컬 환경뿐 아니라 **Railway를 통한 외부 네트워크 배포까지 완료**했으며, 인증, AI 호출, DB 저장, 사용자별 로그 조회, 입력 검증, 예외 처리, DB 영속성 및 안전한 DOM 렌더링을 배포 환경에서 검증했습니다.

> ⚠️ **현재 단계 안내**
>
> 본 저장소는 단일 작성자가 구현한 기술 검증용 PoC입니다.
>
> 서비스 배포와 핵심 기능 검증은 완료했지만, `main` / `develop` 브랜치 운영, 기능 브랜치, PR 기반 Merge, 팀원별 유의미한 커밋 10회 이상 등의 **팀 협업 요구사항은 아직 완료된 것으로 간주하지 않습니다.**
>
> 해당 항목은 팀 본 프로젝트에서 실제 Git 이력과 함께 적용할 예정입니다.

---

# 1. 프로젝트 개요

## 1.1 개발 목적

본 프로젝트의 목적은 개별 기술을 단순히 구현하는 것이 아니라 다음 기술 요소를 하나의 실제 웹 서비스로 연결하는 것입니다.

- **Backend**: FastAPI
- **Frontend**: HTML / CSS / JavaScript + Jinja2
- **Database**: SQLite + SQLAlchemy ORM
- **Authentication**: JWT + PBKDF2 Password Hashing
- **AI API**: Google Gemini API (`google-genai`)
- **Deployment**: Railway
- **Configuration**: Environment Variables / `.env`
- **Persistence**: Railway Volume + SQLite

전체 처리 흐름은 다음과 같습니다.

```text
사용자
  ↓
회원가입 / 로그인
  ↓
JWT 발급
  ↓
질문 입력
  ↓
FastAPI
  ↓
입력 검증
  ↓
JWT 사용자 인증
  ↓
최근 대화 Context 조회
  ↓
Gemini API 호출
  ↓
Timeout / Retry / Exception Handling
  ↓
AI 응답
  ↓
SQLite DB 저장
  ↓
사용자별 대화 이력 조회
  ↓
웹 화면 출력
```

---

## 1.2 타겟 사용자

로그인 후 개인별 대화 기록을 보관하면서 이전 대화를 바탕으로 연속성 있는 AI 대화를 진행하고자 하는 웹 사용자입니다.

---

## 1.3 핵심 기능

1. 회원가입 및 로그인
2. PBKDF2 기반 비밀번호 해싱
3. JWT Access Token 기반 사용자 인증
4. 로그인 사용자 전용 챗봇 API
5. 사용자별 대화 이력 접근 제어
6. Google Gemini API 서버 사이드 연동
7. 최근 3개 대화를 활용한 Context 구성
8. 질문/응답 SQLite DB 누적 저장
9. 사용자 기준 대화 이력 조회
10. 공백 입력 및 500자 초과 입력 검증
11. AI API 5초 하드 타임아웃
12. 최대 3회 AI 호출 시도
13. Exponential Backoff 기반 재시도
14. AI API 실패 시 사용자 오류 안내
15. DB 저장 실패 시 `rollback()`
16. 주요 처리 단계 서버 로깅
17. UUID 기반 `request_id` 요청 추적
18. 사용자 질문 원문을 서버 요청 로그에서 제외
19. `textContent` 기반 안전한 DOM 렌더링
20. Railway 외부 배포
21. Railway Volume을 통한 SQLite DB 영속성 확보
22. 재배포 이후 사용자 및 대화 기록 유지 검증

---

# 2. 배포 서비스

## 2.1 외부 접속 URL

현재 서비스는 Railway에 배포되어 있으며 외부 네트워크에서 접근할 수 있습니다.

**배포 URL**

```text
https://term-project-proto-production.up.railway.app
```

평가자는 위 URL을 통해 회원가입 → 로그인 → 챗봇 질문 → 대화 이력 확인의 전체 흐름을 직접 확인할 수 있습니다.

---

## 2.2 배포 구조

```text
┌─────────────────────────────┐
│       Client Browser        │
│                             │
│ HTML / CSS / JavaScript     │
└──────────────┬──────────────┘
               │
               │ HTTPS
               ▼
┌─────────────────────────────┐
│           Railway           │
│                             │
│       FastAPI / Uvicorn     │
└──────────────┬──────────────┘
               │
       ┌───────┴────────┐
       │                │
       ▼                ▼
┌──────────────┐   ┌──────────────────┐
│ Gemini API   │   │ Railway Volume   │
│              │   │                  │
│ AI Response  │   │ SQLite DB        │
└──────────────┘   │ chatbot.db       │
                   └──────────────────┘
```

Railway 서비스의 컨테이너가 재배포되더라도 SQLite 데이터가 사라지지 않도록 영속 Volume을 사용합니다.

---

# 3. 프로토타입 개발 과정

## Step 1. 개발 환경 및 DB ORM 구축

- Python 가상환경 `.venv` 구성
- FastAPI / Uvicorn 설치
- SQLAlchemy ORM 구성
- SQLite DB 연결
- `User`, `ChatLog` 모델 작성
- User : ChatLog = 1 : N 관계 구성

---

## Step 2. 사용자 인증

`auth.py`에서 다음 기능을 구현했습니다.

- PBKDF2 비밀번호 해싱
- 비밀번호 검증
- JWT Access Token 생성
- JWT 검증
- JWT에서 현재 사용자 조회

로그인 성공 시 서버가 JWT를 발급합니다.

```text
username + password
        ↓
사용자 조회
        ↓
PBKDF2 비밀번호 검증
        ↓
JWT Access Token 생성
        ↓
Browser 저장
```

---

## Step 3. Web UI 및 FastAPI Routing

HTML 템플릿은 다음과 같이 분리했습니다.

```text
templates/
├── login.html
├── register.html
└── chat.html
```

HTML 페이지 라우트:

```text
GET /
GET /login
GET /register
GET /chat
```

API:

```text
POST /api/auth/register
POST /api/auth/login
POST /api/chat
GET  /api/me/chats
```

---

## Step 4. Gemini API 연동

`ai_service.py`에서 Google GenAI SDK의 비동기 API를 사용합니다.

```python
client.aio.models.generate_content(...)
```

현재 설정된 Gemini 모델을 서버에서 호출하며 API Key는 브라우저에 전달하지 않습니다.

```text
Browser
   ↓
FastAPI
   ↓
GEMINI_API_KEY
   ↓
Google Gemini API
   ↓
FastAPI
   ↓
Browser
```

따라서 사용자가 브라우저에서 Gemini API Key를 직접 확인할 수 없습니다.

---

## Step 5. 대화 Context 구성

로그인 사용자의 최근 3개 대화를 DB에서 조회합니다.

```text
ChatLog
   ↓
현재 user_id 조건
   ↓
created_at DESC
   ↓
LIMIT 3
```

이후 AI에 전달할 때는 다시 과거 → 최신 순서로 구성합니다.

```text
이전 User 질문
→ 이전 AI 응답
→ 다음 User 질문
→ 다음 AI 응답
→ 현재 User 질문
```

이를 통해 전체 대화 기록을 AI에 계속 전달하지 않으면서 최근 대화의 문맥을 유지합니다.

---

## Step 6. AI Timeout

AI API가 응답하지 않는 상황에서 서버가 무한 대기하지 않도록 `asyncio.wait_for()`를 사용합니다.

```text
TIMEOUT_SECONDS = 5.0
```

처리 구조:

```text
Gemini API
    ↓
asyncio.wait_for()
    ↓
5초 이내 응답?
 ┌──┴───┐
Yes     No
 │       │
응답    Timeout
         ↓
       Retry
```

---

## Step 7. Retry 및 Exponential Backoff

일시적인 API 장애에 대응하기 위해 최대 3회의 호출을 시도합니다.

재시도 대상에는 다음과 같은 상황이 포함됩니다.

- Timeout
- `429 RESOURCE_EXHAUSTED`
- `503 UNAVAILABLE`

Backoff 구조:

```text
1차 호출
   ↓
실패
   ↓
2초 대기
   ↓
2차 호출
   ↓
실패
   ↓
4초 대기
   ↓
3차 호출
   ↓
실패
   ↓
사용자 오류 안내
```

이를 통해 일시적인 Gemini API 장애가 발생하더라도 FastAPI 서버 자체가 종료되지 않습니다.

---

## Step 8. DB 저장 및 Rollback

AI 응답을 받은 후 사용자 질문과 응답을 `ChatLog`에 저장합니다.

```text
AI 응답
   ↓
ChatLog 생성
   ↓
db.add()
   ↓
db.commit()
```

DB 저장 중 오류가 발생하면:

```python
db.rollback()
```

을 실행하여 실패한 트랜잭션 상태를 정리합니다.

---

## Step 9. request_id 기반 로그 추적

각 `/api/chat` 요청에는 UUID 기반 `request_id`가 생성됩니다.

```text
POST /api/chat
      ↓
request_id 생성
      ↓
request_received
      ↓
ai_call_start
      ↓
ai_call_success / ai_call_failed
      ↓
db_save_success / db_save_failed
```

하나의 사용자 요청에서 발생한 로그에는 동일한 `request_id`가 사용됩니다.

예:

```text
request_received request_id=b67c61c2-... user_id=1 question_length=2
ai_call_start request_id=b67c61c2-... prompt_length=2 context_count=3
ai_call_success request_id=b67c61c2-... attempt=1
db_save_success request_id=b67c61c2-... user_id=1 chat_id=4
```

따라서 동시에 여러 요청이 발생해도 하나의 요청 처리 흐름을 추적할 수 있습니다.

또한 서버 요청 로그에는 질문 원문을 기록하지 않고 다음 정보만 기록합니다.

```text
request_id
user_id
question_length
```

---

## Step 10. 안전한 DOM 렌더링

`chat.html`에서는 사용자 질문과 AI 응답을 출력할 때 외부 문자열을 `innerHTML`로 삽입하지 않습니다.

DOM Element를 생성하고 `textContent`를 사용합니다.

```javascript
messageText.textContent = String(message ?? '');
```

따라서 다음과 같은 입력:

```html
<h1>TEST</h1>
```

은 실제 HTML 제목으로 렌더링되지 않고 문자 그대로 표시됩니다.

다음 입력:

```html
<img src=x onerror="alert('test')">
```

역시 실제 `<img>` 요소로 생성되지 않으며 `onerror` JavaScript가 실행되지 않습니다.

이 동작은 Railway 배포 환경에서도 직접 검증했습니다.

---

# 4. 시스템 아키텍처

```text
┌──────────────────────────────┐
│        Client Browser        │
│                              │
│ HTML / CSS / JavaScript      │
│ login / register / chat      │
└──────────────┬───────────────┘
               │
               │ HTTPS / REST API
               │ Authorization: Bearer <JWT>
               ▼
┌──────────────────────────────┐
│        FastAPI Server        │
│           main.py            │
│                              │
│ - Routing                    │
│ - Pydantic Validation        │
│ - JWT Authentication         │
│ - request_id                 │
│ - Server Logging             │
└───────┬─────────────┬────────┘
        │             │
        ▼             ▼
┌──────────────┐ ┌─────────────────────┐
│   auth.py    │ │    ai_service.py    │
│              │ │                     │
│ - PBKDF2     │ │ - Context           │
│ - JWT        │ │ - Gemini API        │
│              │ │ - Timeout           │
│              │ │ - Retry / Backoff   │
└──────────────┘ └──────────┬──────────┘
                            │
                            ▼
                  ┌─────────────────────┐
                  │ Google Gemini API   │
                  └─────────────────────┘

        FastAPI
           │
           ▼
┌──────────────────────────────┐
│ database.py + models.py      │
│ SQLAlchemy ORM               │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│ SQLite Database              │
│ Users / ChatLogs             │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│ Railway Persistent Volume    │
└──────────────────────────────┘
```

---

# 5. 주요 컴포넌트

| 파일 / 디렉터리 | 역할 |
| --- | --- |
| `main.py` | FastAPI 앱, 페이지/API 라우팅, 입력 검증, JWT 인증 연결, request_id 생성, DB 저장, 서버 로깅 |
| `auth.py` | PBKDF2 비밀번호 해싱, JWT 생성 및 인증 사용자 조회 |
| `ai_service.py` | Gemini API, Context 구성, Timeout, Retry, Exponential Backoff, AI 예외 처리 |
| `database.py` | SQLite / SQLAlchemy 엔진 및 DB 세션 관리 |
| `models.py` | `User`, `ChatLog` ORM 모델 |
| `templates/login.html` | 로그인 UI |
| `templates/register.html` | 회원가입 UI |
| `templates/chat.html` | 챗봇 UI, 대화 이력 출력, 안전한 DOM 렌더링 |
| `tests/` | 입력 검증 자동화 테스트 |

---

# 6. API 명세

## 6.1 회원가입

### `POST /api/auth/register`

Request:

```json
{
  "username": "testuser",
  "password": "password123"
}
```

Response:

```text
201 Created
```

```json
{
  "message": "회원가입 완료"
}
```

중복 사용자명:

```text
400 Bad Request
```

---

## 6.2 로그인

### `POST /api/auth/login`

Request:

```json
{
  "username": "testuser",
  "password": "password123"
}
```

Response:

```text
200 OK
```

```json
{
  "access_token": "eyJhbGciOiJIUzI1Ni...",
  "token_type": "bearer"
}
```

잘못된 계정 정보:

```text
401 Unauthorized
```

---

## 6.3 챗봇 질문

### `POST /api/chat`

로그인이 필요한 API입니다.

Header:

```text
Authorization: Bearer <access_token>
Content-Type: application/json
```

Request:

```json
{
  "question": "FastAPI의 장점이 뭐야?"
}
```

Response:

```json
{
  "question": "FastAPI의 장점이 뭐야?",
  "response": "FastAPI는 비동기 처리 지원, Pydantic 기반 입력 검증 등의 장점이 있습니다."
}
```

인증 정보가 없는 경우:

```text
401 Unauthorized
```

공백만 입력한 경우:

```text
422 Unprocessable Content
```

500자를 초과한 경우:

```text
422 Unprocessable Content
```

---

## 6.4 내 대화 이력 조회

### `GET /api/me/chats`

로그인이 필요한 API입니다.

Header:

```text
Authorization: Bearer <access_token>
```

Response:

```json
[
  {
    "id": 1,
    "question": "FastAPI의 장점이 뭐야?",
    "response": "FastAPI는 비동기 처리 지원...",
    "time": "2026-08-14T09:47:35"
  }
]
```

현재 로그인한 사용자 자신의 대화 기록만 반환합니다.

인증 정보가 없는 경우:

```text
401 Unauthorized
```

---

# 7. 인증 및 접근 제어

인증 흐름:

```text
회원가입
   ↓
PBKDF2 Password Hash 저장
   ↓
로그인
   ↓
비밀번호 검증
   ↓
JWT Access Token 발급
   ↓
Browser localStorage
   ↓
Authorization: Bearer <JWT>
   ↓
FastAPI get_current_user
   ↓
현재 사용자 확인
   ↓
보호된 API 접근
```

다음 API는 로그인 사용자만 접근할 수 있습니다.

```text
POST /api/chat
GET  /api/me/chats
```

백엔드 API에서 JWT를 직접 검증하므로 프론트엔드의 페이지 이동 제한에만 의존하지 않습니다.

배포 환경에서도 인증 없이 다음 API를 직접 호출하여 접근 제어를 검증했습니다.

```text
POST /api/chat
→ 401 Unauthorized

GET /api/me/chats
→ 401 Unauthorized
```

올바른 계정으로 로그인한 경우:

```text
POST /api/auth/login
→ 200 OK
→ JWT Access Token 발급
```

발급된 JWT를 사용한 경우:

```text
GET /api/me/chats
→ 200 OK
→ 현재 사용자의 대화 이력 반환
```

---

# 8. 데이터베이스 구조

SQLite + SQLAlchemy ORM을 사용합니다.

```text
+----------------------+       1 : N       +----------------------+
|        User          | ----------------> |       ChatLog        |
+----------------------+                   +----------------------+
| id (PK)              |                   | id (PK)              |
| username             |                   | user_id (FK)         |
| hashed_password      |                   | question             |
| created_at           |                   | response             |
+----------------------+                   | created_at           |
                                           +----------------------+
```

각 ChatLog에는 최소 다음 정보가 저장됩니다.

- 사용자 식별자 `user_id`
- 질문 `question`
- AI 응답 `response`
- 생성 시각 `created_at`

따라서 사용자 기준으로 대화 이력을 조회하고 추적할 수 있습니다.

---

# 9. DB 영속성

Railway 배포 환경에서 SQLite DB를 영속적으로 유지하기 위해 Persistent Volume을 사용합니다.

이를 통해 애플리케이션이 재배포되어 컨테이너가 교체되더라도 DB 데이터가 유지되도록 구성했습니다.

실제 검증 과정:

```text
1. railwaytest 계정 생성
2. 챗봇 대화 생성
3. ChatLog 저장 확인
4. Railway Redeploy
5. 기존 railwaytest 계정으로 다시 로그인
6. 기존 대화 기록 조회
```

재배포 이후에도 기존 계정과 대화 기록이 그대로 조회되는 것을 확인했습니다.

```text
Railway Redeploy
      ↓
Application Container 교체
      ↓
Persistent Volume 재연결
      ↓
SQLite DB 유지
      ↓
User 유지
      ↓
ChatLog 유지
```

---

# 10. 입력 검증

챗봇 질문에는 서버 사이드 입력 검증을 적용했습니다.

## 10.1 공백 입력

공백만 입력한 질문:

```json
{
  "question": "     "
}
```

배포 환경 테스트 결과:

```text
HTTP/2 422
```

```text
Value error, 질문은 공백일 수 없습니다.
```

---

## 10.2 최대 길이

질문 최대 길이는 500자입니다.

501자를 전달한 경우 배포 환경에서:

```text
HTTP/2 422
```

```text
String should have at most 500 characters
```

가 반환되는 것을 확인했습니다.

따라서 프론트엔드 검증뿐 아니라 직접 API 요청을 보내더라도 서버에서 잘못된 입력을 차단합니다.

---

# 11. 운영 안정성 및 예외 처리

## 11.1 AI Timeout

Gemini API 호출에는 5초 하드 타임아웃을 적용했습니다.

```text
Gemini API
    ↓
asyncio.wait_for()
    ↓
5초 초과
    ↓
Timeout
    ↓
Retry
```

---

## 11.2 Exponential Backoff

```text
1차 실패
 ↓
2초
 ↓
2차 시도
 ↓
실패
 ↓
4초
 ↓
3차 시도
```

최종 실패 시 서버 프로세스를 종료하지 않고 사용자에게 오류 안내를 반환합니다.

예:

```text
AI 서비스가 현재 혼잡합니다.
잠시 후 다시 시도해 주세요.
```

실제 Railway 환경에서도 Gemini 호출이 일시적으로 실패한 뒤 서비스 자체는 정상적으로 유지되고 이후 요청에서 AI 응답이 정상적으로 반환되는 것을 확인했습니다.

---

## 11.3 DB 실패

```text
db.add()
   ↓
db.commit()
   ↓
실패
   ↓
db.rollback()
```

DB 저장 실패가 이후 SQLAlchemy Session 사용에 미치는 영향을 최소화합니다.

---

# 12. 서버 로그

다음 이벤트를 기록합니다.

```text
request_received
ai_call_start
ai_call_success
ai_call_failed
ai_call_retry
db_save_success
db_save_failed
```

예:

```text
INFO:app_logger:request_received request_id=4c4ada56-... user_id=2 question_length=16
INFO:     ai_call_start request_id=4c4ada56-... prompt_length=16 context_count=0
ERROR:    ai_call_failed request_id=4c4ada56-... attempt=1 reason=timeout
INFO:     ai_call_retry request_id=4c4ada56-... attempt=1 wait=2s
INFO:     ai_call_success request_id=4c4ada56-... attempt=2
INFO:app_logger:db_save_success request_id=4c4ada56-... user_id=2 chat_id=9
```

동일한 `request_id`를 통해:

```text
요청 수신
→ AI 호출
→ Retry
→ AI 성공/실패
→ DB 저장
```

의 전체 흐름을 하나의 요청 단위로 추적할 수 있습니다.

사용자의 실제 질문 내용은 요청 로그에 직접 남기지 않고 `question_length`만 기록합니다.

---

# 13. 대화 로그 확인 가이드

## 13.1 웹 화면

로그인 후 `/chat` 페이지에 접속하면:

```text
GET /api/me/chats
```

를 호출하여 현재 로그인한 사용자의 기존 대화 기록을 화면에 표시합니다.

---

## 13.2 API 조회

로컬:

```bash
curl \
  -H "Authorization: Bearer <access_token>" \
  http://127.0.0.1:8000/api/me/chats
```

배포 환경:

```bash
curl \
  -H "Authorization: Bearer <access_token>" \
  https://term-project-proto-production.up.railway.app/api/me/chats
```

응답:

```json
[
  {
    "id": 1,
    "question": "질문",
    "response": "AI 응답",
    "time": "2026-08-14T09:47:35"
  }
]
```

이를 통해 평가 시 사용자 기준 로그 저장 및 조회 여부를 직접 검증할 수 있습니다.

---

# 14. 프론트엔드 메시지 렌더링 보안

채팅 메시지를 화면에 출력할 때 `innerHTML` 문자열 삽입 대신 DOM API와 `textContent`를 사용합니다.

```javascript
const messageText = document.createElement('span');
messageText.textContent = String(message ?? '');
```

## 테스트 1

입력:

```html
<h1>TEST</h1>
```

결과:

```text
<h1>TEST</h1>
```

HTML 제목으로 실행되지 않고 일반 문자열로 표시됩니다.

---

## 테스트 2

입력:

```html
<img src=x onerror="alert('test')">
```

배포 환경에서 테스트한 결과:

- 문자열 그대로 표시
- 실제 `<img>` 요소 생성 안 됨
- `onerror` 실행 안 됨
- JavaScript Alert 발생 안 함
- 문자열 자체는 정상적으로 Gemini API에 전달됨

따라서 채팅 메시지 출력 과정에서 사용자 입력을 HTML 코드로 직접 해석하지 않도록 구성했습니다.

---

# 15. 환경 변수 및 민감정보 관리

민감정보는 소스 코드에 직접 작성하지 않습니다.

필요한 환경 변수:

```env
SECRET_KEY=your_secret_key_here
ALGORITHM=HS256
GEMINI_API_KEY=your_gemini_api_key_here
```

로컬에서는 `.env`를 사용하고, 배포 환경에서는 Railway의 환경 변수 설정을 사용합니다.

실제 Secret 값은 README 또는 Git 저장소에 작성하지 않습니다.

---

## 15.1 `.gitignore`

```gitignore
.env

*.db
*.sqlite3

.venv/
venv/
env/

__pycache__/
*.py[cod]

.DS_Store
```

이를 통해 다음 항목이 GitHub에 직접 노출되지 않도록 합니다.

- Gemini API Key
- JWT Secret Key
- 로컬 SQLite DB
- Python 가상환경
- Python Cache

---

# 16. 로컬 실행 방법

## 16.1 Clone

```bash
git clone https://github.com/bangahee/term-project-proto.git
cd term-project-proto
```

---

## 16.2 가상환경 생성

macOS / Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
```

---

## 16.3 Dependency 설치

```bash
pip install -r requirements.txt
```

---

## 16.4 환경 변수 설정

macOS / Linux:

```bash
cp .env.example .env
```

`.env`:

```env
SECRET_KEY=<your-secret-key>
ALGORITHM=HS256
GEMINI_API_KEY=<your-gemini-api-key>
```

실제 값을 입력합니다.

---

## 16.5 테스트

```bash
pytest -v
```

현재 입력 검증 테스트 결과:

```text
tests/test_validation.py::test_valid_question PASSED
tests/test_validation.py::test_whitespace_question_rejected PASSED
tests/test_validation.py::test_question_too_long_rejected PASSED

3 passed
```

---

## 16.6 서버 실행

```bash
uvicorn main:app --reload
```

정상 실행:

```text
INFO: Uvicorn running on http://127.0.0.1:8000
INFO: Application startup complete.
```

브라우저:

```text
http://127.0.0.1:8000
```

---

# 17. Railway 배포

현재 서비스는 Railway에서 실행됩니다.

배포 URL:

```text
https://term-project-proto-production.up.railway.app
```

## 배포 환경 변수

Railway에서 다음 환경 변수를 설정해야 합니다.

```text
SECRET_KEY
ALGORITHM
GEMINI_API_KEY
```

실제 Secret 값은 GitHub에 저장하지 않습니다.

## DB

배포 환경의 SQLite DB는 Persistent Volume을 통해 유지합니다.

따라서 단순 컨테이너 파일 시스템에만 DB를 저장하는 방식과 달리 재배포 이후에도 사용자 및 ChatLog 데이터를 유지할 수 있습니다.

---

# 18. Production 검증 결과

Railway에 배포한 실제 서비스를 대상으로 다음 테스트를 수행했습니다.

| 테스트 | 결과 |
| --- | --- |
| 외부 서비스 URL 접근 | ✅ |
| 회원가입 | ✅ |
| 로그인 | ✅ |
| 올바른 로그인 → JWT 발급 | ✅ |
| 잘못된 로그인 → `401` | ✅ |
| `/api/chat` 인증 없음 → `401` | ✅ |
| `/api/me/chats` 인증 없음 → `401` | ✅ |
| JWT + `/api/me/chats` → `200` | ✅ |
| 사용자별 기존 대화 조회 | ✅ |
| Gemini API 정상 응답 | ✅ |
| Gemini API 실패 시 서버 유지 | ✅ |
| Retry 이후 AI 응답 성공 | ✅ |
| ChatLog DB 저장 | ✅ |
| 공백 질문 → `422` | ✅ |
| 501자 질문 → `422` | ✅ |
| HTML 문자열 안전 출력 | ✅ |
| XSS 형태 입력 실행 방지 | ✅ |
| Railway 재배포 | ✅ |
| 재배포 후 기존 사용자 유지 | ✅ |
| 재배포 후 기존 ChatLog 유지 | ✅ |

---

# 19. Production 검증 명령어

## 19.1 인증 없는 챗봇 접근

```bash
curl -i -X POST \
  https://term-project-proto-production.up.railway.app/api/chat \
  -H "Content-Type: application/json" \
  -d '{"question":"hello"}'
```

예상:

```text
401 Unauthorized
```

---

## 19.2 인증 없는 로그 조회

```bash
curl -i \
  https://term-project-proto-production.up.railway.app/api/me/chats
```

예상:

```text
401 Unauthorized
```

---

## 19.3 로그인

```bash
curl -i -X POST \
  https://term-project-proto-production.up.railway.app/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"<username>","password":"<password>"}'
```

성공 시:

```text
200 OK
```

및 JWT Access Token이 반환됩니다.

> 실제 비밀번호 및 JWT Token은 README에 기록하지 않습니다.

---

## 19.4 JWT 저장

```bash
TOKEN='<access_token>'
```

---

## 19.5 인증된 로그 조회

```bash
curl -i \
  https://term-project-proto-production.up.railway.app/api/me/chats \
  -H "Authorization: Bearer $TOKEN"
```

예상:

```text
200 OK
```

---

## 19.6 공백 입력 검증

```bash
curl -i -X POST \
  https://term-project-proto-production.up.railway.app/api/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"question":"     "}'
```

예상:

```text
422 Unprocessable Content
```

---

## 19.7 501자 입력 검증

```bash
curl -i -X POST \
  https://term-project-proto-production.up.railway.app/api/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d "$(python3 -c 'import json; print(json.dumps({"question":"a"*501}))')"
```

예상:

```text
422 Unprocessable Content
```

---

# 20. 팀 협업 및 역할 분담 계획

본 PoC를 팀 프로젝트의 기술적 베이스라인으로 활용할 예정입니다.

아래 내용은 **현재 완료된 팀 작업 실적이 아니라 팀 프로젝트 진행 계획**입니다.

| 구분 | 담당 영역 | 예정 작업 |
| --- | --- | --- |
| **팀원 A (PoC 작성자)** | 시스템 아키텍처 / Backend | PoC 구조 정리, 핵심 API, DB ORM 및 전체 통합 |
| **팀원 B** | AI / 안정성 | Prompt 개선, AI 예외 처리 및 Retry 전략 고도화 |
| **팀원 C** | 인증 / 보안 | 인증 구조 검토, 접근 제어 및 보안 강화 |
| **팀원 D** | Frontend UI/UX | UI 개선, 로딩 상태, 반응형 디자인 및 사용자 경험 개선 |

최종 프로젝트에서는 실제 팀원 이름, 실제 담당 기능 및 작업 결과를 Git 이력과 일치하도록 작성합니다.

---

# 21. Git Branch / PR 전략

현재 PoC는 단일 작성자가 `main` 브랜치에서 구현했습니다.

따라서 아래 구조는 **팀 프로젝트에서 실제 적용할 협업 전략**이며 현재 PoC에서 이미 적용했다고 주장하지 않습니다.

```text
main
 │
 └── develop
      │
      ├── feat/auth
      ├── feat/ai
      ├── feat/frontend
      └── fix/<bug-name>
```

## 브랜치 역할

| Branch | 역할 |
| --- | --- |
| `main` | 평가 및 배포 가능한 안정 버전 |
| `develop` | 기능 개발 결과 통합 |
| `feat/<기능명>` | 기능 단위 개발 |
| `fix/<버그명>` | 버그 수정 |

## 팀 프로젝트 Git 규칙

1. `main`과 `develop`에서 직접 기능 개발하지 않습니다.
2. `develop`에서 기능 브랜치를 생성합니다.
3. 기능 구현 후 GitHub PR을 생성합니다.
4. 팀원 코드 리뷰 후 `develop`에 Merge합니다.
5. 검증된 버전만 `main`에 반영합니다.
6. 의미 있는 기능 단위로 Commit을 분리합니다.
7. 평가 전 팀원별 유의미한 Commit 10회 이상을 확인합니다.

예:

```bash
git checkout develop
git pull origin develop
git checkout -b feat/chat-ui
```

작업:

```bash
git add .
git commit -m "feat: add chat loading state"
git push origin feat/chat-ui
```

이후:

```text
feat/chat-ui
     ↓
Pull Request
     ↓
Code Review
     ↓
develop
```

---

# 22. 현재 구현 상태

## PoC 완료

- [x] FastAPI 웹 서버
- [x] 회원가입
- [x] 로그인
- [x] PBKDF2 비밀번호 해싱
- [x] JWT Access Token
- [x] 로그인 사용자 전용 챗봇 API
- [x] 사용자별 대화 이력 접근 제어
- [x] SQLite
- [x] SQLAlchemy ORM
- [x] User / ChatLog 1:N 구조
- [x] 사용자별 ChatLog 저장
- [x] `GET /api/me/chats`
- [x] 최근 3개 대화 Context
- [x] Gemini API Backend 연동
- [x] 5초 하드 타임아웃
- [x] 최대 3회 AI 호출
- [x] Exponential Backoff
- [x] AI API 예외 처리
- [x] DB 저장 실패 `rollback()`
- [x] 주요 서버 이벤트 로깅
- [x] UUID 기반 `request_id`
- [x] 사용자 질문 원문 요청 로그 제외
- [x] 클라이언트 입력 검증
- [x] 서버 공백 입력 검증
- [x] 500자 최대 길이 검증
- [x] Pytest 입력 검증 테스트
- [x] `textContent` 기반 안전한 메시지 렌더링
- [x] HTML 형태 입력 안전 출력 검증
- [x] XSS 형태 입력 실행 방지 검증
- [x] `.env` 기반 민감정보 관리
- [x] `.gitignore`
- [x] 로컬 실행 검증
- [x] Railway 외부 배포
- [x] 외부 접근 가능한 서비스 URL
- [x] Railway 환경 변수 설정
- [x] 배포 환경 회원가입/로그인 검증
- [x] 배포 환경 JWT 인증 검증
- [x] 배포 환경 Gemini API 검증
- [x] 배포 환경 ChatLog 저장/조회 검증
- [x] 배포 환경 입력 검증
- [x] Railway Persistent Volume
- [x] Railway 재배포 후 DB 데이터 유지 검증

## 팀 본 프로젝트에서 추가 필요

- [ ] `main` / `develop` 브랜치 실제 운영
- [ ] 기능 단위 작업 브랜치 사용
- [ ] PR 기반 Merge 기록
- [ ] 팀원별 유의미한 Commit 10회 이상
- [ ] 실제 팀 구성원 역할 작성
- [ ] 팀원별 실제 작업 요약 작성
- [ ] Git 이력과 역할 설명 최종 대조
- [ ] 팀 통합 이후 전체 Regression Test
- [ ] 최종 평가 직전 배포 URL 정상 동작 재확인

---

# 23. 평가 요구사항 대응 현황

| 요구사항 | 현재 상태 |
| --- | --- |
| FastAPI 웹 서비스 | ✅ PoC 완료 |
| 질문 입력 Web UI | ✅ |
| 같은 화면에서 AI 응답 확인 | ✅ |
| 회원가입 | ✅ |
| 로그인 | ✅ |
| 인증 상태 기반 접근 제어 | ✅ |
| 챗봇 로그인 사용자 전용 | ✅ |
| 서버에서 AI API 호출 | ✅ |
| API Key 서버 관리 | ✅ |
| 최소 Context 전략 | ✅ 최근 3개 대화 |
| 질문/응답 DB 누적 저장 | ✅ |
| 사용자 식별 정보 저장 | ✅ |
| 생성 시각 저장 | ✅ |
| 사용자 기준 로그 조회 | ✅ |
| 요청 수신 로그 | ✅ |
| AI 호출 로그 | ✅ |
| AI 성공/실패 로그 | ✅ |
| DB 저장 성공/실패 로그 | ✅ |
| AI Timeout | ✅ |
| AI 실패 시 서버 비정상 종료 방지 | ✅ |
| 사용자 오류 안내 | ✅ |
| 입력 검증 | ✅ |
| 외부 네트워크 배포 | ✅ |
| 서비스 URL 제공 | ✅ |
| 환경 변수 관리 | ✅ |
| `.env.example` | ✅ |
| `.gitignore` | ✅ |
| DB 확인 방법 | ✅ `/api/me/chats` |
| DB 영속성 | ✅ Railway Volume |
| README / 기술 문서 | ✅ |
| `main` / `develop` 운영 | ⏳ 팀 프로젝트에서 진행 |
| 기능 브랜치 | ⏳ 팀 프로젝트에서 진행 |
| PR 기반 Merge | ⏳ 팀 프로젝트에서 진행 |
| 팀원별 Commit 10회 이상 | ⏳ 팀 프로젝트에서 진행 |
| 실제 팀 역할/작업 요약 | ⏳ 팀 프로젝트에서 진행 |

---

# 24. 최종 목표

현재 PoC에서는 다음 기술 흐름을 실제 배포 환경까지 연결하여 검증했습니다.

```text
사용자
  ↓
Railway Public URL
  ↓
회원가입 / 로그인
  ↓
PBKDF2 + JWT
  ↓
인증된 질문 요청
  ↓
FastAPI
  ↓
Pydantic 입력 검증
  ↓
최근 ChatLog Context 조회
  ↓
Google Gemini API
  ↓
Timeout / Retry / Backoff
  ↓
AI 응답
  ↓
SQLite ChatLog 저장
  ↓
Persistent Volume
  ↓
사용자별 대화 이력 조회
  ↓
안전한 DOM 렌더링
  ↓
웹 화면 출력
```

따라서 현재 PoC에서는 **Web + Authentication + DB + AI API + Logging + Error Handling + Deployment + Persistence**의 핵심 통합 흐름을 구축했습니다.

다음 단계에서는 이 PoC를 팀 프로젝트의 기술적 베이스라인으로 사용하고, 실제 팀원들과 `develop` 및 기능 브랜치, PR 기반 Merge, 팀원별 Commit 이력을 구축하여 최종 Term Project로 확장하는 것을 목표로 합니다.