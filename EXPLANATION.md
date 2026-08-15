# 1. 먼저, 이 프로젝트는 무엇인가?

**웹 애플리케이션**을 만드는 프로젝트

이 서비스에는 여러 프로그램과 시스템이 연결되어 있다.

```text
┌──────────── 사용자의 컴퓨터 ────────────┐

브라우저
  │
  │ HTML / CSS / JavaScript
  ▼
웹사이트
  │
  │ HTTP Request
  ▼

────────────── 인터넷 ──────────────

┌──────────── Railway 서버 ─────────────┐

FastAPI
  │
  ├── 인증
  ├── 입력 검증
  ├── 데이터베이스
  └── AI Service
         │
         │ API Request
         ▼
     OpenAI Server
         │
         ▼
     GPT-5 nano

FastAPI
  │
  ▼
HTTP Response

────────────── 인터넷 ──────────────
  │
  ▼
브라우저가 AI 답변 표시
```

### 중요한 구분

```text
브라우저 ≠ 서버
OpenAI ≠ 내 서버
SQLite ≠ 서버
```

**FastAPI**
= 프로젝트의 **백엔드 서버 애플리케이션**

**Railway**
= FastAPI를 실제 인터넷에서 실행시키는 **배포 환경**

---

# 2. Client와 Server

## Client

**Client = 무언가를 요청하는 쪽**

해당 프로젝트에서는:

```text
브라우저 = Client
```

예:

```text
"로그인 페이지를 보여줘."
"이 질문을 AI에게 보내줘."
```

## Server

**Server = Client의 요청을 받고 처리한 뒤 결과를 반환하는 쪽**

해당 프로젝트에서는:

```text
FastAPI = Server
```

### 전체 구조

```text
Client                    Server

Browser ─── Request ───→ FastAPI
Browser ←── Response ─── FastAPI
```

### 식당으로 비유

```text
손님 = Client
식당 / 직원 = Server
주문 = Request
음식 = Response
```

---

# 3. Frontend와 Backend

웹 애플리케이션은 크게:

* Frontend
* Backend

로 나눌 수 있다.

## Frontend

**Frontend = 사용자가 직접 보는 화면**

해당 프로젝트:

* HTML
* CSS
* JavaScript

파일 예:

```text
login.html
register.html
chat.html
```

### HTML = 구조

화면에 **무엇이 존재하는지** 정의

예:

```html
<input id="question">
<button>전송</button>
```

즉:

* 입력창
* 버튼
* 제목
* 채팅창

등의 구조를 만든다.

### CSS = 디자인

CSS가 담당하는 것:

* 색상
* 크기
* 간격
* 위치
* 폰트
* 버튼 모양

### JavaScript = 동작

사용자의 행동에 따라 실제 기능을 실행

예:

* 버튼 클릭
* Enter 입력
* API 요청
* 화면 업데이트

### 정리

```text
HTML          CSS          JavaScript
 ↓             ↓               ↓
구조          디자인           동작
```

> 이 프로젝트에서는 **React를 사용하지 않음**

---

# 4. Backend

**Backend = 사용자가 직접 보지는 않지만 서버에서 실제 로직을 처리하는 부분**

해당 프로젝트:

```text
Python + FastAPI
```

사용자가:

```text
Python이 뭐야?
```

라고 질문하면 JavaScript가 직접 AI 답변을 만드는 것이 아니다.

```text
JavaScript
    ↓
FastAPI
    ↓
OpenAI API
    ↓
GPT-5 nano
```

FastAPI가 Frontend, 인증, Database, AI API를 연결하고 요청을 처리한다.

---

# 5. HTTP

**HTTP = Hypertext Transfer Protocol**

브라우저와 서버가 **Request / Response를 주고받기 위한 통신 규칙**

```text
Browser
   │
   │ HTTP Request
   ▼
FastAPI
   │
   │ HTTP Response
   ▼
Browser
```

### 정리

```text
Request  = Client → Server
Response = Server → Client
```

---

# 6. URL / Endpoint

서버에는 여러 기능이 존재한다.

예:

* 회원가입
* 로그인
* 채팅
* 대화 기록 조회
* 대화 기록 삭제

**Endpoint = 서버의 특정 기능으로 요청을 보내기 위한 API 주소**

예:

```text
/api/auth/register
/api/auth/login
/api/chat
/api/me/chats
```

즉:

```text
Endpoint = 어느 기능에 요청할지 지정하는 주소
```

---

# 7. HTTP Method

Endpoint만으로는 부족하다.

서버에게 **어떤 행동을 원하는지**도 알려줘야 한다.

그 역할:

```text
HTTP Method
```

해당 프로젝트에서 주로 사용하는 Method:

* GET
* POST
* DELETE

서버는:

```text
HTTP Method + Endpoint
```

를 함께 확인해서 어떤 작업인지 판단한다.

---

# 8. GET

**GET = 데이터 조회 요청**

예:

```http
GET /api/me/chats
```

의미:

```text
내 채팅 기록을 가져와 줘
```

GET은 보통 기존 데이터를 **조회**할 때 사용한다.

```text
GET = 가져오기 / 조회
```

---

# 9. POST

**POST = 데이터를 서버에 보내고 처리를 요청**

예:

```http
POST /api/chat
```

Body:

```json
{
  "question": "Python이 뭐야?"
}
```

의미:

```text
이 질문을 처리해서 AI 답변을 만들어 줘
```

회원가입과 로그인도 POST 사용:

```http
POST /api/auth/register
POST /api/auth/login
```

이유:

```text
사용자 정보를 서버에 보내서 처리해야 하기 때문
```

---

# 10. DELETE

**DELETE = 데이터 삭제 요청**

예:

```http
DELETE /api/me/chats
```

의미:

```text
내 대화 기록을 삭제해 줘
```

같은 Endpoint라도 Method가 다르면 다른 기능으로 처리 가능

```text
GET /api/me/chats
→ 내 대화 조회

DELETE /api/me/chats
→ 내 대화 삭제
```

---

# 11. API

**API = Application Programming Interface**

프로그램과 프로그램이 서로 통신하기 위해 정해둔 방식

해당 프로젝트에서는 두 종류의 API 통신이 있다.

## Browser → FastAPI

```text
Browser
   ↓
내 API
   ↓
FastAPI
```

## FastAPI → OpenAI

```text
FastAPI
   ↓
OpenAI API
   ↓
OpenAI Server
```

### 전체 구조

```text
Browser
   ↓
내 API
   ↓
FastAPI
   ↓
OpenAI API
   ↓
GPT-5 nano
```

---

# 12. Request Body

POST 요청에서는 서버에 실제 데이터를 같이 보내는 경우가 많다.

예:

```json
{
  "username": "test3",
  "password": "1234"
}
```

또는:

```json
{
  "question": "안녕"
}
```

**Request Body = 서버로 보내는 실제 데이터**

### 정리

```text
POST
= 어떤 행동인지

/api/chat
= 어느 기능인지

Body
= 실제 보낼 데이터
```

---

# 13. JSON

**JSON = 데이터를 표현하고 주고받기 위한 형식**

구조:

```text
key : value
```

예:

```json
{
  "username": "test3",
  "password": "1234"
}
```

즉:

```text
username → test3
password → 1234
```

JavaScript에서는:

```javascript
JSON.stringify(...)
```

를 사용해 JavaScript 데이터를 JSON 문자열 형태로 만들어 서버에 전송할 수 있다.

---

# 14. HTTP Header

**Header = HTTP 요청에 대한 추가 정보를 담는 영역**

예:

```http
Content-Type: application/json
```

의미:

```text
보내는 데이터가 JSON 형식
```

또:

```http
Authorization: Bearer <token>
```

의미:

```text
인증 정보로 JWT Token을 함께 전송
```

### 실제 요청 구조

```http
POST /api/chat

HEADERS
Content-Type: application/json
Authorization: Bearer eyJ...

BODY
{
    "question": "안녕"
}
```

---

# 15. HTTP Status Code

**HTTP Status Code = 서버가 요청 처리 결과를 숫자로 알려주는 방식**

|    코드 | 의미            |
| ----: | ------------- |
| `200` | 요청 성공         |
| `201` | 생성 성공         |
| `400` | 잘못된 요청        |
| `401` | 인증 실패 / 인증 필요 |
| `404` | 없는 주소 또는 리소스  |
| `422` | 입력 검증 실패      |
| `429` | 너무 많은 요청      |
| `500` | 서버 내부 오류      |
| `503` | 서비스 일시 장애     |

예:

```text
HTTP 200
```

= 요청 정상 처리

실제 데이터나 AI 답변은 보통 **Response Body** 안에 들어간다.

---

# 16. 왜 회원가입이 필요한가?

회원 구분이 없으면 여러 사용자의 대화가 섞일 수 있다.

```text
사용자 A 대화
사용자 B 대화
사용자 C 대화
```

따라서 사용자별로 데이터를 분리:

```text
User 1 → User 1의 ChatLog
User 2 → User 2의 ChatLog
User 3 → User 3의 ChatLog
```

회원가입 / 로그인 기능을 통해:

```text
누가 요청했는지 확인
        ↓
해당 사용자의 데이터만 처리
```

할 수 있다.

---

# 17. 회원가입 과정

### 전체 흐름

```text
사용자
  ↓
username + password 입력
  ↓
POST /api/auth/register
  ↓
FastAPI
  ↓
입력 검증
  ↓
같은 username 존재 여부 확인
  ↓
비밀번호 Hash
  ↓
User DB 저장
```

**회원가입 = 새로운 User 데이터를 생성하는 과정**

---

# 18. Password Hashing

비밀번호를 DB에 그대로 저장하면 위험하다.

잘못된 예:

```text
username: test3
password: 1234
```

DB가 유출되면 실제 비밀번호가 그대로 노출된다.

따라서 **PBKDF2 기반 Hashing** 사용

```text
1234
 ↓
Hash
 ↓
긴 Hash 값
```

DB에는 실제 비밀번호가 아니라 **Hash 값만 저장**

### 중요

```text
암호화 ≠ Hashing
```

Hashing은 기본적으로 **단방향**

로그인 시:

```text
사용자 입력 비밀번호
        ↓
Hash 검증
        ↓
저장된 Hash와 비교
        ↓
일치 여부 판단
```

### 정리

```text
실제 비밀번호 저장 X
비밀번호의 지문 역할을 하는 Hash 값 저장
```

---

# 19. 회원가입과 로그인 차이

## 회원가입

```text
없는 사용자
   ↓
새 User 생성
   ↓
DB 저장
```

