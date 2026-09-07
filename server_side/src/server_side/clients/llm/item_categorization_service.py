from pathlib import Path

from openai import OpenAI

from server_side.core.config import settings

_PROMPT_FILE = Path(__file__).resolve().parents[4] / "ai_prompts" / "invoice_item_categorization.md"

_REASONING_EFFORT = "medium"


class ItemCategorizationError(RuntimeError):
    pass


def _load_prompt_template() -> str:
    return _PROMPT_FILE.read_text(encoding="utf-8")


def categorize_item(item_description: str, categories: list[str]) -> str:
    if not settings.openai_api_key:
        raise ItemCategorizationError("OPENAI_API_KEY is not configured.")

    prompt = _load_prompt_template().format(
        CATEGORIES=", ".join(categories),
        ITEM_DESCRIPTION=item_description,
    )

    client = OpenAI(api_key=settings.openai_api_key)
    response = client.chat.completions.create(
        model=settings.openai_model,
        messages=[{"role": "user", "content": prompt}],
        reasoning_effort=_REASONING_EFFORT,
    )

    category = (response.choices[0].message.content or "").strip()
    if not category:
        raise ItemCategorizationError("The AI model returned an empty category.")

    return category
