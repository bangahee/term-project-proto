# 🤖 웹 기반 AI 챗봇 서비스 PoC (Term Project Prototype)

FastAPI와 Google Gemini API를 기반으로 구현한 **사용자 인증, 대화 문맥 유지, 대화 이력 DB 저장을 지원하는 웹 AI 챗봇 서비스의 기능 검증용 프로토타입(PoC)**입니다.

팀 프로젝트 본격 착수 전, 웹 UI → FastAPI 백엔드 → 사용자 인증 → AI API 호출 → 대화 문맥 구성 → DB 저장 → 로그 추적까지의 전체 파이프라인이 하나의 서비스 안에서 정상적으로 연결되는지 검증하기 위해 선제적으로 제작했습니다.

> ⚠️ **현재 단계 안내**
> 본 저장소는 단일 작성자가 구현한 PoC 단계입니다.
> 외부 네트워크 배포, `main`/`develop` 브랜치 운영, 기능 브랜치, PR 기반 협업, 팀원별 유의미한 커밋 10회 이상 등의 **팀 협업 요구사항은 아직 완료된 것으로 간주하지 않으며**, 팀 본 프로젝트에서 실제 이력과 함께 적용할 예정입니다.

---

## 1. 프로젝트 개요 및 PoC 목적

### 개발 목적

팀원들과의 역할 분담 및 본격적인 개발에 앞서 다음 기술 요소가 하나의 서비스 안에서 정상적으로 연결되는지 검증하는 것이 목적입니다.

```text
Web UI
→ FastAPI
→ JWT 인증
→ 사용자 입력 검증
→ 최근 대화 Context 조회
→ Google Gemini API 호출
→ AI 응답 반환
→ SQLite DB 저장
→ 사용자별 대화 이력 조회
```

핵심 기술 구성은 다음과 같습니다.

* **Web / Backend**: FastAPI
* **Frontend**: HTML / CSS / JavaScript + Jinja2 Templates
* **Database**: SQLite + SQLAlchemy ORM
* **Authentication**: JWT + PBKDF2 Password Hashing
* **AI API**: Google Gemini API (`google-genai`)
* **Configuration**: `.env` + `python-dotenv`

### 타겟 사용자

로그인 후 개인별 대화 기록을 보관하면서 이전 대화를 바탕으로 연속성 있는 AI 대화를 진행하고자 하는 웹 사용자입니다.

### 핵심 기능

1. PBKDF2 해싱 및 JWT 기반 회원가입/로그인
2. 인증 상태에 따른 챗봇 API 및 사용자별 대화 이력 접근 제어
3. Google GenAI SDK 기반 Gemini API 연동
4. 최근 3개 대화를 활용한 최소 Context 구성
5. 사용자 질문 및 AI 응답의 SQLite DB 누적 저장
6. 로그인 사용자 기준 대화 이력 조회
7. Pydantic 및 클라이언트 검증을 통한 빈 입력/길이 제한
8. AI API 5초 하드 타임아웃
9. 일시적인 AI API 오류에 대한 최대 3회 재시도 및 Exponential Backoff
10. `request_id` 기반 요청 흐름 추적
11. DB 저장 실패 시 `rollback()` 처리
12. 사용자 질문 본문을 서버 요청 로그에 남기지 않는 로깅 방식
13. `textContent` 기반 안전한 DOM 렌더링을 통한 HTML/XSS 실행 방지

---

## 2. 프로토타입 제작 단계 (Development Steps)

프로토타입은 핵심 기능을 단계적으로 추가하고 검증하는 방식으로 구축했습니다.

### Step 1. 개발 환경 설정 및 DB ORM 구축

* Python 가상환경(`.venv`) 구성
* FastAPI, Uvicorn, SQLAlchemy, Google GenAI SDK, JWT 관련 패키지 설치
* `database.py`에 SQLAlchemy 엔진 및 세션 관리 로직 구현
* `models.py`에 `User`, `ChatLog` ORM 모델 정의
* 사용자와 대화 로그 사이의 1:N 관계 구성