= 새로운 계정 생성

## 로그인

```text
기존 User 조회
   ↓
비밀번호 검증
   ↓
일치하면 인증 성공
```

= 기존 사용자의 신원 확인

---

# 20. Authentication과 Authorization

두 개는 서로 다른 개념

## Authentication

**Authentication = 인증**

질문:

```text
너 누구야?
```

예:

```text
너 test3 사용자 맞아?
```

## Authorization

**Authorization = 인가 / 권한 확인**

질문:

```text
너 이 작업을 할 권한이 있어?
```

예:

```text
test3가 이 대화를 삭제할 수 있어?
```

### 정리

```text
Authentication
= 사용자 신원 확인

Authorization
= 해당 사용자의 권한 확인
```

---

# 21. JWT를 왜 사용하는가?

로그인 후 매 요청마다:

```text
username
password
```

를 다시 보내지 않기 위해 사용

로그인 성공 후 서버에서:

```text
JWT Access Token
```

발급

### 전체 흐름

```text
아이디 + 비밀번호
      ↓
서버에서 확인
      ↓
로그인 성공
      ↓
JWT 발급
      ↓
브라우저 저장
```

이후 요청:

```http
Authorization: Bearer <JWT>
```

즉:

```text
처음 로그인할 때 신원 확인
        ↓
이후 요청에서는 JWT를 출입증처럼 사용
```

---

# 22. Access Token

**Access Token = 로그인 성공 후 발급되는 임시 인증 토큰**

```text
아이디 + 비밀번호
       ↓
신원 확인
       ↓
Access Token 발급
```

이후 인증이 필요한 API 요청에서는:

```http
Authorization: Bearer <token>
```

형태로 전송

---

# 23. JWT 구조

JWT는 기본적으로:

```text
HEADER.PAYLOAD.SIGNATURE
```

구조

Payload 예:

```json
{
  "sub": "test3",
  "exp": "..."
}
```

## `sub`

```text
subject
```

사용자 식별 정보로 사용 가능

## `exp`

```text
expiration
```

Token 만료 시간

## Signature

토큰이 서버에서 발급된 이후 조작되었는지 확인하는 데 사용

### 중요

```text
JWT Payload는 기본적으로 암호화되어 완전히 숨겨지는 구조가 아님
```

따라서 민감정보 자체를 넣는 용도로 사용하면 안 된다.

---

# 24. `SECRET_KEY`

JWT를 생성하고 검증할 때 서버만 알고 있어야 하는 값

```text
SECRET_KEY
```

역할:

```text
JWT Signature 생성 / 검증
```

코드에 직접 작성하지 않고 **환경변수로 관리**

---

# 25. Environment Variable

**Environment Variable = 코드와 민감정보 / 환경 설정값을 분리하는 방법**

예:

```text
OPENAI_API_KEY
SECRET_KEY
DATABASE_URL
```

Python에서는:

```python
os.getenv("OPENAI_API_KEY")
```

처럼 읽어올 수 있다.

즉:

```text
코드
≠
Secret / 환경 설정값
```

실행 환경에서 값을 설정하고 코드가 이를 읽는 구조

---

# 26. `.env`와 `.env.example`

## `.env`

로컬에서 실제 환경변수 값을 저장할 수 있는 파일

예:

```env
OPENAI_API_KEY=실제키
SECRET_KEY=실제값
```

실제 Secret이 들어가기 때문에:

```text
GitHub 업로드 X
```

`.gitignore`에 등록

## `.env.example`

프로젝트 실행에 어떤 환경변수가 필요한지만 보여주는 예시 파일

```env
OPENAI_API_KEY=your_key_here
SECRET_KEY=your_secret_here
```

### 정리

```text
.env
= 실제 값

.env.example
= 필요한 변수 이름과 형식 예시
```

---

# 27. Input Validation

**Input Validation = 사용자 입력이 정해진 조건에 맞는지 검사하는 것**

사용자 입력에는 다음 문제가 있을 수 있다.

* 빈 값
* 공백만 입력
* 너무 긴 문자열
* 잘못된 형식

해당 프로젝트에서는 **FastAPI + Pydantic**으로 검증

예:

```text
최소 1자
최대 500자
공백만 입력 불가
```

---

# 28. 왜 Frontend와 Backend 둘 다 검증하는가?

Frontend:

```html
maxlength="500"
```

같은 방식으로 제한 가능

### Frontend Validation

* 사용자 편의
* UX 개선

하지만 사용자가 브라우저를 거치지 않고 API를 직접 호출할 수도 있다.

따라서 Backend에서도:

```python
max_length=500
```

등의 검증 필요

### 정리

```text
Frontend Validation
= 사용자 편의 / UX

Backend Validation
= 서버가 실제로 강제하는 규칙
```

---

# 29. Database

**Database = 서비스에서 필요한 데이터를 지속적으로 저장하는 공간**

AI 답변을 화면에만 표시하면 새로고침 후 사라질 수 있다.

따라서 다음 정보를 DB에 저장:

* 사용자
* 질문
* AI 응답
* 생성 시각

해당 프로젝트:

```text
SQLite
```

사용

---

# 30. Database Table

**Table = 데이터를 행과 열 형태로 저장하는 구조**

엑셀 표와 비슷하게 이해 가능

## `users`

```text
id | username | hashed_password | created_at
```

## `chat_logs`

