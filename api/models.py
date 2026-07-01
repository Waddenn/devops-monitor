from dataclasses import dataclass, field

from pydantic import BaseModel, Field


@dataclass
class Server:
    """Internal server representation."""

    id: int
    name: str
    host: str
    port: int
    status: str = "unknown"
    tags: list[str] = field(default_factory=list)

    def base_url(self) -> str:
        scheme = "https" if self.port == 443 else "http"
        return f"{scheme}://{self.host}:{self.port}"


class ServerIn(BaseModel):
    """Payload used to register a server."""

    name: str = Field(min_length=1, max_length=80)
    host: str = Field(min_length=1, max_length=255)
    port: int = Field(default=8080, ge=1, le=65535)
    tags: list[str] = Field(default_factory=list)


class ServerOut(BaseModel):
    """Server data returned by the API."""

    id: int
    name: str
    host: str
    port: int
    status: str
    tags: list[str] = Field(default_factory=list)

    model_config = {"from_attributes": True}
