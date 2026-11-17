// import type: 타입만 가져와요. 실행되는 코드에는 안 들어가요.
import type { Agent } from '../types/agent'

// 백엔드에서 에이전트 목록을 가져와요. (GET /api/agents)
// async 함수는 Promise를 돌려줘요. Promise<Agent[]>: "나중에 Agent 배열이 와요"라는 약속이에요.
// (Java의 CompletableFuture<List<Agent>>와 비슷해요)
export async function fetchAgents(): Promise<Agent[]> {
  // fetch: 브라우저에 들어 있는 HTTP 요청 함수예요. await: 응답이 올 때까지 기다려요.
  const response = await fetch('/api/agents')
  // response.ok: 상태 코드가 200~299면 true예요. 아니면 에러를 던져요.
  if (!response.ok) {
    throw new Error(`목록을 불러오지 못했어요 (HTTP ${response.status})`)
  }
  // 응답 본문(JSON 글자)을 자바스크립트 객체로 바꿔요.
  return response.json()
}
