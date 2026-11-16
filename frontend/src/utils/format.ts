// 서버가 준 UTC 시간 글자를 한국 시간으로 바꿔서 보여줘요.
// 예: "2026-11-07T00:54:49Z" → "2026. 11. 7. 오전 9:54:49"
export function formatDateTime(isoText: string): string {
  // new Date(글자): 글자를 날짜 객체로 바꿔요. 끝의 Z(UTC)도 알아서 읽어요.
  // toLocaleString('ko-KR', ...): 한국어 형식의 글자로 바꿔요.
  // timeZone: 어느 지역 시간으로 보여 줄지예요. 'Asia/Seoul'은 한국 시간(UTC+9)이에요.
  return new Date(isoText).toLocaleString('ko-KR', { timeZone: 'Asia/Seoul' })
}
