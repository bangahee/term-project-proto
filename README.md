# 🤖 웹 기반 AI 챗봇 서비스 PoC (Term Project Prototype)

FastAPI와 OpenAI API를 기반으로 구현한 **사용자 인증, 대화 문맥 유지, 대화 이력 DB 저장·조회·삭제, AI API 예외 처리 및 외부 배포를 지원하는 웹 기반 AI 챗봇 서비스 프로토타입(PoC)**입니다.

팀 프로젝트의 기술적 베이스라인을 구축하기 위해 다음 전체 서비스 파이프라인이 실제 환경에서 정상적으로 연결되고 동작하는지 검증했습니다.

```text
Web UI
→ FastAPI Backend
→ JWT Authentication
→ Input Validation
→ Conversation Context
→ OpenAI API (GPT-5 nano)
→ AI Response
→ SQLite DB
→ User-specific Chat History
→ Railway Deployment
```

현재 PoC는 로컬 환경뿐 아니라 **Railway를 통한 외부 네트워크 배포까지 완료**했으며, 인증, AI 호출, DB 저장, 사용자별 로그 조회/삭제, 입력 검증, 예외 처리, DB 영속성, 대화 시간 표시 및 안전한 DOM 렌더링을 배포 환경에서 검증했습니다.

> ⚠️ **현재 단계 안내**
>
> 본 저장소의 현재 구현은 단일 작성자가 구축한 기술 검증용 PoC입니다.
>
> 서비스 배포와 핵심 기능 검증은 완료했지만, `main` / `develop` 브랜치 실제 운영, 기능 브랜치, PR 기반 Merge, 팀원별 유의미한 커밋 10회 이상 등의 **팀 협업 요구사항은 아직 완료된 것으로 간주하지 않습니다.**
>
> 해당 항목은 팀 본 프로젝트에서 실제 Git 이력과 함께 적용할 예정입니다.

---

# 1. 프로젝트 개요

## 1.1 문제 정의

AI 챗봇 서비스를 실제 웹 서비스로 운영하기 위해서는 웹 UI, 사용자 인증, AI API 호출, DB 저장, 예외 처리, 로그 추적 및 배포가 하나의 흐름으로 연결되어야 합니다.

본 프로젝트는 이러한 개별 기술을 통합하여 로그인 사용자가 질문을 입력하고 AI 응답을 받은 뒤, 자신의 대화 기록을 사용자별로 저장·조회·삭제할 수 있는 서비스를 구현하는 것을 목표로 합니다.

---

## 1.2 개발 목적

본 프로젝트의 목적은 개별 기술을 단순히 구현하는 것이 아니라 다음 기술 요소를 하나의 실제 웹 서비스로 연결하는 것입니다.

- **Backend**: FastAPI
- **Frontend**: HTML / CSS / JavaScript + Jinja2
- **Database**: SQLite + SQLAlchemy ORM
- **Authentication**: JWT + PBKDF2 Password Hashing
- **AI API**: OpenAI API
- **AI Model**: GPT-5 nano
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
OpenAI API 호출 (GPT-5 nano)
  ↓
Timeout / Retry / Exception Handling
  ↓
AI 응답
  ↓
SQLite DB 저장
  ↓
사용자별 대화 이력 조회 / 삭제
  ↓
KST 기준 날짜 / 시간 표시
  ↓