```text
id | user_id | question | response | created_at
```

---

# 31. Primary Key

**Primary Key = Table의 각 행을 유일하게 구분하는 값**

예:

```text
User id = 6
```

같은 Table 안에서 각 데이터를 고유하게 식별

---

# 32. Foreign Key

**Foreign Key = 다른 Table의 Primary Key를 참조하는 값**

예:

```text
User
id = 6
```

```text
ChatLog
id = 46
user_id = 6
```

여기서:

```text
ChatLog.user_id
        ↓
User.id
```

를 참조

따라서:

```text
ChatLog 46은 User 6의 대화
```

라는 관계를 알 수 있다.

---

# 33. 1:N 관계

한 명의 사용자는 여러 개의 ChatLog를 가질 수 있다.

```text
User 6
  │
  ├── Chat 1
  ├── Chat 2
  ├── Chat 3
  └── Chat 4
```

즉:

```text
User 1명 : ChatLog 여러 개
```

이 관계를:

```text
1 : N
```

관계라고 한다.

---

# 34. SQLAlchemy

**SQLite**

```text
실제 데이터를 저장하는 Database
```

**SQLAlchemy**

```text
Python 코드에서 Database를 쉽게 다룰 수 있게 해주는 도구
```

### 정리

```text
SQLite
= Database

SQLAlchemy
= Python과 Database를 연결하고 조작하는 도구
```

---

# 35. ORM

**ORM = Object Relational Mapping**

Database Table을 Python 객체 / Class처럼 다룰 수 있게 하는 방식

예:

```python
models.User
models.ChatLog
```

SQL을 직접 길게 작성하지 않고 Python 코드 중심으로 DB를 조작할 수 있다.

```text
Python Object
      ↕
     ORM
      ↕
Database Table
```

즉:

```text
Python과 관계형 Database 사이의 변환 역할
```

---

# 36. Database Session

DB 작업 시 SQLAlchemy Session 사용

### 흐름

```text
Request
   ↓
DB Session 생성
   ↓
조회 / 저장 / 삭제
   ↓
commit() 또는 rollback()
   ↓
Session 종료
```

**Session = DB와 작업하기 위한 하나의 작업 단위 / 연결 컨텍스트**

---

# 37. `commit()`

**`commit()` = DB 변경사항을 실제로 확정**

예:

```text
ChatLog 생성
   ↓
db.add()
   ↓
db.commit()
```

즉:

```text
현재 변경사항을 실제 Database에 저장
```

---

# 38. `rollback()`

DB 작업 중 오류가 발생했을 때:

```python
db.rollback()
```

사용

의미:

```text
현재 실패한 Transaction 상태를 되돌림
```

목적:

```text
실패한 DB 작업을 그대로 남기지 않음
DB Session을 정상 상태로 복구
```

---

# 39. AI는 어디에 들어가는가?

이 프로젝트의 기본 웹서비스 구조:

* Frontend
* 로그인
* JWT
* Database
* API

AI는 이 구조에 **외부 서비스로 추가**

```text
Browser
   ↓
FastAPI
   ↓
OpenAI API
   ↓
GPT-5 nano
```

### 중요

```text
Browser → OpenAI 직접 요청 X

Browser → FastAPI → OpenAI
```

FastAPI가 중간에서 OpenAI API를 호출한다.

---

# 40. API Key

OpenAI API를 사용하기 위해 필요한 인증 정보

```text
OPENAI_API_KEY
```

역할:

```text
OpenAI에게
"이 애플리케이션은 API 사용 권한이 있다"
는 것을 증명
```

민감정보이기 때문에:

```text
Frontend 노출 X
GitHub 업로드 X
코드 직접 작성 X
```

환경변수로 관리

---

# 41. 왜 GPT-5 nano를 사용하는가?

이 프로젝트에서는 AI 모델을 직접 학습하지 않는다.

```text
내 웹서비스
    ↓
OpenAI API
    ↓
GPT-5 nano
    ↓
AI Response
```

따라서 프로젝트 성격:

```text
AI 모델 직접 개발 X
AI API 연동 O
```

---

# 42. Context

**Context = 현재 질문과 함께 AI에게 제공하는 이전 대화 정보**

예:

```text
사용자:
내가 좋아하는 과일은 사과야.

사용자:
내가 좋아하는 과일이 뭐였지?
```

두 번째 질문만 AI에게 보내면 이전 정보를 모를 수 있다.

따라서:

```text
최근 대화
   +
현재 질문
   ↓
OpenAI
```

형태로 전달

---

# 43. 왜 최근 3개만 사용하는가?

모든 대화를 계속 Context로 보내면:

* 전송 데이터 증가
* Token 사용량 증가
* 비용 증가 가능
* 응답 시간 증가 가능
* 불필요한 과거 내용 포함

문제가 발생할 수 있다.

따라서 최근 N개만 사용

해당 프로젝트:

```text
최근 3개 ChatLog
```

사용

### 중요

```text
3개 = 절대적인 정답 X
3개 = 프로젝트에서 선택한 설계 기준
```

---

# 44. Async / Await

OpenAI API는 외부 서버와 통신하기 때문에 응답을 기다리는 시간이 발생한다.

이와 같은 I/O 작업을 처리하기 위해:

```python
async
await
```

사용

목적:

```text
외부 요청을 기다리는 동안 서버가 더 효율적으로 동작할 수 있도록 처리
```