### Step 2. 인증 모듈 및 민감정보 관리

* `auth.py`에서 `passlib` 기반 PBKDF2 비밀번호 해싱 구현
* 로그인 성공 시 JWT Access Token 발급
* `get_current_user` 의존성을 통해 보호된 API에서 사용자 인증
* `SECRET_KEY`, `GEMINI_API_KEY` 등 민감정보를 `.env`로 분리
* `.env`를 `.gitignore`에 등록하여 Git 저장소에서 제외

### Step 3. 다중 페이지 UI 및 FastAPI 라우팅

HTML 화면을 다음과 같이 분리했습니다.

```text
templates/
├── login.html
├── register.html
└── chat.html
```

각 파일의 역할은 다음과 같습니다.

* `login.html`: 로그인
* `register.html`: 회원가입
* `chat.html`: 챗봇 대화 및 기존 대화 이력 표시

FastAPI에서는 다음 HTML 라우트를 제공합니다.

```text
GET /
GET /login
GET /register
GET /chat
```

실제 챗봇 데이터 요청과 대화 이력 요청은 JWT 인증이 필요한 API를 통해 처리됩니다.

```text
POST /api/chat
GET  /api/me/chats
```

> `chat.html`은 클라이언트에서도 토큰 존재 여부를 확인하여 토큰이 없으면 로그인 화면으로 이동합니다.
> 실제 보호가 필요한 데이터/API 접근은 백엔드의 JWT 검증(`get_current_user`)을 통해 수행합니다.

### Step 4. AI API 연동 및 대화 Context 구성

`ai_service.py`에서 Google GenAI SDK의 비동기 API를 사용합니다.

```python
client.aio.models.generate_content(...)
```

현재 모델 설정:

```text
gemini-3.6-flash
```

AI 호출 전 로그인한 사용자의 최근 대화 3개를 DB에서 조회합니다.

```text
최근 ChatLog 3개 조회
        ↓
과거 → 최신 순서로 정렬
        ↓
user 질문
model 응답
user 질문
model 응답
...
        ↓
현재 질문 추가
        ↓
Gemini API 호출
```

이를 통해 다음과 같은 연속 대화가 가능합니다.

```text
사용자: 배고파
챗봇: 무엇을 먹고 싶은지 알려주세요.

사용자: 내가 아까 뭐라고 했어?
챗봇: 아까 배고프다고 말씀하셨어요.
```

AI API 키가 브라우저에 노출되지 않도록 Gemini 호출은 모두 FastAPI 백엔드에서 수행합니다.

### Step 5. 타임아웃 및 예외 처리

`asyncio.wait_for()`를 사용하여 Gemini API 호출 1회당 **5초 하드 타임아웃**을 적용했습니다.

```text
TIMEOUT_SECONDS = 5.0
```

따라서 AI API가 장시간 응답하지 않아도 서버가 무한정 대기하지 않습니다.

타임아웃 발생 시 사용자에게 다음과 같은 안내 메시지를 반환합니다.

```text
현재 응답이 지연되고 있어요.
잠시 후 다시 시도해 주세요.
(error: AI_TIMEOUT)
```

### Step 6. Retry 및 Exponential Backoff

일시적인 API 장애에 대응하기 위해 최대 3회의 호출 시도를 적용했습니다.

재시도 대상 예시는 다음과 같습니다.

* `429 RESOURCE_EXHAUSTED`
* `503 UNAVAILABLE`
* AI API Timeout

재시도 간 대기 시간은 Exponential Backoff 방식으로 증가합니다.

```text
1차 실패
→ 2초 대기
→ 2차 호출

2차 실패
→ 4초 대기
→ 3차 호출

3차 실패
→ 사용자에게 오류 안내
```

