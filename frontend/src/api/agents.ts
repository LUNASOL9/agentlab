// import type: 타입만 가져와요. 실행되는 코드에는 안 들어가요.
import type { Agent, AgentCreateInput } from '../types/agent'
import { toErrorMessage } from '../utils/errors'

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

// 에이전트를 하나 만들어요. (POST /api/agents)
// 성공하면 서버가 만든 에이전트(id, created_at 포함)를 돌려줘요.
export async function createAgent(input: AgentCreateInput): Promise<Agent> {
  // fetch의 두 번째 인자로 요청 방법을 정해요.
  const response = await fetch('/api/agents', {
    // method: HTTP 메서드예요. 안 쓰면 GET이에요.
    method: 'POST',
    // headers: 본문이 JSON이라고 알려 줘요. 그래야 FastAPI가 JSON으로 읽어요.
    headers: { 'Content-Type': 'application/json' },
    // body: 보낼 내용이에요. JSON.stringify는 객체를 JSON 글자로 바꿔요. (Jackson의 writeValueAsString)
    body: JSON.stringify(input),
  })

  if (!response.ok) {
    // 에러 본문(JSON)을 읽어요. 본문이 JSON이 아니면(예: 백엔드가 꺼져서 502) null로 해요.
    const body = await response.json().catch(() => null)
    throw new Error(toErrorMessage(response.status, body))
  }

  return response.json()
}
