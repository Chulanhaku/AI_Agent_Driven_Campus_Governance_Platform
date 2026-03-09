import uvicorn

from app.config.settings import get_settings


def main() -> None:
    settings = get_settings()

    uvicorn.run(
        "app.main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=settings.debug,
    )


if __name__ == "__main__":
    main()