웹 화면 출력
```

---

## 1.3 타겟 사용자

로그인 후 개인별 대화 기록을 보관하면서 이전 대화를 바탕으로 연속성 있는 AI 대화를 진행하고자 하는 웹 사용자입니다.

---

## 1.4 핵심 시나리오

```text
1. 사용자가 웹 서비스에 접속한다.
2. 회원가입 시 비밀번호를 두 번 입력하여 일치 여부를 확인한다.
3. 회원가입 후 로그인한다.
4. 서버가 로그인 성공 시 JWT Access Token을 발급한다.
5. 사용자가 챗봇 화면에서 질문을 입력한다.
6. 입력창 하단에서 500자 기준 남은 입력 가능 글자 수를 확인할 수 있다.
7. FastAPI 서버가 JWT를 검증하여 로그인 사용자를 확인한다.
8. 입력값을 검증하고 해당 사용자의 최근 대화 기록을 조회한다.
9. 최근 대화를 Context로 구성하여 OpenAI API를 호출한다.
10. GPT-5 nano의 응답을 사용자에게 반환한다.
11. 질문과 AI 응답을 SQLite DB에 저장한다.
12. 저장된 생성 시각을 기반으로 메시지의 날짜와 시간을 화면에 표시한다.
13. 날짜가 변경되면 날짜 구분선을 표시한다.
14. 사용자는 자신의 기존 대화 기록을 다시 조회할 수 있다.
15. 필요한 경우 삭제 확인 후 자신의 전체 대화 기록을 삭제할 수 있다.
```

---

## 1.5 핵심 기능

1. 회원가입 및 로그인
2. 회원가입 비밀번호 재입력 확인
3. 로그인/회원가입 Enter 키 제출
4. PBKDF2 기반 비밀번호 해싱
5. JWT Access Token 기반 사용자 인증
6. 로그인 사용자 전용 챗봇 API
7. 사용자별 대화 이력 접근 제어
8. OpenAI API 서버 사이드 연동
9. GPT-5 nano 모델 사용
10. 최근 3개 대화를 활용한 Context 구성
11. 질문/응답 SQLite DB 누적 저장
12. 사용자 기준 대화 이력 조회
13. 사용자 자신의 전체 대화 이력 삭제
14. 삭제 전 되돌릴 수 없음을 알리는 확인 절차
15. 공백 입력 및 500자 초과 입력 검증
16. 입력창 500자 제한 및 실시간 남은 글자 수 표시
17. 메시지별 `HH:MM` 시간 표시
18. 날짜 변경 시 `YYYY년 M월 D일` 날짜 구분선 표시
19. DB UTC 시간의 KST(`Asia/Seoul`) 화면 변환
20. AI API 하드 타임아웃
21. 최대 3회 AI 호출 시도
22. Exponential Backoff 기반 재시도
23. AI API 실패 시 사용자 오류 안내
24. DB 저장 실패 시 `rollback()`
25. 주요 처리 단계 서버 로깅
26. UUID 기반 `request_id` 요청 추적
27. 사용자 질문 원문을 서버 요청 로그에서 제외
28. `textContent` 기반 안전한 DOM 렌더링
29. Railway 외부 배포
30. Railway Volume을 통한 SQLite DB 영속성 확보
31. 재배포 이후 사용자 및 대화 기록 유지 검증

---

# 2. 배포 서비스

## 2.1 외부 접속 URL

현재 서비스는 Railway에 배포되어 있으며 외부 네트워크에서 접근할 수 있습니다.

**배포 URL**

```text
https://term-project-proto-production.up.railway.app
```

평가자는 위 URL을 통해 다음 전체 흐름을 직접 확인할 수 있습니다.

```text
회원가입
→ 로그인
→ 챗봇 질문
→ AI 응답
→ 날짜 / 시간 표시
→ 대화 이력 확인
→ 대화 기록 삭제
```

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
│ OpenAI API   │   │ Railway Volume   │
│ GPT-5 nano   │   │                  │
│ AI Response  │   │ SQLite DB        │
└──────────────┘   │ chatbot.db       │
                   └──────────────────┘
```

Railway 서비스의 컨테이너가 재배포되더라도 SQLite 데이터가 사라지지 않도록 Persistent Volume을 사용합니다.

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
Browser localStorage 저장
```

백엔드의 보호된 API에서는 JWT를 다시 검증하므로 단순히 프론트엔드 화면을 숨기는 방식에 의존하지 않습니다.

---

## Step 3. 회원가입 UX

회원가입 화면에서는 다음 기능을 적용했습니다.

- 아이디 입력
- 비밀번호 입력
- 비밀번호 확인 입력
- 비밀번호 일치 여부 검증
- 최소 입력 길이 사전 검증
- Enter 키 회원가입
- FastAPI/Pydantic 오류 메시지 처리
- `[object Object]` 형태의 오류 출력 방지
- 요청 중 버튼 비활성화를 통한 중복 요청 방지

비밀번호와 비밀번호 확인 값이 일치하지 않으면 서버에 회원가입 요청을 보내기 전에 클라이언트에서 차단합니다.

---

## Step 4. 로그인 UX

로그인 화면에서는 HTML `<form>`의 `submit` 이벤트를 사용합니다.

따라서 다음 두 동작이 동일한 로그인 함수로 연결됩니다.

```text
로그인 버튼 클릭
       ↓
form submit
       ↓
login()

Enter 키
       ↓
form submit
       ↓
login()
```

로그인 요청 중에는 버튼을 일시적으로 비활성화하여 중복 요청을 방지합니다.

또한 FastAPI의 오류 응답 구조를 처리하여 잘못된 입력이 `[object Object]`로 출력되지 않도록 구성했습니다.

---

## Step 5. Web UI 및 FastAPI Routing

HTML 템플릿은 다음과 같이 분리했습니다.

```text
templates/
├── login.html
├── register.html
└── chat.html
```

HTML 페이지 Route:

```text
GET /
GET /login
GET /register
GET /chat
```

주요 API:

```text
POST   /api/auth/register
POST   /api/auth/login
POST   /api/chat
GET    /api/me/chats
DELETE /api/me/chats
```

---

## Step 6. OpenAI API 연동

`ai_service.py`에서 OpenAI API를 서버 사이드에서 호출합니다.

현재 AI 모델은 다음 모델을 사용합니다.

```text
gpt-5-nano
```

API 호출 구조:

```text
Browser
   ↓
FastAPI
   ↓
OPENAI_API_KEY
   ↓
OpenAI API
   ↓
GPT-5 nano
   ↓
FastAPI
   ↓
