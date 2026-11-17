// 백엔드 API가 돌려주는 에이전트 한 개의 모양이에요.
// backend/app/schemas/agent.py의 AgentRead와 짝이에요. (Java의 DTO나 record 같은 거예요)
export type Agent = {
  // number: TypeScript에는 숫자 타입이 하나예요. Java의 int, double을 모두 number로 써요.
  id: number
  name: string
  // string | null: 글자이거나, 값이 없으면 null이에요. (Python의 str | None)
  description: string | null
  model: string
  system_prompt: string
  temperature: number
  max_steps: number
  // 시간은 JSON에서 글자로 와요. 예: "2026-11-07T00:54:49.334043Z"
  created_at: string
  updated_at: string
}
