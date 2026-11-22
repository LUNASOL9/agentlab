// 입력 검사 에러(422)에 들어 있는 문제 하나의 모양이에요.
// 예: { "loc": ["body", "name"], "msg": "String should have at least 1 character" }
type ValidationIssue = {
  // loc: 문제가 난 위치예요. 마지막 값이 필드 이름이에요.
  loc: (string | number)[]
  // msg: 무엇이 문제인지 알려 주는 설명이에요.
  msg: string
}

// FastAPI가 에러 때 보내는 본문의 모양이에요. 본문이 JSON이 아니면 null로 받아요.
// 409 (우리가 만든 에러): { "detail": "Agent name already exists: alpha" }
// 422 (입력 검사 에러):  { "detail": [{ "loc": [...], "msg": "..." }, ...] }
type ErrorBody = { detail?: string | ValidationIssue[] } | null

// 에러 응답을 화면에 보여 줄 문구로 바꿔요.
export function toErrorMessage(status: number, body: ErrorBody): string {
  // ?.: body가 null이면 에러 없이 undefined를 줘요.
  const detail = body?.detail
  // typeof: 값의 종류를 글자로 알려 줘요. 글자면 'string'이에요.
  if (typeof detail === 'string') {
    return detail
  }
  // Array.isArray: 배열이면 true예요.
  if (Array.isArray(detail)) {
    // 문제마다 "필드: 설명"으로 바꾸고, 쉼표로 이어 붙여요.
    // at(-1): 배열의 마지막 값이에요. (Python의 [-1])
    return detail.map((issue) => `${issue.loc.at(-1)}: ${issue.msg}`).join(', ')
  }
  // 그 밖에는 상태 코드만 알려 줘요.
  return `요청이 실패했어요 (HTTP ${status})`
}
