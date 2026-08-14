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

logger = logging.getLogger("uvicorn.error")

MAX_RETRIES = 3
RETRY_DELAY_SECONDS = 2
TIMEOUT_SECONDS = 5.0  # 명시적 하드 타임아웃 설정 (초)

async def get_ai_response(prompt: str, history_logs: list) -> str:
    """
    최근 N개의 대화 기록을 포함하여 Google Gemini API를 호출합니다.
    5초 하드 타임아웃 및 재시도(Retry) 로직이 적용되어 있습니다.
    """
    load_dotenv(override=True)
    api_key = os.getenv("GEMINI_API_KEY", "").strip()

    if not api_key or api_key == "your_gemini_api_key_here":
        logger.error("ai_call_failed reason=missing_or_invalid_gemini_api_key")
        return "AI 서비스 설정에 문제가 발생했습니다. (.env GEMINI_API_KEY 확인 필요)"

    client = genai.Client(api_key=api_key)

    # 이전 대화 기록으로 Context 구성
    contents = []
    for log in reversed(history_logs):  # 과거 -> 최신 순서
        contents.append(
            types.Content(
                role="user",
                parts=[types.Part.from_text(text=log.question)]
            )
        )
        contents.append(
            types.Content(
                role="model",
                parts=[types.Part.from_text(text=log.response)]
            )
        )

    contents.append(
        types.Content(
            role="user",
            parts=[types.Part.from_text(text=prompt)]
        )
    )

    logger.info(f"ai_call_start prompt_length={len(prompt)}")

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = await asyncio.wait_for(
                client.aio.models.generate_content(
                    model="gemini-3.6-flash",
                    contents=contents,
                    config=types.GenerateContentConfig(
                        system_instruction="너는 친절하고 유용한 AI 보조원이야.",
                    )
                ),
                timeout=TIMEOUT_SECONDS
            )

            ai_text = response.text
            logger.info("ai_call_success")
            return ai_text

        except asyncio.TimeoutError:
            logger.error(f"ai_call_failed attempt={attempt} reason=timeout")

            # if attempt < MAX_RETRIES:
            #     wait_time = RETRY_DELAY_SECONDS * attempt
            #     logger.info(f"ai_call_retry attempt={attempt} wait={wait_time}s")
            #     await asyncio.sleep(wait_time)
            #     continue

            if attempt < MAX_RETRIES:
                # Exponential backoff: 2초 → 4초 → 8초 ...
                wait_time = RETRY_DELAY_SECONDS * (2 ** (attempt - 1))
                logger.info(f"ai_call_retry attempt={attempt} wait={wait_time}s")
                await asyncio.sleep(wait_time)
                continue

            return "현재 응답이 지연되고 있어요. 잠시 후 다시 시도해 주세요. (error: AI_TIMEOUT)"

        except errors.APIError as e:
            # 503(UNAVAILABLE), 429(RESOURCE_EXHAUSTED) 등 재시도 가능한 오류 처리
            status = getattr(e, "status", None) or getattr(e, "code", None)
            is_retryable = status in (503, 429, "UNAVAILABLE", "RESOURCE_EXHAUSTED")

            logger.error(f"ai_call_failed attempt={attempt} reason={str(e)}")

            # if is_retryable and attempt < MAX_RETRIES:
            #     wait_time = RETRY_DELAY_SECONDS * attempt  # 점진적 대기 (2s, 4s, ...)
            #     logger.info(f"ai_call_retry attempt={attempt} wait={wait_time}s")
            #     await asyncio.sleep(wait_time)
            #     continue

            if is_retryable and attempt < MAX_RETRIES:
                # 429/503 오류는 Exponential Backoff를 적용해 재시도
                wait_time = RETRY_DELAY_SECONDS * (2 ** (attempt - 1))
                logger.info(f"ai_call_retry attempt={attempt} wait={wait_time}s")
                await asyncio.sleep(wait_time)
                continue

            return "AI 서비스가 현재 혼잡합니다. 잠시 후 다시 시도해 주세요."

        except Exception as e:
            logger.error(f"ai_call_failed reason={str(e)}")
            return f"AI 서비스 응답 오류가 발생했습니다. (error: {type(e).__name__})"