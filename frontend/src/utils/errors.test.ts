import { describe, expect, it } from 'vitest'
import { toErrorMessage } from './errors'

describe('toErrorMessage', () => {
  it('detail이 글자면(409) 그대로 보여줘요', () => {
    const body = { detail: 'Agent name already exists: alpha' }

    expect(toErrorMessage(409, body)).toBe('Agent name already exists: alpha')
  })

  it('detail이 목록이면(422) "필드: 설명"으로 보여줘요', () => {
    // loc의 마지막 값이 필드 이름이에요.
    const body = {
      detail: [{ loc: ['body', 'name'], msg: 'String should have at least 1 character' }],
    }

    expect(toErrorMessage(422, body)).toBe('name: String should have at least 1 character')
  })

  it('본문이 없으면 상태 코드를 보여줘요', () => {
    // 백엔드가 꺼져 있으면 Vite가 502를 줘요. 본문이 JSON이 아니라서 null로 받아요.
    expect(toErrorMessage(502, null)).toBe('요청이 실패했어요 (HTTP 502)')
  })

  it('422 에러가 두 개일 때 테스트', () => {
    // 이름도 비고 temperature도 1을 넘으면, 422의 detail 목록에 문제가 2개 들어와요.
    const body = {
      detail: [
        { loc: ['body', 'name'], msg: 'String should have at least 1 character' },
        { loc: ['body', 'temperature'], msg: 'Input should be less than or equal to 1' }
      ]
    }

    expect(toErrorMessage(422, body)).toBe(
      'name: String should have at least 1 character, temperature: Input should be less than or equal to 1',
    )
  })
})