Browser
```

`OPENAI_API_KEY`는 FastAPI 서버의 환경 변수로 관리되며 브라우저 JavaScript에 전달하지 않습니다.

따라서 사용자가 브라우저에서 OpenAI API Key를 직접 확인할 수 없도록 구성했습니다.

---

## Step 7. 대화 Context 구성

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

AI에 전달할 때는 대화 순서를 고려하여 이전 질문/응답과 현재 질문을 Context로 구성합니다.

```text
이전 User 질문
→ 이전 AI 응답
→ 다음 User 질문
→ 다음 AI 응답
→ 현재 User 질문
```

이를 통해 모든 과거 대화를 무제한으로 AI에 전달하지 않으면서 최소한의 대화 문맥을 유지합니다.

---

## Step 8. AI Timeout

AI API가 장시간 응답하지 않는 상황에서 서버가 무한 대기하지 않도록 명시적인 타임아웃을 적용했습니다.

현재 설정:

```text
TIMEOUT_SECONDS = 20.0
```

처리 구조:

```text
OpenAI API
    ↓
20초 이내 응답?
 ┌──┴───┐
Yes     No
 │       │
응답    Timeout
         ↓
       Retry
```

외부 AI 서비스의 응답 지연 가능성을 고려하여 일정 시간 이상 응답이 없으면 해당 시도를 종료하고 재시도 또는 오류 안내를 수행합니다.

---

## Step 9. Retry 및 Exponential Backoff

일시적인 API 장애에 대응하기 위해 최대 3회의 AI 호출을 시도하도록 구성했습니다.

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

일시적인 API 오류가 발생하더라도 FastAPI 서버 자체가 비정상 종료되지 않도록 예외를 처리합니다.

---

## Step 10. DB 저장 및 Rollback

AI 응답을 받은 후 사용자 질문과 응답을 `ChatLog`에 저장합니다.

```text
AI 응답
   ↓
ChatLog 생성
   ↓
db.add()
   ↓
db.commit()
   ↓
db.refresh()
```

DB 저장 중 오류가 발생하면:

```python
db.rollback()
```

을 실행하여 실패한 트랜잭션 상태를 정리합니다.

---

## Step 11. 사용자별 대화 기록 조회

다음 API를 통해 현재 로그인한 사용자의 대화 기록만 조회합니다.

```text
GET /api/me/chats
```

조회 조건:

```text
JWT
 ↓
current_user
 ↓
current_user.id
 ↓
ChatLog.user_id == current_user.id
 ↓
해당 사용자의 기록만 반환
```

따라서 다른 사용자의 대화 기록은 조회할 수 없습니다.

---

## Step 12. 사용자별 대화 기록 삭제

대화 기록이 계속 누적되어 화면이 복잡해지는 문제를 개선하기 위해 전체 대화 삭제 기능을 추가했습니다.

API:

```text
DELETE /api/me/chats
```

삭제 조건:

```text
JWT 인증
   ↓
current_user.id 확인
   ↓
ChatLog.user_id == current_user.id
   ↓
현재 사용자의 ChatLog만 삭제
```

다른 사용자의 기록에는 영향을 주지 않습니다.

삭제 성공 시 서버 로그에 다음 정보를 기록합니다.

```text
chat_history_delete_success
user_id
deleted_count
```

실패 시:

```text
chat_history_delete_failed
```

를 기록하고 DB 트랜잭션을 `rollback()`합니다.

또한 사용자가 실수로 기록을 삭제하는 것을 방지하기 위해 프론트엔드에서 **삭제 후 되돌릴 수 없음을 안내하고 확인을 받은 후 삭제 요청을 수행**하도록 구성했습니다.

---

## Step 13. 채팅 입력 길이 표시

백엔드에서는 Pydantic을 통해 질문을 최대 500자로 제한합니다.

```python
question: str = Field(
    ...,
    min_length=1,
    max_length=500
)
```

프론트엔드에서도 동일한 제한을 적용합니다.

```html
<input
    type="text"
    id="question"
    maxlength="500"
>
```

사용자가 입력할 때마다 현재 입력 길이를 계산하여 남은 글자 수를 실시간으로 표시합니다.

```text
500자 남음
499자 남음
498자 남음
...
0자 남음
```

따라서 프론트엔드 UX와 백엔드 검증이 모두 동일한 500자 기준을 사용합니다.

---

## Step 14. 메시지 날짜 및 시간 표시

각 `ChatLog`에는 `created_at`이 저장됩니다.

```text
ChatLog
├── id
├── user_id
├── question
├── response
└── created_at
```

`GET /api/me/chats` 및 `POST /api/chat` 응답을 통해 생성 시각을 프론트엔드에 전달합니다.

하나의 `ChatLog`는 하나의 사용자 질문과 하나의 AI 응답을 하나의 대화 단위로 저장하므로, 저장된 대화 이력을 출력할 때 질문과 응답은 동일한 `created_at`을 사용합니다.

화면에서는 각 메시지 옆에 시간을 표시합니다.

```text
사용자: 안녕                    15:01
챗봇: 안녕하세요!               15:01
```

날짜가 변경되면 새로운 날짜 구분선을 추가합니다.

```text
──────── 2026년 8월 14일 ────────

사용자: 안녕                    23:41
챗봇: 안녕하세요!               23:41

──────── 2026년 8월 15일 ────────

사용자: 오늘 뭐했지?             15:01
챗봇: 이전 대화를 기준으로...     15:01
```

같은 날짜의 메시지가 계속되는 경우 날짜 구분선을 반복해서 출력하지 않습니다.

---

## Step 15. UTC → KST 시간 변환

DB의 `created_at`은 `datetime.utcnow()`을 기반으로 생성되므로 UTC 기준 시간을 저장합니다.

예:

```text
DB / API
2026-08-15T06:01:00
```

프론트엔드에서는 timezone 정보가 없는 DB timestamp를 UTC로 해석한 뒤 `Asia/Seoul` timezone을 적용합니다.

```text
UTC 06:01
   ↓
