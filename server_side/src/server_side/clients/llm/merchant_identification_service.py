from pathlib import Path

from openai import OpenAI

from server_side.core.config import settings

_PROMPT_FILE = (
    Path(__file__).resolve().parents[4] / "ai_prompts" / "invoice_item_merchant_identification.md"
)

_REASONING_EFFORT = "low"


class MerchantIdentificationError(RuntimeError):
    pass


def _load_prompt_template() -> str:
    return _PROMPT_FILE.read_text(encoding="utf-8")


def identify_merchant(item_description: str, merchants: list[str]) -> str:
    if not settings.openai_api_key:
        raise MerchantIdentificationError("OPENAI_API_KEY is not configured.")

    prompt = _load_prompt_template().format(
        MERCHANTS=", ".join(merchants),
        ITEM_DESCRIPTION=item_description,
    )

    client = OpenAI(api_key=settings.openai_api_key)
    response = client.chat.completions.create(
        model=settings.openai_model,
        messages=[{"role": "user", "content": prompt}],
        reasoning_effort=_REASONING_EFFORT,
    )

    merchant = (response.choices[0].message.content or "").strip()
    if not merchant:
        raise MerchantIdentificationError("The AI model returned an empty merchant.")

    return merchant