이를 통해 일시적인 API 장애가 발생했을 때 즉시 전체 요청을 실패시키지 않고 제한된 범위에서 자동 복구를 시도합니다.

### Step 7. DB 트랜잭션 실패 처리

AI 응답을 `ChatLog`에 저장할 때 DB 오류가 발생하면 다음과 같이 처리합니다.

```python
try:
    db.add(chat_log)
    db.commit()

except Exception:
    db.rollback()
```

`rollback()`을 통해 실패한 SQLAlchemy 세션의 트랜잭션 상태를 되돌려 이후 DB 작업에 영향을 최소화합니다.

### Step 8. `request_id` 기반 로그 추적

각 `/api/chat` 요청마다 UUID 기반의 고유 `request_id`를 생성합니다.

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

동일한 요청에서 발생한 로그에는 동일한 `request_id`가 기록됩니다.

예:

```text
request_received request_id=b67c61c2-... user_id=1 question_length=2
ai_call_start request_id=b67c61c2-... prompt_length=2 context_count=3
ai_call_success request_id=b67c61c2-... attempt=1
db_save_success request_id=b67c61c2-... user_id=1 chat_id=4
```

따라서 여러 사용자의 요청이 동시에 발생하더라도 하나의 요청이 어떤 처리 단계를 거쳤는지 추적하기 쉽습니다.

또한 사용자 질문 본문을 서버 요청 로그에 직접 기록하지 않고 다음 정보만 기록합니다.

```text
user_id
request_id
question_length
```

### Step 9. 안전한 프론트엔드 메시지 렌더링

`chat.html`에서 사용자 질문과 AI 응답을 화면에 출력할 때 외부 데이터를 `innerHTML` 문자열 보간 방식으로 삽입하지 않습니다.

대신 DOM Element를 생성하고 `textContent`를 사용합니다.

```javascript
messageText.textContent = String(message ?? '');
```

따라서 다음과 같은 문자열을 입력해도:

```html
<h1>TEST</h1>
```

브라우저에서 HTML 태그로 렌더링되지 않고 문자 그대로 표시됩니다.

또한 다음과 같은 입력도:

```html
<img src=x onerror="alert('test')">
```

실제 `<img>` 요소나 JavaScript 이벤트 핸들러로 실행되지 않고 일반 텍스트로 출력됩니다.

이를 통해 채팅 메시지를 DOM에 삽입하는 과정에서 발생할 수 있는 XSS 위험을 줄였습니다.

---

## 3. 시스템 아키텍처 및 구성 요소

### 3.1 전체 아키텍처

```text
┌─────────────────────────────┐
│       Client Browser        │
│ HTML / CSS / JavaScript     │
│                             │
│ login / register / chat     │
└──────────────┬──────────────┘
               │
               │ REST API
               │ Authorization: Bearer <JWT>
               ▼
┌─────────────────────────────┐
│       FastAPI Server        │
│          main.py            │
│                             │
│ - Routing                   │
│ - Pydantic Validation       │
│ - JWT Authentication        │
│ - request_id 생성           │
│ - Server Logging            │
└───────┬───────────┬─────────┘
        │           │
        │           │
        ▼           ▼
┌──────────────┐  ┌─────────────────────┐
│   auth.py    │  │    ai_service.py    │
│              │  │                     │
│ - PBKDF2     │  │ - Context 구성      │
│ - JWT        │  │ - Gemini API        │
│              │  │ - 5s Timeout        │
│              │  │ - Retry             │
│              │  │ - Backoff           │
└──────────────┘  └──────────┬──────────┘
                             │
                             ▼
                   ┌─────────────────────┐
                   │ Google Gemini API   │
                   └─────────────────────┘

        FastAPI
           │
           ▼
┌─────────────────────────────┐
│ database.py + models.py     │
│ SQLAlchemy ORM              │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│       SQLite Database       │
│         chatbot.db          │
│                             │
│ Users / ChatLogs            │
└─────────────────────────────┘
```

