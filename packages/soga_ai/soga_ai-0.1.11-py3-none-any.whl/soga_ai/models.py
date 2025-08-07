from pydantic import BaseModel


class SogaResult(BaseModel):
    download_url: str | None = None
    save_path: str | None = None
    success: bool = True