### 중요

```text
async 사용
≠
OpenAI 응답 자체가 더 빨라짐
```

---

# 45. Timeout

외부 API가 응답하지 않을 때 무한정 기다리면 안 된다.

따라서:

```text
Timeout
```

설정

해당 프로젝트 기준:

```text
20초
```

흐름:

```text
20초 안에 응답?
   │
   ├── Yes → 정상 진행
   │
   └── No → Timeout 처리
```

---

# 46. Retry

**Retry = 일시적인 오류가 발생했을 때 다시 요청하는 것**

예:

```text
1차 요청
   ↓
실패
   ↓
2차 요청
   ↓
실패
   ↓
3차 요청
   ↓
성공 또는 최종 실패
```

해당 프로젝트에서는 최대 3회까지 시도

---

# 47. Exponential Backoff

실패 후 바로 연속 요청하지 않고 **재시도 전 대기 시간을 점점 늘리는 방식**

예:

```text
1차 실패
   ↓
2초 대기
   ↓
2차 실패
   ↓
4초 대기
   ↓
3차 시도
```

목적:

```text
외부 서버가 일시적으로 혼잡한 상황에서
연속 요청으로 부담을 더 주지 않고
시간 간격을 두고 재시도
```

---

# 48. Exception Handling

**Exception Handling = 오류가 발생했을 때 프로그램이 비정상 종료되지 않도록 처리하는 것**

발생 가능한 오류:

* 네트워크 오류
* OpenAI API 오류
* DB 오류
* 잘못된 입력
* JWT 만료
* Timeout

Python 예:

```python
try:
    ...
except:
    ...
```

목적:

```text
오류를 숨기는 것 X
오류 상황을 예측하고 적절하게 처리하는 것 O
```

---

# 49. Logging

**Logging = 서버 내부에서 발생한 작업과 상태를 기록하는 것**

사용자가:

```text
"챗봇이 안 돼요."
```

라고 했을 때 원인은 여러 가지일 수 있다.

```text
JWT?
FastAPI?
OpenAI?
Database?
Timeout?
```

따라서 주요 단계에 로그 작성

예:

```text
request_received
ai_call_start
ai_call_success
ai_call_failed
db_save_success
db_save_failed
```

로그를 통해 문제가 어느 단계에서 발생했는지 확인 가능

---

# 50. `request_id`

여러 요청이 동시에 들어오면 로그가 서로 섞일 수 있다.

따라서 요청마다 고유한:

```text
request_id
```

생성

예:

```text
request_received   ABC123
ai_call_start      ABC123
ai_call_success    ABC123
db_save_success    ABC123
```

같은 `request_id`를 따라가면:

```text
하나의 Request가 처음부터 끝까지 어떻게 처리됐는지 추적 가능
```

---

# 51. UUID

**UUID = 충돌 가능성이 매우 낮은 고유 ID를 생성하기 위한 방식**

예:

```text
0b57faed-7fd2-4902-bd28-8875d5dabd6a
```

해당 프로젝트에서는 `request_id` 생성에 사용

### 정리

```text
UUID 기반 request_id
→ 각 요청을 고유하게 식별
→ 로그 추적 가능
```

---

# 52. 왜 사용자 질문 내용을 로그에 남기지 않았는가?

사용자 질문에는 민감정보가 포함될 수 있다.

예:

* 개인정보
* 비밀번호
* 계좌 관련 정보
* 사적인 내용

따라서 질문 원문 대신:

```text
question_length=10
```

처럼 길이 등의 최소 정보만 기록

목적:

```text
문제 추적에 필요한 로그는 남기되
사용자 입력 내용은 불필요하게 저장하지 않음
```

---

# 53. DOM

**DOM = Document Object Model**

브라우저는 HTML을 단순 문자열로만 처리하지 않고 구조화된 객체 형태로 메모리에 표현한다.

JavaScript는 DOM을 통해 HTML 요소에 접근하고 수정한다.

예:

```javascript
document.getElementById('chat-box')
```

의미:

```text
id가 chat-box인 HTML 요소를 찾아라
```

---

# 54. `textContent`와 `innerHTML`

사용자가 다음과 같은 값을 입력했다고 가정:

```html
<img src=x onerror="alert('hacked')">
```

## `innerHTML`

입력값을 HTML 코드로 해석할 가능성이 있음

```text
innerHTML
→ HTML로 해석 가능
```

## `textContent`

입력값을 문자 그대로 출력

```text
textContent
→ 문자열 그대로 출력
```

따라서 해당 프로젝트에서는 채팅 메시지를 출력할 때:

```javascript
textContent
```

사용

---

# 55. XSS

**XSS = Cross-Site Scripting**

웹페이지에 악성 JavaScript 등을 삽입해 실행시키는 공격

예:

```html
<img src=x onerror="alert('hacked')">
```

해당 프로젝트에서는 사용자 입력 / AI 응답을:

```javascript
textContent
```

로 출력

따라서 입력값을 HTML이나 JavaScript 코드로 실행하지 않고 문자 그대로 표시

---

# 56. Timestamp

각 ChatLog에는:

```text
created_at
```

저장

역할:

```text
해당 대화가 언제 생성됐는지 기록
```

화면 예:

```text
2026년 8월 15일

test3: 안녕        15:01
챗봇: 안녕하세요!  15:01
```

---