### 3.2 주요 컴포넌트 역할

| 파일/디렉터리                   | 역할                                                                                    |
| ------------------------- | ------------------------------------------------------------------------------------- |
| `main.py`                 | FastAPI 앱 엔트리포인트, 페이지 라우팅, REST API, 입력 검증, 인증 의존성 연결, `request_id` 생성, DB 저장 및 서버 로깅 |
| `auth.py`                 | PBKDF2 비밀번호 해싱, JWT Access Token 생성 및 인증 사용자 조회                                       |
| `ai_service.py`           | Gemini API 호출, 최근 대화 Context 구성, 5초 타임아웃, Retry, Exponential Backoff 및 AI 예외 처리       |
| `database.py`             | SQLite SQLAlchemy 엔진, DB 세션 및 초기화 관리                                                  |
| `models.py`               | `User`, `ChatLog` SQLAlchemy ORM 모델 정의                                                |
| `templates/login.html`    | 로그인 UI                                                                                |
| `templates/register.html` | 회원가입 UI                                                                               |
| `templates/chat.html`     | 챗봇 UI, 대화 이력 표시, 안전한 DOM 렌더링                                                          |

---

## 4. API 명세

## 4.1 회원가입

### `POST /api/auth/register`

**Request**

```json
{
  "username": "testuser",
  "password": "password123"
}
```

**Response — `201 Created`**

```json
{
  "message": "회원가입 완료"
}
```

이미 존재하는 사용자명일 경우:

```text
400 Bad Request
```

---

## 4.2 로그인

### `POST /api/auth/login`

**Request**

```json
{
  "username": "testuser",
  "password": "password123"
}
```

**Response — `200 OK`**

```json
{
  "access_token": "eyJhbGciOiJIUzI1Ni...",
  "token_type": "bearer"
}
```

인증 실패 시:

```text
401 Unauthorized
```

---

## 4.3 챗봇 질문

### `POST /api/chat`

로그인이 필요한 API입니다.

**Header**

```text
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request**

```json
{
  "question": "FastAPI의 장점이 뭐야?"
}
```

질문 길이는 서버의 Pydantic Schema를 통해 제한됩니다.

```text
최소 길이: 1자
최대 길이: 500자
```

클라이언트에서는 `trim()`을 사용하여 공백만 입력한 질문도 차단합니다.

**Response — `200 OK`**

```json
{
  "question": "FastAPI의 장점이 뭐야?",
  "response": "FastAPI는 비동기 처리 지원, Pydantic 기반 입력 검증 등의 장점이 있습니다."
}
```

AI Timeout 발생 후 모든 재시도가 실패한 경우에도 서버 프로세스가 종료되지 않고 사용자에게 안내 메시지를 반환합니다.

예:

```json
{
  "question": "긴 글 요약해줘",
  "response": "현재 응답이 지연되고 있어요. 잠시 후 다시 시도해 주세요. (error: AI_TIMEOUT)"
}
```

> 현재 PoC에서는 AI 서비스 오류를 사용자용 응답 문자열로 변환해 정상 JSON 응답 형태로 반환합니다. 향후 본 프로젝트에서는 오류 유형별 HTTP 상태 코드와 구조화된 에러 응답 도입을 검토할 수 있습니다.

---

## 4.4 내 대화 이력 조회

### `GET /api/me/chats`

로그인이 필요한 API입니다.

**Header**

```text
Authorization: Bearer <access_token>
```

로그인한 사용자 자신의 대화 기록만 조회합니다.

**Response — `200 OK`**

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

## 5. 인증 및 접근 제어

인증 흐름은 다음과 같습니다.

```text
회원가입
   ↓
비밀번호 PBKDF2 Hash 저장
   ↓
로그인
   ↓
비밀번호 검증
   ↓
JWT Access Token 발급
   ↓
Browser localStorage 저장
   ↓
