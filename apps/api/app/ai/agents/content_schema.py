from pydantic import BaseModel, Field


class GeneratedContent(BaseModel):
    title: str
    hook: str
    script: str
    caption: str
    hashtags: list[str] = Field(default_factory=list)
    cta: str
    format: str
    platform: str
    objective: str