Asia/Seoul
   ↓
KST 15:01
```

따라서 사용자 질문을 브라우저에서 즉시 표시하는 시간과 DB에서 다시 불러온 AI 응답 시간이 서로 9시간 차이나는 문제를 방지합니다.

날짜 구분선 역시 KST 기준으로 계산하기 때문에 한국 시간 자정 전후의 대화도 올바른 날짜로 구분됩니다.

---

## Step 16. request_id 기반 로그 추적

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

따라서 동시에 여러 요청이 발생하더라도 하나의 요청 처리 흐름을 추적할 수 있습니다.

사용자의 실제 질문 내용은 서버 요청 로그에 기록하지 않고 다음 정보만 기록합니다.

```text
request_id
user_id
question_length
```

---

## Step 17. 안전한 DOM 렌더링

`chat.html`에서는 사용자 질문과 AI 응답을 출력할 때 외부 문자열을 `innerHTML`로 직접 삽입하지 않습니다.

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
│ KST Time Display             │
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
│ - Chat History Delete        │
└───────┬─────────────┬────────┘
        │             │
        ▼             ▼
┌──────────────┐ ┌─────────────────────┐
│   auth.py    │ │    ai_service.py    │
│              │ │                     │
│ - PBKDF2     │ │ - Context           │
│ - JWT        │ │ - OpenAI API        │
│              │ │ - GPT-5 nano        │
│              │ │ - Timeout           │
│              │ │ - Retry / Backoff   │
└──────────────┘ └──────────┬──────────┘
                            │
                            ▼
                  ┌─────────────────────┐
                  │     OpenAI API      │
                  │     GPT-5 nano      │
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
| `main.py` | FastAPI 앱, 페이지/API 라우팅, 입력 검증, JWT 인증 연결, `request_id` 생성, DB 저장/조회/삭제, 생성 시각 반환, 서버 로깅 |
| `auth.py` | PBKDF2 비밀번호 해싱, JWT 생성 및 인증 사용자 조회 |
| `ai_service.py` | OpenAI API, GPT-5 nano 호출, Context 구성, Timeout, Retry, Exponential Backoff, AI 예외 처리 |
| `database.py` | SQLite / SQLAlchemy 엔진 및 DB 세션 관리 |
| `models.py` | `User`, `ChatLog` ORM 모델 및 `created_at` 관리 |
| `templates/login.html` | 로그인 UI, Enter 제출, 로그인 오류 처리 |
| `templates/register.html` | 회원가입 UI, 비밀번호 확인, Enter 제출, 검증 오류 처리 |
| `templates/chat.html` | 챗봇 UI, 500자 입력 제한/카운터, 대화 이력 출력/삭제, 날짜 구분선, KST 시간 표시, 안전한 DOM 렌더링 |
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

> 비밀번호 확인 값은 프론트엔드에서 비밀번호 일치 여부를 확인하기 위한 값이며, 일치 확인 후 실제 API에는 `username`과 `password`만 전달합니다.

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
  "response": "FastAPI는 비동기 처리와 Pydantic 기반 입력 검증 등을 지원합니다.",
  "time": "2026-08-15T06:01:30.123456"
}
```

`time`은 저장된 `ChatLog.created_at`을 ISO 형식으로 반환한 값이며, 웹 화면에서는 이를 KST 기준으로 변환하여 표시합니다.

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
    "time": "2026-08-15T06:01:30.123456"
  }
]
```

현재 로그인한 사용자 자신의 대화 기록만 반환합니다.

`time`은 DB에 저장된 생성 시각이며, 프론트엔드에서는 `Asia/Seoul` 기준으로 변환하여 날짜 구분선과 메시지 시간을 표시합니다.

---

## 6.5 내 대화 이력 전체 삭제

### `DELETE /api/me/chats`

로그인이 필요한 API입니다.

Header:

```text
Authorization: Bearer <access_token>
```

Response 예시:

```json
{
  "message": "대화 기록이 삭제되었습니다.",
  "deleted_count": 5
}
```

현재 로그인한 사용자의 `ChatLog`만 삭제합니다.

다른 사용자의 대화 기록은 삭제되지 않습니다.

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
POST   /api/chat
GET    /api/me/chats
DELETE /api/me/chats
```

백엔드 API에서 JWT를 직접 검증하므로 프론트엔드의 페이지 이동 제한에만 의존하지 않습니다.

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

각 `ChatLog`에는 최소 다음 정보가 저장됩니다.

- 사용자 식별자 `user_id`
- 질문 `question`
- AI 응답 `response`
- 생성 시각 `created_at`

따라서 사용자 기준으로 대화 이력을 조회하고 추적할 수 있습니다.

`created_at`은 대화 생성 시각을 기록하며 API를 통해 프론트엔드로 전달되어 메시지 날짜 및 시간 표시에도 사용됩니다.

---

# 9. DB 영속성

Railway 배포 환경에서 SQLite DB를 영속적으로 유지하기 위해 Persistent Volume을 사용합니다.