Authorization: Bearer <token>
   ↓
FastAPI get_current_user
   ↓
사용자 확인
   ↓
보호된 API 접근
```

다음 API는 인증된 사용자만 접근할 수 있습니다.

```text
POST /api/chat
GET  /api/me/chats
```

인증되지 않은 요청은 JWT 검증 단계에서 거부됩니다.

`/chat` HTML 페이지에서는 클라이언트 JavaScript가 토큰 존재 여부를 확인하여 토큰이 없으면 `/login`으로 이동합니다.

중요한 데이터 접근 제어는 프론트엔드에만 의존하지 않고 백엔드 API의 `get_current_user` 검증을 통해 수행합니다.

---

## 6. 대화 Context 유지 전략

현재 PoC에서는 로그인 사용자의 **최근 3개 대화**를 AI Context로 사용합니다.

`main.py`에서:

```text
현재 사용자 ID 확인
       ↓
ChatLog 조회
       ↓
created_at DESC
       ↓
LIMIT 3
```

`ai_service.py`에서는 조회된 데이터를 다시 과거 → 최신 순서로 구성합니다.

```text
과거 질문
→ 과거 AI 응답
→ 다음 질문
→ 다음 AI 응답
→ 현재 질문
```

이 방식은 전체 대화 기록을 매번 전달하지 않으면서도 최근 대화의 연속성을 유지하기 위한 최소 Context 전략입니다.

---

## 7. 데이터베이스 구조 (Database Schema)

SQLite와 SQLAlchemy ORM을 사용합니다.

`User` 한 명이 여러 개의 `ChatLog`를 가질 수 있는 **1:N 관계**입니다.

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

### 최소 추적 정보

각 대화 로그에는 다음 정보가 저장됩니다.

* 사용자 식별자 (`user_id`)
* 사용자 질문 (`question`)
* AI 응답 (`response`)
* 생성 시각 (`created_at`)

이를 통해 특정 사용자 기준으로 대화를 조회하고 추적할 수 있습니다.

---

## 8. 운영 안정성 및 예외 처리

### 8.1 AI Timeout

```text
Gemini API 호출
      ↓
asyncio.wait_for()
      ↓
5초 이내 응답?
 ┌────┴────┐
Yes        No
 │          │
응답       Timeout
            ↓
          Retry
```

### 8.2 Exponential Backoff

```text
1차 호출 실패
    ↓
2초 대기
    ↓
2차 호출 실패
    ↓
4초 대기
    ↓
3차 호출 실패
    ↓
사용자 오류 안내
```

### 8.3 DB 저장 실패

```text
AI 응답 수신
    ↓
db.add()
    ↓
db.commit()
    ↓
 성공? ─── Yes → db_save_success
    │
    No
    ↓
db.rollback()
    ↓