# 57. UTC와 KST

서버 / DB에서는 UTC 기준 시간 사용

Frontend에서는:

```text
Asia/Seoul
```

기준으로 변환해 KST 표시

관계:

```text
KST = UTC + 9시간
```

예:

```text
UTC 06:01
   ↓
KST 15:01
```

따라서 저장 시간과 사용자 화면 표시 시간을 구분

---

# 58. 왜 대화 삭제에도 JWT가 필요한가?

삭제 API:

```http
DELETE /api/me/chats
```

하지만 서버는 먼저:

```text
누구의 대화를 삭제할 것인가?
```

를 알아야 한다.

따라서 JWT 확인:

```text
JWT
 ↓
current_user
 ↓
current_user.id
 ↓
해당 User의 ChatLog만 삭제
```

즉:

```text
JWT를 통해 현재 사용자를 식별
→ 그 사용자의 대화만 삭제
```

---

# 59. 삭제 확인 팝업

삭제 버튼을 누르자마자 바로 삭제되면 실수 가능

따라서:

```text
삭제 버튼 클릭
     ↓
"정말 삭제할까요?"
     ↓
취소 / 확인
```

단계를 추가

이 기능은:

```text
보안 기능보다는 UX 측면의 안전장치
```

---

# 60. Railway

로컬 실행:

```text
localhost:8000
```

은 기본적으로 자신의 컴퓨터에서 앱을 실행하는 환경

다른 사용자도 인터넷에서 접속하려면 애플리케이션을 외부 서버 환경에 배포해야 한다.

해당 프로젝트:

```text
Railway
```

사용

### 정리

```text
내 Mac
   ↓
Local 실행

Railway
   ↓
인터넷에 공개된 서버 환경에서 실행
```

---

# 61. Deployment

**Deployment = 개발한 애플리케이션을 실제 사용 가능한 서버 환경에 올려 실행하는 것**

GitHub와 역할이 다름

```text
GitHub
= 코드 저장 / 버전 관리

Railway
= 실제 애플리케이션 실행
```

---

# 62. Persistent Volume

Railway에서 애플리케이션 환경이 다시 생성되면 내부 파일이 사라질 수 있다.

SQLite는 파일 기반 DB이기 때문에 DB 파일을 일반 컨테이너 내부에만 두면 문제가 될 수 있다.

따라서:

```text
Persistent Volume
```

사용

### 구조

```text
Application Container
        │
        └── Persistent Volume
                 ↓
             chatbot.db
```

목적:

```text
애플리케이션이 재배포 / 재시작되어도
Database 파일을 지속적으로 유지
```

---

# 63. Git

**Git = 버전 관리 도구**

코드 변경 이력을 기록

```text
Version 1
   ↓
Version 2
   ↓
Version 3
```

각 변경 단위를:

```text
Commit
```

으로 저장

---

# 64. GitHub

**GitHub = Git Repository를 인터넷에서 저장하고 관리할 수 있는 플랫폼**

### 정리

```text
Git
= 버전 관리 기술 / 도구

GitHub
= Git Repository를 온라인에서 호스팅하는 플랫폼
```

---

# 65. `git add`, `commit`, `push`

### 기본 흐름

```text
파일 수정
   ↓
git add
   ↓
Staging Area
   ↓
git commit
   ↓
Local Git 기록
   ↓
git push
   ↓
GitHub 업로드
```

## `git add`

다음 Commit에 포함할 변경사항 선택

## `git commit`

선택한 변경사항을 Local Git 기록으로 저장

## `git push`

Local Commit을 Remote Repository인 GitHub로 전송

---

# 66. `requirements.txt`

프로젝트에서 사용하는 Python 외부 라이브러리 목록

예:

```text
fastapi
uvicorn
sqlalchemy
pydantic
openai
```

새로운 환경에서:

```bash
pip install -r requirements.txt
```

실행

목적:

```text
프로젝트에 필요한 Package를 동일하게 설치
→ 실행 환경 재현성 향상
```

---

# 67. `.venv`

**`.venv` = Python Virtual Environment**

프로젝트마다 서로 다른 Library / Version을 사용할 수 있기 때문에 사용

예:

```text
Project A
└── .venv

Project B
└── .venv
```

각 프로젝트의 Python 환경을 분리

---

# 68. Uvicorn

**FastAPI = 웹 애플리케이션 Framework**

**Uvicorn = FastAPI Application을 실제로 실행하고 HTTP Request를 받아주는 ASGI Server**

예:

```bash
uvicorn main:app --reload
```

의미:

```text
main.py 안의

app = FastAPI(...)

객체를 Uvicorn으로 실행
```

### 정리

```text
FastAPI
= 웹 애플리케이션 작성

Uvicorn
= 해당 애플리케이션 실행 및 HTTP 요청 수신
```

---

# 69. Jinja2

**Jinja2 = HTML Template Engine**

FastAPI가 HTML 파일을 사용자에게 전달할 때 사용

해당 프로젝트:

```text
login.html
register.html
chat.html
```

FastAPI에서:

```python
Jinja2Templates
```

를 사용해 HTML Template을 반환

---

# 70. localStorage

**localStorage = 브라우저 내부의 간단한 저장 공간**

해당 프로젝트에서는 예를 들어:

```text
token
username
```

저장

### 구조

```text
Browser
└── localStorage
      ├── token
      └── username
```

