# AI 파이프라인, Context, Timeout 구현
# ai_service.py:
# AI API 호출 시 타임아웃 핸들링,
# 문맥 유지(최근 N개 대화),
# 재시도 및 예외 처리를 담당하는 핵심 로직

# OpenAI 공식 Python SDK 기반 연동,
# 문맥 유지, 하드 타임아웃, 재시도 및 예외 처리

import os
import asyncio
import logging

from dotenv import load_dotenv

from openai import (
    AsyncOpenAI,
    APITimeoutError,
    RateLimitError,
    APIStatusError,
    APIConnectionError
)


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
# OpenAI 호출 함수
# -------------------------------------------------------------------
async def get_ai_response(
    prompt: str,
    history_logs: list,
    request_id: str
) -> str:
    """
    최근 N개의 대화 기록을 Context로 구성하여
    OpenAI API를 호출합니다.

    주요 기능:
    - 최근 대화 Context 유지
    - 20초 하드 타임아웃
    - 최대 3회 API 호출 시도
    - Exponential Backoff 적용
    - OpenAI API 오류 처리
    - request_id 기반 요청 흐름 추적
    """

    # ---------------------------------------------------------------
    # 환경 변수 로드
    # ---------------------------------------------------------------
    load_dotenv(override=True)

    api_key = os.getenv(
        "OPENAI_API_KEY",
        ""
    ).strip()


    # ---------------------------------------------------------------
    # OpenAI API Key 확인
    # ---------------------------------------------------------------
    if (
        not api_key
        or api_key == "your_openai_api_key_here"
    ):
        logger.error(
            f"ai_call_failed "
            f"request_id={request_id} "
            f"reason=missing_or_invalid_openai_api_key"
        )

        return (
            "AI 서비스 설정에 문제가 발생했습니다. "
            "(.env OPENAI_API_KEY 확인 필요)"
        )


    # ---------------------------------------------------------------
    # OpenAI Client 생성
    #
    # OpenAI SDK 자체 Retry는 비활성화하고
    # 아래 프로젝트의 Retry 로직만 사용
    # ---------------------------------------------------------------
    client = AsyncOpenAI(
        api_key=api_key,
        max_retries=0
    )


    # ---------------------------------------------------------------
    # 최근 대화 기록을 기반으로 Context 구성
    # ---------------------------------------------------------------
    messages = []


    # System Message
    messages.append(
        {
            "role": "system",
            "content": (
                "너는 친절하고 유용한 AI 보조원이야."
            )
        }
    )


    # main.py에서는 최신 대화부터 조회하기 때문에
    # reversed()를 사용하여 과거 → 최신 순서로 전달
    for log in reversed(history_logs):

        # 이전 사용자 질문
        messages.append(
            {
                "role": "user",
                "content": log.question
            }
        )

        # 이전 AI 응답
        messages.append(
            {
                "role": "assistant",
                "content": log.response
            }
        )


    # 현재 사용자의 새로운 질문 추가
    messages.append(
        {
            "role": "user",
            "content": prompt
        }
    )


    # ---------------------------------------------------------------
    # AI 호출 시작 로그
    # ---------------------------------------------------------------
    logger.info(
        f"ai_call_start "
        f"request_id={request_id} "
        f"prompt_length={len(prompt)} "
        f"context_count={len(history_logs)} "
        f"model=gpt-5-nano"
    )


    # ---------------------------------------------------------------
    # OpenAI API 호출 + Retry
    # ---------------------------------------------------------------
    for attempt in range(
        1,
        MAX_RETRIES + 1
    ):

        try:

            # -------------------------------------------------------
            # asyncio.wait_for를 사용하여
            # AI API 호출에 명시적인 하드 타임아웃 적용
            # -------------------------------------------------------
            response = await asyncio.wait_for(
                client.chat.completions.create(
                    model="gpt-5-nano",
                    messages=messages
                ),
                timeout=TIMEOUT_SECONDS
            )


            # -------------------------------------------------------
            # OpenAI 응답 텍스트 추출
            # -------------------------------------------------------
            ai_text = (
                response
                .choices[0]
                .message
                .content
            )


            # 응답이 비어 있는 예외 상황 방어
            if not ai_text:
                raise ValueError(
                    "empty_openai_response"
                )


            # -------------------------------------------------------
            # 정상 응답 로그
            # -------------------------------------------------------
            logger.info(
                f"ai_call_success "
                f"request_id={request_id} "
                f"attempt={attempt} "
                f"model=gpt-5-nano"
            )


            return ai_text


        # -----------------------------------------------------------
        # asyncio.wait_for Timeout 처리
        # -----------------------------------------------------------
        except asyncio.TimeoutError:

            logger.error(
                f"ai_call_failed "
                f"request_id={request_id} "
                f"attempt={attempt} "
                f"reason=timeout"
            )


            if attempt < MAX_RETRIES:

                # Exponential Backoff
                #
                # attempt 1 실패 → 2초 대기
                # attempt 2 실패 → 4초 대기
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


                await asyncio.sleep(
                    wait_time
                )

                continue


            return (
                "현재 응답이 지연되고 있어요. "
                "잠시 후 다시 시도해 주세요. "
                "(error: AI_TIMEOUT)"
            )


        # -----------------------------------------------------------
        # OpenAI SDK Timeout 처리
        # -----------------------------------------------------------
        except APITimeoutError:

            logger.error(
                f"ai_call_failed "
                f"request_id={request_id} "
                f"attempt={attempt} "
                f"reason=openai_timeout"
            )


            if attempt < MAX_RETRIES:

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


                await asyncio.sleep(
                    wait_time
                )

                continue


            return (
                "현재 응답이 지연되고 있어요. "
                "잠시 후 다시 시도해 주세요. "
                "(error: AI_TIMEOUT)"
            )


        # -----------------------------------------------------------
        # OpenAI Rate Limit 처리
        # -----------------------------------------------------------
        except RateLimitError as e:

            logger.error(
                f"ai_call_failed "
                f"request_id={request_id} "
                f"attempt={attempt} "
                f"status=429 "
                f"reason={str(e)}"
            )


            if attempt < MAX_RETRIES:

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


                await asyncio.sleep(
                    wait_time
                )

                continue


            return (
                "AI 서비스 요청 한도에 도달했습니다. "
                "잠시 후 다시 시도해 주세요."
            )


        # -----------------------------------------------------------
        # 네트워크 연결 오류
        # -----------------------------------------------------------
        except APIConnectionError as e:

            logger.error(
                f"ai_call_failed "
                f"request_id={request_id} "
                f"attempt={attempt} "
                f"reason=connection_error "
                f"detail={str(e)}"
            )


            if attempt < MAX_RETRIES:

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


                await asyncio.sleep(
                    wait_time
                )

                continue


            return (
                "AI 서비스에 연결할 수 없습니다. "
                "잠시 후 다시 시도해 주세요."
            )


        # -----------------------------------------------------------
        # OpenAI HTTP 상태 코드 오류
        # -----------------------------------------------------------
        except APIStatusError as e:

            status_code = e.status_code


            logger.error(
                f"ai_call_failed "
                f"request_id={request_id} "
                f"attempt={attempt} "
                f"status={status_code} "
                f"reason={str(e)}"
            )


            # 서버 측 일시적 장애는 재시도
            is_retryable = (
                status_code >= 500
            )


            if (
                is_retryable
                and attempt < MAX_RETRIES
            ):

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


                await asyncio.sleep(
                    wait_time
                )

                continue


            return (
                "AI 서비스 요청 처리 중 오류가 발생했습니다. "
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