db_save_failed
```

### 8.4 사용자 입력 검증

현재 질문 입력에는 다음 검증이 적용됩니다.

* Pydantic 최소 길이 1자
* Pydantic 최대 길이 500자
* 브라우저에서 `trim()` 적용 후 빈 입력 차단

---

## 9. 서버 로깅 및 `request_id` 추적

평가 요구사항에 맞춰 주요 처리 단계가 서버 로그에 기록됩니다.

주요 이벤트:

```text
request_received
ai_call_start
ai_call_success
ai_call_failed
ai_call_retry
db_save_success
db_save_failed
```

각 채팅 요청에는 UUID 기반 `request_id`가 부여됩니다.

실제 정상 동작 확인 로그 예:

```text
INFO:app_logger:request_received request_id=b67c61c2-edf1-445f-80ac-cae985a84245 user_id=1 question_length=2
INFO:     ai_call_start request_id=b67c61c2-edf1-445f-80ac-cae985a84245 prompt_length=2 context_count=3
INFO:     ai_call_success request_id=b67c61c2-edf1-445f-80ac-cae985a84245 attempt=1
INFO:app_logger:db_save_success request_id=b67c61c2-edf1-445f-80ac-cae985a84245 user_id=1 chat_id=4
INFO:     127.0.0.1:56837 - "POST /api/chat HTTP/1.1" 200 OK
```

위 로그에서 동일한:

```text
b67c61c2-edf1-445f-80ac-cae985a84245
```

가 전체 처리 과정에 사용됩니다.

따라서:

```text
요청 수신
→ AI 호출
→ AI 응답
→ DB 저장
```

을 하나의 요청 단위로 추적할 수 있습니다.

또한 사용자 질문 원문을 요청 로그에 남기지 않고 `question_length`만 기록하여 불필요한 사용자 입력 노출을 줄였습니다.

---

## 10. 대화 로그 확인 가이드

### 10.1 웹 화면

로그인 후 `/chat`에 접속하면 `GET /api/me/chats`를 통해 해당 사용자의 기존 대화 기록이 자동으로 표시됩니다.

### 10.2 API

Access Token을 이용해 직접 조회할 수도 있습니다.

```bash
curl \
  -H "Authorization: Bearer <access_token>" \
  http://127.0.0.1:8000/api/me/chats
```

응답에는 다음 정보가 포함됩니다.

```text
id
question
response
time
```

따라서 평가 시 사용자 기준 로그 저장 및 조회 여부를 API와 웹 화면 양쪽에서 확인할 수 있습니다.

---

## 11. 프론트엔드 메시지 렌더링 보안

채팅 메시지는 `innerHTML` 문자열 보간 방식으로 출력하지 않고 DOM API와 `textContent`를 사용합니다.

예:

```javascript
const messageText = document.createElement('span');
messageText.textContent = String(message ?? '');
```

### 테스트 예시 1

입력:

```html
<h1>TEST</h1>
```

화면:

```text
<h1>TEST</h1>
```

`TEST`가 HTML 제목 요소로 렌더링되지 않고 문자열 그대로 출력됩니다.

### 테스트 예시 2

입력:

```html
<img src=x onerror="alert('test')">
```

결과:

* 문자열 그대로 표시
* `<img>` 요소 생성 안 됨
* `onerror` JavaScript 실행 안 됨
* Alert 팝업 발생 안 함

이를 통해 채팅 출력 과정에서 사용자 입력 및 AI 응답을 HTML로 직접 해석하지 않도록 구성했습니다.

---

## 12. 환경 변수 및 민감정보 관리

API 키와 JWT 서명 키 등의 민감정보는 코드에 직접 작성하지 않고 환경 변수로 관리합니다.

### `.env.example`

```env
SECRET_KEY=your_secret_key_here
ALGORITHM=HS256
GEMINI_API_KEY=your_gemini_api_key_here
```

실제 값은 로컬 `.env`에 작성합니다.

```env
SECRET_KEY=<실제_SECRET_KEY>
ALGORITHM=HS256
GEMINI_API_KEY=<실제_GEMINI_API_KEY>
```

실제 `.env` 파일은 Git에 커밋하지 않습니다.

### `.gitignore`

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

이를 통해 다음 정보가 GitHub에 직접 노출되는 것을 방지합니다.

* Gemini API Key
* JWT Secret Key
* 로컬 DB
* 가상환경 파일

---

## 13. 로컬 실행 가이드

### 13.1 저장소 Clone

```bash
git clone https://github.com/bangahee/term-project-proto.git
cd term-project-proto
```

### 13.2 가상환경 생성

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

### 13.3 패키지 설치

```bash
pip install -r requirements.txt
```

### 13.4 환경 변수 설정

macOS / Linux:

```bash
cp .env.example .env
```

Windows에서는 `.env.example`을 복사하여 `.env` 파일을 생성합니다.

이후 `.env`에 실제 값을 입력합니다.

```env
SECRET_KEY=<your-secret-key>
ALGORITHM=HS256
GEMINI_API_KEY=<your-gemini-api-key>
```

### 13.5 Python 문법 확인

```bash
python -m py_compile main.py ai_service.py auth.py database.py models.py
```

오류가 없다면 별도의 출력 없이 종료됩니다.

### 13.6 서버 실행

```bash
uvicorn main:app --reload
```

정상 실행 예:

```text
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

