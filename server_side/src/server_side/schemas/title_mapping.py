from pydantic import BaseModel


class TitleTypeMappingItem(BaseModel):
    title: str
    type: str | None = None
    merchant: str | None = None


class TitleTypeMappingUpdateRequest(BaseModel):
    mappings: list[TitleTypeMappingItem]