API 요청 시 token을 꺼내:

```text
Authorization Header
```

에 추가

### 중요

```text
localStorage = 가장 안전한 인증 저장 방식
```

이라고 말하면 안 됨

해당 프로젝트 / PoC에서는 구현이 간단하기 때문에 사용

실제 서비스에서는:

```text
HttpOnly Cookie
```

같은 방식도 고려 가능

---

# 71. 로그인 전체 흐름

```text
사용자
아이디 + 비밀번호 입력
        ↓
JavaScript
        ↓
POST /api/auth/login
        ↓
FastAPI
        ↓
DB에서 User 조회
        ↓
PBKDF2 Hash 검증
        ↓
비밀번호 일치?
   ┌────┴────┐
   │         │
  No        Yes
   │         │
   ↓         ↓
 401      JWT 생성
             ↓
      Access Token 반환
             ↓
      localStorage 저장
```

### 핵심

```text
사용자 입력
→ API 요청
→ DB 사용자 확인
→ 비밀번호 Hash 검증
→ JWT 발급
→ Browser 저장
```

---

# 72. 메시지 전송 전체 흐름

> **프로젝트에서 가장 중요한 흐름**

```text
사용자 질문 입력
        ↓
JavaScript
        ↓
POST /api/chat
        │
        ├── Body
        │    question
        │
        └── Header
             Authorization: Bearer JWT
        ↓
FastAPI
        ↓
Pydantic 입력 검증
        ↓
JWT 검증
        ↓
current_user 확인
        ↓
SQLite에서
최근 3개 ChatLog 조회
        ↓
ai_service.py
        ↓
Context 구성
        ↓
OpenAI API
        ↓
GPT-5 nano
        ↓
AI Response
        ↓
FastAPI
        ↓
ChatLog 생성
        ↓
SQLite commit
        ↓
JSON Response
        ↓
JavaScript
        ↓
DOM에 출력
        ↓
사용자가 답변 확인
```

### 한 문장으로 정리

Frontend가 질문과 JWT를 FastAPI에 보내고, FastAPI가 입력과 사용자를 검증한 뒤 최근 대화를 Context로 OpenAI에 요청하고, 받은 AI 응답을 DB에 저장한 후 JSON으로 Frontend에 반환해서 화면에 출력한다.

---

# 73. 대화 이력 조회 흐름

```text
사용자가 /chat 페이지 접속
        ↓
JavaScript
        ↓
GET /api/me/chats
+
Authorization: Bearer JWT
        ↓
FastAPI
        ↓
JWT 검증
        ↓
현재 사용자 확인
        ↓
SQLite
        ↓
해당 사용자의 ChatLog 조회
        ↓
JSON Response
        ↓
JavaScript
        ↓
DOM에 메시지 표시
        ↓
UTC → KST
        ↓
날짜 구분선 + HH:MM 표시
```

---

# 74. 대화 삭제 흐름

```text
사용자
"대화 기록 삭제" 클릭
        ↓
확인 팝업
        ↓
사용자 확인
        ↓
DELETE /api/me/chats
+
JWT
        ↓
FastAPI
        ↓
JWT 검증
        ↓
current_user 확인
        ↓
해당 사용자 ChatLog 삭제

WHERE user_id = current_user.id

        ↓
commit()
        ↓
Success Response
        ↓
Frontend 화면에서 메시지 제거
```

---

# 75. Enter를 누르면 왜 동작하는가?

로그인 / 회원가입에서는 `<form>` 사용

사용자가 Enter를 누르면:

```text
Enter
 ↓
form submit 이벤트 발생
 ↓
JavaScript Event Listener 실행
 ↓
event.preventDefault()
 ↓
기본 페이지 새로고침 방지
 ↓
login() 또는 register()
 ↓
fetch()
 ↓
HTTP Request
```

즉:

```text
Enter 입력
= submit Event 발생
```

---

# 76. Event Listener

JavaScript는 많은 기능이 **Event 기반**으로 동작

Event 예:

* `click`
* `keydown`
* `submit`
* `load`
* `input`

예:

```javascript
form.addEventListener('submit', ...)
```

의미:

```text
해당 form에서 submit Event가 발생하면
지정한 함수를 실행
```

---

# 77. `fetch()`

**`fetch()` = JavaScript에서 서버로 HTTP Request를 보내기 위한 함수**

예:

```javascript
fetch('/api/chat', ...)
```

의미:

```text
브라우저에서 /api/chat Endpoint로 HTTP Request 전송
```

Frontend와 Backend를 연결하는 주요 방법 중 하나

---

# 78. Response JSON

FastAPI에서:

```python
return {
    "response": ai_response
}
```

처럼 반환하면 브라우저는 JSON Response를 받는다.

JavaScript:

```javascript
const data = await res.json();
```

그 이후:

```javascript
data.response
```

형태로 값 사용 가능

### 흐름

```text
Python dict
    ↓
JSON HTTP Response
    ↓
JavaScript Object
```

---

# 79. `[object Object]` 오류가 왜 생겼는가?

FastAPI / Pydantic의 오류 응답은 단순 문자열이 아니라 객체 구조일 수 있다.

예:

```text
Array
 └── Object
      ├── type
      ├── loc
      └── msg
```

JavaScript에서 Object 자체를 문자열처럼 출력하면:

```text
[object Object]
```

표시 가능