### 13.7 브라우저 접속

```text
http://127.0.0.1:8000
```

> ⚠️ 현재 PoC에서는 로컬 실행을 검증했습니다. 평가 시 요구되는 외부 네트워크 접근 가능한 서비스 URL은 팀 본 프로젝트의 배포 단계에서 추가해야 합니다.

---

## 14. 기능 검증 방법

### 회원가입

1. `/register` 접속
2. 새로운 사용자명 및 비밀번호 입력
3. 회원가입 실행
4. DB에 사용자 생성 여부 확인

### 로그인

1. `/login` 접속
2. 등록한 계정으로 로그인
3. JWT 발급
4. `/chat` 화면 이동 확인

### 챗봇

1. 로그인
2. 질문 입력
3. Gemini 응답 확인
4. DB에 질문/응답 저장 확인

### Context

연속된 질문을 통해 이전 대화를 참고하는지 확인합니다.

예:

```text
사용자: 배고파
사용자: 내가 아까 뭐라고 했어?
```

AI가 이전 질문을 참고하여 답변하면 최근 대화 Context가 정상적으로 전달된 것입니다.

### `request_id`

질문을 전송한 후 터미널에서 다음 로그를 확인합니다.

```text
request_received
ai_call_start
ai_call_success
db_save_success
```

네 로그의 `request_id`가 동일해야 합니다.

### DOM 렌더링

다음 문자열을 입력합니다.

```html
<h1>TEST</h1>
```

HTML 제목으로 렌더링되지 않고 문자열 그대로 보여야 합니다.

다음 문자열도 테스트할 수 있습니다.

```html
<img src=x onerror="alert('test')">
```

Alert가 실행되지 않고 문자열 그대로 표시되어야 합니다.

---

## 15. 팀 협업 및 역할 분담 계획 (Team Roadmap)

본 PoC를 프로젝트의 기술적 베이스라인으로 활용할 예정입니다.

아래 내용은 **현재 완료된 작업 실적이 아니라 팀 프로젝트 진행 계획**입니다.

| 구분                 | 담당 영역          | 예정 작업                                |
| ------------------ | -------------- | ------------------------------------ |
| **팀원 A (PoC 작성자)** | 시스템 아키텍처 / 백엔드 | PoC 기반 구조 정리, 핵심 API, DB ORM 및 전체 통합 |
| **팀원 B**           | AI 연동 / 안정성    | Prompt 개선, AI 예외 처리 및 Retry 전략 고도화   |
| **팀원 C**           | 인증 / 보안        | 인증 구조 검토, 접근 제어 및 보안 강화              |
| **팀원 D**           | Frontend UI/UX | UI 개선, 로딩 상태, 반응형 디자인 및 사용자 경험 개선    |

> 실제 최종 README에서는 팀원의 실제 이름, 실제 담당 기능, 실제 작업 내역을 Git 이력과 일치하도록 수정해야 합니다.

---

## 16. 팀 브랜치 전략 및 Git Workflow

본 프로젝트에서는 팀 개발 착수 후 다음과 같은 브랜치 전략을 적용할 예정입니다.

> ⚠️ 현재 PoC에서는 단일 작성자가 `main` 브랜치에서 구현했으므로 아래 브랜치 구조와 PR Workflow가 이미 적용되었다고 주장하지 않습니다.

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

### 브랜치 역할

| 브랜치          | 역할              |
| ------------ | --------------- |
| `main`       | 평가/배포 가능한 안정 버전 |
| `develop`    | 기능 개발 결과 통합     |
| `feat/<기능명>` | 기능 단위 개발        |
| `fix/<버그명>`  | 버그 수정           |