```text
Railway:

DATABASE_URL
      ↓
sqlite:////data/chatbot.db
      ↓
/data
      ↓
Railway Persistent Volume
```

이를 통해 애플리케이션이 재배포되어 컨테이너가 교체되더라도 DB 데이터가 유지되도록 구성했습니다.

실제 검증 과정:

```text
1. 테스트 계정 생성
2. 챗봇 대화 생성
3. ChatLog 저장 확인
4. Railway Redeploy
5. 기존 테스트 계정으로 다시 로그인
6. 기존 대화 기록 조회
```

재배포 이후에도 기존 계정과 대화 기록이 그대로 조회되는 것을 확인했습니다.

---

# 10. 입력 검증

챗봇 질문에는 클라이언트 및 서버 사이드 입력 검증을 적용했습니다.

## 10.1 공백 입력

공백만 입력한 질문:

```json
{
  "question": "     "
}
```

배포 환경 테스트 결과:

```text
HTTP 422 Unprocessable Content
```

```text
Value error, 질문은 공백일 수 없습니다.
```

---

## 10.2 최대 길이

질문 최대 길이는 **500자**입니다.

501자를 전달한 경우:

```text
HTTP 422 Unprocessable Content
```

```text
String should have at most 500 characters
```

가 반환되는 것을 확인했습니다.

따라서 프론트엔드 검증뿐 아니라 직접 API 요청을 보내더라도 서버에서 잘못된 입력을 차단합니다.

---

## 10.3 실시간 남은 글자 수

웹 UI에서는 `maxlength="500"`을 적용하고 현재 입력된 글자 수를 기반으로 남은 입력 가능 글자 수를 표시합니다.

```text
질문 입력 전
500자 남음

100자 입력
400자 남음

500자 입력
0자 남음
```

이 기능은 사용자 편의를 위한 프론트엔드 UX이며, 실제 보안 및 입력 제한은 FastAPI의 Pydantic 검증에서도 다시 수행됩니다.

---

# 11. 메시지 날짜 및 시간

## 11.1 생성 시각 저장

`ChatLog` 생성 시 `created_at` 필드에 생성 시각을 저장합니다.

```text
사용자 질문
   ↓
AI 응답
   ↓
ChatLog
   ├── question
   ├── response
   └── created_at
```

---

## 11.2 메시지 시간 표시

화면에서는 각 메시지 옆에 `HH:MM` 형식으로 시간을 표시합니다.

```text
사용자: 안녕                     15:01
챗봇: 안녕하세요!                15:01
```

기존 DB 이력을 다시 불러온 경우 질문과 해당 AI 응답은 같은 `ChatLog`에 속하므로 동일한 `created_at`을 사용합니다.

---

## 11.3 날짜 구분선

날짜가 변경되는 지점에만 날짜 구분선을 표시합니다.

```text
──────── 2026년 8월 14일 ────────

사용자: 안녕                     23:41
챗봇: 안녕하세요!                23:41

──────── 2026년 8월 15일 ────────

사용자: 오늘 뭐했지?              15:01
챗봇: 이전 대화를 기준으로...      15:01
```

같은 날짜에 여러 메시지가 존재하더라도 날짜 구분선은 반복되지 않습니다.

---

## 11.4 KST 변환

DB 생성 시각은 UTC를 기준으로 저장합니다.

프론트엔드에서는 이를 `Asia/Seoul` timezone으로 변환하여 KST로 표시합니다.

```text
DB:
2026-08-15 06:01 UTC

        ↓

Web UI:
2026년 8월 15일 15:01 KST
```

이를 통해 브라우저에서 즉시 표시한 사용자 메시지와 DB에서 반환된 챗봇 메시지가 서로 다른 시간대로 표시되는 문제를 방지했습니다.

---

# 12. 운영 안정성 및 예외 처리

## 12.1 AI Timeout

OpenAI API 호출에는 명시적인 하드 타임아웃을 적용했습니다.

현재 설정:

```text
TIMEOUT_SECONDS = 20.0
```

```text
OpenAI API
    ↓
20초 초과
    ↓
Timeout
    ↓
Retry
```

---

## 12.2 Exponential Backoff

```text
1차 호출 실패
 ↓
2초 대기
 ↓
2차 시도
 ↓
실패
 ↓
4초 대기
 ↓
3차 시도
 ↓
최종 실패
 ↓
사용자 오류 안내
```

최종 실패 시 서버 프로세스를 종료하지 않고 사용자에게 오류 안내를 반환합니다.

---

## 12.3 DB 실패 처리

```text
db.add()
   ↓
db.commit()
   ↓
실패
   ↓
db.rollback()
```

DB 저장 실패 시 `rollback()`을 실행하여 실패한 트랜잭션 상태를 정리합니다.

대화 기록 삭제 중 DB 오류가 발생한 경우에도 동일하게 `rollback()`을 수행합니다.

---

# 13. 서버 로그

AI 채팅 처리 과정에서 다음과 같은 주요 이벤트를 기록합니다.

```text
request_received
ai_call_start
ai_call_success
ai_call_failed
ai_call_retry
db_save_success
db_save_failed
```

대화 삭제 과정에서는 다음 이벤트도 기록합니다.

