# AI 파이프라인, Context, Timeout 구현
# ai_service.py: AI API 호출 시 타임아웃 핸들링, 문맥 유지(최근 N개 대화), 에러 처리를 담당하는 핵심 로직

# Google GenAI 공식 SDK 기반 연동, 문맥 유지, 하드 타임아웃, 재시도 및 예외 처리

import os
import asyncio
import logging

from dotenv import load_dotenv
from google import genai
from google.genai import types
from google.genai import errors


# -------------------------------------------------------------------
# 로깅 설정
# -------------------------------------------------------------------
logger = logging.getLogger("uvicorn.error")


# -------------------------------------------------------------------
# AI 호출 설정
# -------------------------------------------------------------------

# 최대 API 호출 시도 횟수
MAX_RETRIES = 3

# 재시도 기본 대기 시간
RETRY_DELAY_SECONDS = 2

# AI API 1회 호출 최대 대기 시간
TIMEOUT_SECONDS = 20.0


# -------------------------------------------------------------------
# Google Gemini AI 호출 함수
# -------------------------------------------------------------------
async def get_ai_response(
    prompt: str,
    history_logs: list,
    request_id: str
) -> str:
    """
    최근 N개의 대화 기록을 Context로 구성하여
    Google Gemini API를 호출합니다.

    주요 기능:
    - 최근 대화 Context 유지
    - 5초 하드 타임아웃
    - 최대 3회 API 호출 시도
    - Exponential Backoff 적용
    - Gemini API 오류 처리
    - request_id 기반 요청 흐름 추적
    """

    # ---------------------------------------------------------------
    # 환경 변수 로드
    # ---------------------------------------------------------------
    load_dotenv(override=True)

    api_key = os.getenv("GEMINI_API_KEY", "").strip()

    # Gemini API Key가 없거나 예시 값 그대로인 경우
    if not api_key or api_key == "your_gemini_api_key_here":
        logger.error(
            f"ai_call_failed "
            f"request_id={request_id} "
            f"reason=missing_or_invalid_gemini_api_key"
        )

        return (
            "AI 서비스 설정에 문제가 발생했습니다. "
            "(.env GEMINI_API_KEY 확인 필요)"
        )

    # Gemini Client 생성
    client = genai.Client(api_key=api_key)


    # ---------------------------------------------------------------
    # 최근 대화 기록을 기반으로 Context 구성
    # ---------------------------------------------------------------
    contents = []

    # main.py에서는 최신 대화부터 조회하기 때문에
    # reversed()를 사용하여 과거 → 최신 순서로 AI에게 전달
    for log in reversed(history_logs):

        # 이전 사용자 질문
        contents.append(
            types.Content(
                role="user",
                parts=[
                    types.Part.from_text(
                        text=log.question
                    )
                ]
            )
        )

        # 이전 AI 응답
        contents.append(
            types.Content(
                role="model",
                parts=[
                    types.Part.from_text(
                        text=log.response
                    )
                ]
            )
        )

    # 현재 사용자의 새로운 질문 추가
    contents.append(
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(
                    text=prompt
                )
            ]
        )
    )


    # ---------------------------------------------------------------
    # AI 호출 시작 로그
    # ---------------------------------------------------------------
    logger.info(
        f"ai_call_start "
        f"request_id={request_id} "
        f"prompt_length={len(prompt)} "
        f"context_count={len(history_logs)}"
    )


    # ---------------------------------------------------------------
    # Gemini API 호출 + Retry
    # ---------------------------------------------------------------
    for attempt in range(1, MAX_RETRIES + 1):

        try:
            # -------------------------------------------------------
            # asyncio.wait_for를 사용하여
            # AI API 호출에 명시적인 하드 타임아웃 적용
            # -------------------------------------------------------
            response = await asyncio.wait_for(
                client.aio.models.generate_content(
                    model="gemini-3.6-flash",
                    contents=contents,
                    config=types.GenerateContentConfig(
                        system_instruction=(
                            "너는 친절하고 유용한 AI 보조원이야."
                        )
                    )
                ),
                timeout=TIMEOUT_SECONDS
            )

            # Gemini 응답 텍스트 추출
            ai_text = response.text

            # 정상 응답 로그
            logger.info(
                f"ai_call_success "
                f"request_id={request_id} "
                f"attempt={attempt}"
            )

            return ai_text


        # -----------------------------------------------------------
        # Timeout 처리
        # -----------------------------------------------------------
        except asyncio.TimeoutError:

            logger.error(
                f"ai_call_failed "
                f"request_id={request_id} "
                f"attempt={attempt} "
                f"reason=timeout"
            )

            # 아직 재시도 횟수가 남아 있다면 재시도
            if attempt < MAX_RETRIES:

                # Exponential Backoff
                #
                # attempt 1 실패 → 2초 대기
                # attempt 2 실패 → 4초 대기
                #
                # MAX_RETRIES가 증가하면 이후에는
                # 8초 → 16초 ... 형태로 증가
                wait_time = (
                    RETRY_DELAY_SECONDS
                    * (2 ** (attempt - 1))
                )

                logger.info(
                    f"ai_call_retry "
                    f"request_id={request_id} "
                    f"attempt={attempt} "
                    f"wait={wait_time}s"
                )

                await asyncio.sleep(wait_time)

                continue

            # 마지막 시도까지 Timeout이면 사용자에게 안내
            return (
                "현재 응답이 지연되고 있어요. "
                "잠시 후 다시 시도해 주세요. "
                "(error: AI_TIMEOUT)"
            )


        # -----------------------------------------------------------
        # Google Gemini API 자체 오류 처리
        # -----------------------------------------------------------
        except errors.APIError as e:

            # Gemini SDK에서 제공하는 상태 코드 확인
            status_code = (
                getattr(e, "status", None)
                or getattr(e, "code", None)
            )

            # 일시적 오류라 재시도할 가치가 있는 상태
            is_retryable = status_code in (
                503,
                429,
                "UNAVAILABLE",
                "RESOURCE_EXHAUSTED"
            )

            logger.error(
                f"ai_call_failed "
                f"request_id={request_id} "
                f"attempt={attempt} "
                f"status={status_code} "
                f"reason={str(e)}"
            )

            # 429 / 503 오류이며 재시도 횟수가 남아 있는 경우
            if is_retryable and attempt < MAX_RETRIES:

                # Exponential Backoff
                wait_time = (
                    RETRY_DELAY_SECONDS
                    * (2 ** (attempt - 1))
                )

                logger.info(
                    f"ai_call_retry "
                    f"request_id={request_id} "
                    f"attempt={attempt} "
                    f"wait={wait_time}s"
                )

                await asyncio.sleep(wait_time)

                continue

            # 재시도 불가능하거나 모든 재시도가 실패한 경우
            return (
                "AI 서비스가 현재 혼잡합니다. "
                "잠시 후 다시 시도해 주세요."
            )


        # -----------------------------------------------------------
        # 예상하지 못한 기타 오류 처리
        # -----------------------------------------------------------
        except Exception as e:

            logger.exception(
                f"ai_call_failed "
                f"request_id={request_id} "
                f"attempt={attempt} "
                f"reason={type(e).__name__}"
            )

            return (
                "AI 서비스 응답 오류가 발생했습니다. "
                f"(error: {type(e).__name__})"
            )