### 팀 프로젝트 적용 규칙

1. `main` 및 `develop`에 기능 개발을 직접 진행하지 않습니다.
2. `develop`에서 기능 브랜치를 생성합니다.
3. 기능 구현 후 GitHub PR을 생성합니다.
4. 코드 리뷰 후 `develop`에 Merge합니다.
5. 배포 가능한 버전만 최종적으로 `main`에 반영합니다.
6. 기능을 의미 있는 단위로 나누어 커밋합니다.
7. 최종 평가 전 팀원별 유의미한 커밋 10회 이상 여부를 확인합니다.

예:

```bash
git checkout develop
git pull origin develop
git checkout -b feat/chat-ui
```

작업 후:

```bash
git add .
git commit -m "feat: add chat loading state"
git push origin feat/chat-ui
```

이후 GitHub에서:

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

## 17. 현재 구현 상태

### PoC에서 완료

* [x] FastAPI 웹 서버
* [x] 회원가입
* [x] 로그인
* [x] PBKDF2 비밀번호 해싱
* [x] JWT Access Token 발급 및 API 인증
* [x] 로그인 사용자 전용 챗봇 API
* [x] SQLite / SQLAlchemy ORM
* [x] 사용자별 ChatLog 저장
* [x] `GET /api/me/chats`
* [x] 최근 3개 대화 Context
* [x] Gemini API 백엔드 연동
* [x] 5초 하드 타임아웃
* [x] 최대 3회 AI 호출 시도
* [x] Exponential Backoff
* [x] AI API 예외 처리
* [x] DB 저장 실패 시 `rollback()`
* [x] 주요 서버 이벤트 로깅
* [x] UUID 기반 `request_id` 추적
* [x] 사용자 질문 원문을 요청 로그에서 제외
* [x] 클라이언트 빈 입력 검증
* [x] Pydantic 질문 길이 검증
* [x] `textContent` 기반 안전한 메시지 렌더링
* [x] HTML/XSS 형태 입력이 실행되지 않는 것 확인
* [x] `.env` 기반 민감정보 관리
* [x] `.gitignore` 적용
* [x] 로컬 실행 검증

### 팀 본 프로젝트에서 추가 필요

* [ ] 외부 네트워크에서 접속 가능한 서비스 배포
* [ ] 평가용 실제 서비스 URL README 추가
* [ ] `main` / `develop` 브랜치 실제 운영
* [ ] 기능 단위 작업 브랜치 사용
* [ ] PR 기반 Merge 기록
* [ ] 팀원별 유의미한 커밋 10회 이상
* [ ] 실제 팀 구성원 역할 및 개인별 작업 요약 작성
* [ ] Git 이력과 README의 역할 설명 최종 대조
* [ ] 배포 환경에서 환경 변수 설정
* [ ] 배포 환경에서 AI / 인증 / DB / 로그 전체 기능 재검증

---

## 18. 최종 목표

현재 PoC의 목적은 개별 기술을 각각 구현하는 것에서 끝나는 것이 아니라 다음 전체 흐름이 실제로 동작하는지 검증하는 것입니다.

```text
사용자
  ↓
회원가입 / 로그인
  ↓
JWT 인증
  ↓
질문 입력
  ↓
FastAPI
  ↓
사용자 입력 검증
  ↓
최근 대화 Context 조회
  ↓
Gemini API 호출
  ↓
Timeout / Retry / Exception Handling
  ↓
AI 응답
  ↓
SQLite ChatLog 저장
  ↓
사용자별 대화 이력 조회
  ↓
웹 화면 출력
```

이 PoC를 기반으로 팀 프로젝트 단계에서는 협업 구조, PR 기반 개발, 외부 배포 및 최종 서비스 검증까지 확장하는 것을 목표로 합니다.
