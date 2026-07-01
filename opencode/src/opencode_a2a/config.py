from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
        populate_by_name=True,
    )

    opencode_base_url: str = Field(
        default="http://127.0.0.1:4096",
        alias="OPENCODE_BASE_URL",
    )

    a2a_host: str = Field(default="127.0.0.1", alias="A2A_HOST")
    a2a_port: int = Field(default=8000, alias="A2A_PORT")
    a2a_public_url: str | None = Field(default=None, alias="A2A_PUBLIC_URL")

    a2a_title: str = Field(default="OpenCode", alias="A2A_TITLE")
    a2a_description: str = Field(
        default="AI-powered coding assistant",
        alias="A2A_DESCRIPTION",
    )
    a2a_version: str = Field(default="1.0.0", alias="A2A_VERSION")

    a2a_documentation_url: str | None = Field(
        default="https://opencode.ai/docs",
        alias="A2A_DOCUMENTATION_URL",
    )
    a2a_provider_org: str | None = Field(default="Red Hat", alias="A2A_PROVIDER_ORG")
    a2a_provider_url: str | None = Field(default="https://redhat.com", alias="A2A_PROVIDER_URL")
    a2a_icon_url: str | None = Field(
        default="https://opencode.ai/favicon-v3.svg",
        alias="A2A_ICON_URL",
    )

    @property
    def public_url(self) -> str:
        if self.a2a_public_url:
            return self.a2a_public_url
        return f"http://{self.a2a_host}:{self.a2a_port}"