```text
chat_history_delete_success
chat_history_delete_failed
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

# 14. 대화 로그 확인 및 관리 가이드

## 14.1 웹 화면

로그인 후 `/chat` 페이지에 접속하면:

```text
GET /api/me/chats
```

를 호출하여 현재 로그인한 사용자의 기존 대화 기록을 화면에 표시합니다.

기존 기록은 날짜별로 구분되며 각 메시지에는 KST 기준 시간이 표시됩니다.

사용자는 대화 기록 삭제 기능을 통해 자신의 대화를 정리할 수 있습니다.

삭제 전에는 복구할 수 없다는 경고를 표시하여 사용자의 확인을 받습니다.

---

## 14.2 API 조회

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

---

## 14.3 API 삭제

```bash
curl -i -X DELETE \
  https://term-project-proto-production.up.railway.app/api/me/chats \
  -H "Authorization: Bearer $TOKEN"
```

성공 시:

```text
200 OK
```

예:

```json
{
  "message": "대화 기록이 삭제되었습니다.",
  "deleted_count": 5
}
```

---

# 15. 프론트엔드 메시지 렌더링 보안

채팅 메시지를 화면에 출력할 때 `innerHTML` 문자열 삽입 대신 DOM API와 `textContent`를 사용합니다.

```javascript
const messageText = document.createElement('span');
messageText.textContent = String(message ?? '');
```

## 15.1 HTML 문자열 테스트

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

## 15.2 XSS 형태 입력 테스트

입력:

```html
<img src=x onerror="alert('test')">
```

배포 환경에서 테스트한 결과:

- 문자열 그대로 표시
- 실제 `<img>` 요소 생성 안 됨
- `onerror` 실행 안 됨
- JavaScript Alert 발생 안 함
- 문자열 자체는 AI 질문으로 전달 가능

따라서 채팅 메시지 출력 과정에서 사용자 입력을 HTML 코드로 직접 해석하지 않도록 구성했습니다.

---

# 16. 환경 변수 및 민감정보 관리

민감정보는 소스 코드에 직접 작성하지 않습니다.

필요한 환경 변수:

```text
SECRET_KEY
ALGORITHM
OPENAI_API_KEY
DATABASE_URL
```

실제 Secret 값은 README 또는 Git 저장소에 작성하지 않습니다.

---

## 16.1 로컬 환경 변수

로컬 개발 환경에서는 `.env` 파일을 사용합니다.

예:

```env
SECRET_KEY=your_secret_key_here
ALGORITHM=HS256
OPENAI_API_KEY=your_openai_api_key_here
DATABASE_URL=sqlite:///./chatbot.db
```

---

## 16.2 Railway 환경 변수

Railway에서는 Variables에 다음 환경 변수를 등록합니다.

```text
SECRET_KEY
ALGORITHM
OPENAI_API_KEY
DATABASE_URL
```

Railway Persistent Volume을 `/data`에 연결한 경우:

```env
DATABASE_URL=sqlite:////data/chatbot.db
```

환경별 DB 위치:

```text
Local
DATABASE_URL=sqlite:///./chatbot.db

Railway
DATABASE_URL=sqlite:////data/chatbot.db
```

---

## 16.3 `.env.example`

저장소의 `.env.example`에는 실제 Secret 대신 예시 값을 사용합니다.

```env
SECRET_KEY=your_secret_key_here
ALGORITHM=HS256
OPENAI_API_KEY=your_openai_api_key_here

# 로컬에서는 생략 가능
# Railway 배포 예시:
DATABASE_URL=sqlite:////data/chatbot.db
```

로컬에서 `DATABASE_URL`을 생략하면 `database.py`의 기본값:

```text
sqlite:///./chatbot.db
```

을 사용합니다.

---

## 16.4 `.gitignore`

예:

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

- OpenAI API Key
- JWT Secret Key
- 로컬 SQLite DB
- Python 가상환경
- Python Cache

---

# 17. 로컬 실행 방법

## 17.1 Clone

```bash
git clone https://github.com/bangahee/term-project-proto.git
cd term-project-proto
```

---

## 17.2 가상환경 생성

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

## 17.3 Dependency 설치

```bash
pip install -r requirements.txt
```

주요 Dependency:

```text
fastapi
uvicorn
sqlalchemy
pydantic
python-dotenv
openai
httpx
passlib
python-jose[cryptography]
jinja2
python-multipart
pytest
```

---

## 17.4 환경 변수 설정

macOS / Linux:

```bash
cp .env.example .env
```

`.env` 파일을 열어 실제 값을 입력합니다.

```env
SECRET_KEY=<your-secret-key>
ALGORITHM=HS256
OPENAI_API_KEY=<your-openai-api-key>
DATABASE_URL=sqlite:///./chatbot.db
```

> 실제 OpenAI API Key는 GitHub에 Commit하지 않습니다.

---

## 17.5 테스트

```bash
pytest -v
```

입력 검증 테스트 예:

```text
tests/test_validation.py::test_valid_question PASSED
tests/test_validation.py::test_whitespace_question_rejected PASSED
tests/test_validation.py::test_question_too_long_rejected PASSED
```

---

## 17.6 서버 실행

```bash
uvicorn main:app --reload
```

브라우저:

```text
http://127.0.0.1:8000
```

---

# 18. Railway 배포

현재 서비스는 Railway에서 실행됩니다.

배포 URL:

```text
https://term-project-proto-production.up.railway.app
```

## 18.1 배포 환경 변수

Railway에서 다음 환경 변수를 설정합니다.

```text
SECRET_KEY
ALGORITHM
OPENAI_API_KEY
DATABASE_URL
```

실제 Secret 값은 GitHub에 저장하지 않습니다.

Railway의 DB 경로:

```env
DATABASE_URL=sqlite:////data/chatbot.db
```

---

## 18.2 Persistent Volume

```text
FastAPI
   ↓
