from fastapi import FastAPI

# Spring Boot의 @SpringBootApplication처럼 애플리케이션의 진입점이에요.
app = FastAPI(title="AgentLab API", version="0.1.0")


# @GetMapping("/")과 같아요. 반환한 dict는 자동으로 JSON 응답이 돼요.
@app.get("/")
def read_root() -> dict[str, str]:
    return {"message": "Hello, AgentLab!"}
