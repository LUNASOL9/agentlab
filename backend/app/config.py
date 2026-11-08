from pydantic_settings import BaseSettings, SettingsConfigDict


# application.yml 역할이에요. 환경변수나 backend/.env 파일에서 값을 읽어요.
class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # 개발용 DB 주소예요. 형식: "드라이버://사용자:비밀번호@주소:포트/DB이름?옵션"
    # 127.0.0.1: 내 PC 자신이에요. localhost라고 쓰면 Windows에서 한참 멈출 수 있어요.
    # connect_timeout=5: DB가 꺼져 있으면 5초만 기다리고 포기해요.
    database_url: str = (
        "postgresql+psycopg://agentlab:agentlab@127.0.0.1:5432/agentlab?connect_timeout=5"
    )

    # 테스트 전용 DB 주소예요. 테스트는 이 DB를 매번 비우고 다시 만들어요.
    test_database_url: str = (
        "postgresql+psycopg://agentlab:agentlab@127.0.0.1:5432/agentlab_test?connect_timeout=5"
    )


settings = Settings()