DATABASE_URL
   ↓
/data/chatbot.db
   ↓
Railway Persistent Volume
```

따라서 재배포 이후에도 사용자 및 `ChatLog` 데이터를 유지할 수 있습니다.

---

# 19. Production 검증 결과

Railway에 배포한 실제 서비스를 대상으로 다음 기능을 검증했습니다.

| 테스트 | 결과 |
| --- | --- |
| 외부 서비스 URL 접근 | ✅ |
| 회원가입 | ✅ |
| 회원가입 비밀번호 확인 | ✅ |
| 회원가입 Enter 제출 | ✅ |
| 로그인 | ✅ |
| 로그인 Enter 제출 | ✅ |
| 올바른 로그인 → JWT 발급 | ✅ |
| 잘못된 로그인 → `401` | ✅ |
| 로그인/회원가입 오류 메시지 처리 | ✅ |
| `/api/chat` 인증 없음 → `401` | ✅ |
| `/api/me/chats` 인증 없음 → `401` | ✅ |
| JWT + `/api/me/chats` → `200` | ✅ |
| 사용자별 기존 대화 조회 | ✅ |
| 사용자별 대화 기록 삭제 | ✅ |
| OpenAI API 연동 | ✅ |
| GPT-5 nano AI 응답 | ✅ |
| AI API 실패 시 서버 유지 | ✅ |
| ChatLog DB 저장 | ✅ |
| 공백 질문 → `422` | ✅ |
| 501자 질문 → `422` | ✅ |
| 500자 프론트엔드 입력 제한 | ✅ |
| 실시간 남은 글자 수 표시 | ✅ |
| 메시지별 시간 표시 | ✅ |
| 날짜별 대화 구분선 | ✅ |
| UTC → KST 화면 변환 | ✅ |
| HTML 문자열 안전 출력 | ✅ |
| XSS 형태 입력 실행 방지 | ✅ |
| Railway 재배포 | ✅ |
| 재배포 후 기존 사용자 유지 | ✅ |
| 재배포 후 기존 ChatLog 유지 | ✅ |

---

# 20. Production 검증 명령어

## 20.1 인증 없는 챗봇 접근

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

## 20.2 인증 없는 로그 조회

```bash
curl -i \
  https://term-project-proto-production.up.railway.app/api/me/chats
```

예상:

```text
401 Unauthorized
```

---

## 20.3 로그인

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

## 20.4 JWT 저장

```bash
TOKEN='<access_token>'
```

---

## 20.5 인증된 로그 조회

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

## 20.6 인증된 챗봇 요청

```bash
curl -i -X POST \
  https://term-project-proto-production.up.railway.app/api/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"question":"안녕"}'
```

예상:

```text
200 OK
```

응답에는 질문, AI 응답 및 DB 생성 시각이 포함됩니다.

```json
{
  "question": "안녕",
  "response": "안녕하세요!",
  "time": "2026-08-15T06:01:30.123456"
}
```

---

## 20.7 공백 입력 검증

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

## 20.8 501자 입력 검증

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

## 20.9 대화 기록 삭제

```bash
curl -i -X DELETE \
  https://term-project-proto-production.up.railway.app/api/me/chats \
  -H "Authorization: Bearer $TOKEN"
```

예상:

```text
200 OK
```

삭제 후 다시:

```bash
curl -i \
  https://term-project-proto-production.up.railway.app/api/me/chats \
  -H "Authorization: Bearer $TOKEN"