따라서 오류 구조 안의 실제 메시지:

```javascript
error.msg
```

등을 추출해서 화면에 표시하도록 처리

---

# 80. PoC

**PoC = Proof of Concept**

의미:

```text
사용하려는 기술 조합이 실제로 동작 가능한지 검증하는 프로토타입
```

해당 프로젝트에서 검증하는 것:

* Frontend ↔ Backend 연결 가능?
* JWT 인증 가능?
* Database 저장 가능?
* AI API 연동 가능?
* Context 유지 가능?
* Deployment 가능?

### 중요

```text
PoC
≠
완성된 대규모 상용 서비스
```

---

# 81. Architecture

**Architecture = 시스템의 주요 구성 요소와 각 요소가 어떻게 연결되는지를 나타내는 구조**

해당 프로젝트:

```text
Presentation Layer
HTML / CSS / JavaScript
        ↓
Application Layer
FastAPI
        ↓
Authentication
JWT / PBKDF2
        ↓
Data Layer
SQLAlchemy / SQLite
        ↓
External AI
OpenAI API / GPT-5 nano
        ↓
Deployment
Railway + Persistent Volume
```

질문:

```text
"프로젝트 Architecture가 어떻게 되나요?"
```

라고 하면 화면 디자인을 설명하는 것이 아니라:

* Frontend
* Backend
* Authentication
* Database
* External API
* Deployment

가 어떻게 연결되는지 설명해야 한다.

---

# 82. 프로젝트 전체를 현실 세계로 비유하면

프로젝트를 **AI 상담소**라고 가정

| 기술 / 개념             | 비유                                  |
| ------------------- | ----------------------------------- |
| HTML / CSS          | 상담소 건물과 인테리어                        |
| JavaScript          | 버튼 / 접수 / 화면 동작                     |
| HTTP                | 정보를 주고받는 통신 규칙                      |
| Endpoint            | 각 업무를 담당하는 창구 주소                    |
| GET                 | 정보 조회 요청                            |
| POST                | 데이터를 보내고 처리 요청                      |
| DELETE              | 데이터 삭제 요청                           |
| FastAPI             | 전체 요청을 처리하는 중앙 직원                   |
| Pydantic            | 접수된 데이터가 규칙에 맞는지 검사                 |
| PBKDF2              | 실제 비밀번호 대신 Hash 값을 저장하는 방식          |
| JWT                 | 로그인 후 받은 임시 출입증                     |
| SQLite              | 데이터 저장 창고                           |
| SQLAlchemy          | Python으로 Database를 쉽게 관리하게 해주는 도구   |
| OpenAI API          | 외부 AI에게 요청을 보내는 통신 수단               |
| GPT-5 nano          | 실제 답변을 생성하는 외부 AI 모델                |
| Context             | 이전 상담 기록                            |
| Timeout             | 너무 오래 기다리지 않기 위한 시간 제한              |
| Retry               | 일시적 오류 발생 시 다시 요청                   |
| Exponential Backoff | 실패할수록 재시도 전 대기 시간을 늘리는 방식           |
| Logging             | 서버 내부 작업 기록                         |
| `request_id`        | 각 Request의 고유 추적 번호                 |
| Railway             | 애플리케이션을 실제 인터넷에서 실행하는 환경            |
| Persistent Volume   | 애플리케이션이 재배포되어도 유지되는 저장 공간           |
| Git                 | 코드 변경 이력 관리                         |
| GitHub              | Git Repository를 인터넷에서 저장 / 관리하는 플랫폼 |

---

# 가장 중요한 최종 흐름

> 피어리뷰 전에 최소한 아래 흐름은 **코드 없이 설명 가능해야 한다.**

```text
사용자 질문 입력
        ↓
JavaScript Event 발생
        ↓
fetch()
        ↓
POST /api/chat
        ↓
Question을 Request Body에 담음
        +
JWT를 Authorization Header에 담음
        ↓
FastAPI Request 수신
        ↓
Pydantic Input Validation
        ↓
JWT 검증
        ↓
current_user 확인
        ↓
Database에서 최근 ChatLog 조회
        ↓
최근 대화 + 현재 질문으로 Context 구성
        ↓
OpenAI API 호출
        ↓
GPT-5 nano가 답변 생성
        ↓
FastAPI가 AI Response 수신
        ↓
질문 + 답변을 ChatLog로 저장
        ↓
db.commit()
        ↓
JSON Response 반환
        ↓
JavaScript가 Response 수신
        ↓
DOM 업데이트
        ↓
textContent로 메시지 출력
        ↓
사용자가 AI 답변 확인
```

## 한 문장 버전

**사용자가 질문을 입력하면 JavaScript가 질문과 JWT를 FastAPI에 보내고, FastAPI가 입력과 사용자를 검증한 뒤 Database에서 최근 대화를 조회하여 Context와 함께 OpenAI API에 전달한다. GPT-5 nano가 생성한 답변을 FastAPI가 받아 Database에 저장하고 JSON으로 Frontend에 반환하면 JavaScript가 DOM을 업데이트하여 화면에 답변을 표시한다.**

이 흐름을 이해하면 프로젝트의:

* Frontend
* Backend
* HTTP
* API
* Authentication
* Database
* AI API
* Security
* Logging
* Deployment

가 하나의 서비스 안에서 어떻게 연결되는지 전체적으로 설명할 수 있다.