```

를 실행하여 해당 사용자의 기록이 삭제되었는지 확인할 수 있습니다.

---

# 21. 팀 협업 및 역할 분담 계획

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

# 22. Git Branch / PR 전략

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

## 22.1 브랜치 역할

| Branch | 역할 |
| --- | --- |
| `main` | 평가 및 배포 가능한 안정 버전 |
| `develop` | 기능 개발 결과 통합 |
| `feat/<기능명>` | 기능 단위 개발 |
| `fix/<버그명>` | 버그 수정 |

---

## 22.2 팀 프로젝트 Git 규칙

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

작업 후:

```bash
git add .
git commit -m "feat: add chat loading state"
git push origin feat/chat-ui
```

---

# 23. 현재 구현 상태

## 23.1 PoC 완료

- [x] FastAPI 웹 서버
- [x] HTML / CSS / JavaScript + Jinja2 Frontend
- [x] 회원가입
- [x] 비밀번호 확인 입력
- [x] 회원가입 Enter 제출
- [x] 로그인
- [x] 로그인 Enter 제출
- [x] 회원가입/로그인 오류 메시지 개선
- [x] PBKDF2 비밀번호 해싱
- [x] JWT Access Token
- [x] 로그인 사용자 전용 챗봇 API
- [x] 사용자별 대화 이력 접근 제어
- [x] SQLite
- [x] SQLAlchemy ORM
- [x] User / ChatLog 1:N 구조
- [x] 사용자별 ChatLog 저장
- [x] `GET /api/me/chats`
- [x] `DELETE /api/me/chats`
- [x] 대화 기록 삭제 확인 절차
- [x] 최근 3개 대화 Context
- [x] OpenAI API Backend 연동
- [x] GPT-5 nano 모델
- [x] AI API 하드 타임아웃
- [x] 최대 3회 AI 호출
- [x] Exponential Backoff
- [x] AI API 예외 처리
- [x] DB 저장 실패 `rollback()`
- [x] DB 삭제 실패 `rollback()`
- [x] 주요 서버 이벤트 로깅
- [x] UUID 기반 `request_id`
- [x] 사용자 질문 원문 요청 로그 제외
- [x] 클라이언트 입력 검증
- [x] 서버 공백 입력 검증
- [x] 500자 최대 길이 검증
- [x] 500자 프론트엔드 입력 제한
- [x] 실시간 남은 글자 수 표시
- [x] ChatLog 생성 시각 저장
- [x] `/api/chat` 생성 시각 반환
- [x] `/api/me/chats` 생성 시각 반환
- [x] 메시지별 `HH:MM` 시간 표시
- [x] 날짜 변경 시 날짜 구분선 표시
- [x] UTC → KST(`Asia/Seoul`) 화면 변환
- [x] Pytest 입력 검증 테스트
- [x] `textContent` 기반 안전한 메시지 렌더링
- [x] HTML 형태 입력 안전 출력 검증
- [x] XSS 형태 입력 실행 방지 검증
- [x] `.env` 기반 민감정보 관리
- [x] `.env.example`
- [x] `.gitignore`
- [x] 로컬 실행 검증
- [x] Railway 외부 배포
- [x] 외부 접근 가능한 서비스 URL
- [x] Railway 환경 변수 설정
- [x] `OPENAI_API_KEY` Railway 환경 변수 설정
- [x] 배포 환경 회원가입/로그인 검증
- [x] 배포 환경 JWT 인증 검증
- [x] 배포 환경 OpenAI API 검증
- [x] 배포 환경 ChatLog 저장/조회 검증
- [x] 배포 환경 입력 검증
- [x] Railway Persistent Volume
- [x] Railway 재배포 후 DB 데이터 유지 검증

---

## 23.2 팀 본 프로젝트에서 추가 필요

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

# 24. 평가 요구사항 대응 현황

| 요구사항 | 현재 상태 |
| --- | --- |
| FastAPI 웹 서비스 | ✅ PoC 완료 |
| 질문 입력 Web UI | ✅ |
| 같은 화면에서 AI 응답 확인 | ✅ |
| 회원가입 | ✅ |
| 로그인 | ✅ |
| 인증 상태 기반 접근 제어 | ✅ |
| 챗봇 로그인 사용자 전용 | ✅ |
| 서버에서 AI API 호출 | ✅ OpenAI API |
| API Key 서버 관리 | ✅ |
| 최소 Context 전략 | ✅ 최근 3개 대화 |
| 질문/응답 DB 누적 저장 | ✅ |
| 사용자 식별 정보 저장 | ✅ |
| 생성 시각 저장 | ✅ |
| 사용자 기준 로그 조회 | ✅ |
| 사용자 기준 로그 삭제 | ✅ |
| 500자 입력 제한 | ✅ |
| 남은 글자 수 표시 | ✅ |
| 메시지 생성 시각 표시 | ✅ |
| 날짜별 대화 구분 | ✅ |
| KST 기준 화면 표시 | ✅ |
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

# 25. 최종 목표

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
OpenAI API
  ↓
GPT-5 nano
  ↓
Timeout / Retry / Backoff
  ↓
AI 응답
  ↓
SQLite ChatLog 저장
  ↓
created_at 저장
  ↓
Persistent Volume
  ↓
사용자별 대화 이력 조회 / 삭제
  ↓
UTC → KST 변환
  ↓
날짜 구분선 + 메시지 시간 표시
  ↓
안전한 DOM 렌더링
  ↓
웹 화면 출력
```

따라서 현재 PoC에서는 **Web + Authentication + DB + AI API + Context + Logging + Error Handling + Deployment + Persistence + Time Handling**의 핵심 통합 흐름을 구축했습니다.

또한 회원가입 비밀번호 확인, Enter 키 제출, 500자 입력 제한 및 남은 글자 수 표시, 대화 기록 삭제, 날짜별 대화 구분, KST 기준 메시지 시간 표시, 안전한 DOM 렌더링 등 실제 사용 과정에서 필요한 UX 및 보안 요소를 추가했습니다.

다음 단계에서는 이 PoC를 팀 프로젝트의 기술적 베이스라인으로 사용하고, 실제 팀원들과 `develop` 및 기능 브랜치, PR 기반 Merge, 팀원별 Commit 이력을 구축하여 최종 Term Project로 확장하는 것을 목표로 합니다.