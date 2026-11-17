// vitest: 프론트엔드 테스트 도구예요. 백엔드의 pytest와 같은 역할이에요.
// describe: 테스트 묶음, it: 테스트 하나, expect(값).toBe(기댓값): "값이 기댓값과 같아야 해요" (assert)
import { describe, expect, it } from 'vitest'

import { formatDateTime } from './format'

describe('formatDateTime', () => {
  it('UTC 시간을 한국 시간(9시간 뒤)으로 바꿔요', () => {
    // API가 실제로 주는 모양 그대로예요. (소수점 아래 6자리 + 끝의 Z)
    expect(formatDateTime('2026-11-07T00:54:49.334043Z')).toBe('2026. 11. 7. 오전 9:54:49')
  })

  it('9시간을 더해서 날짜가 바뀌면 다음 날로 보여줘요', () => {
    // UTC 15시 4분 = 한국 시간으로 다음 날 0시 4분이에요.
    expect(formatDateTime('2026-11-07T15:04:05Z')).toBe('2026. 11. 8. 오전 12:04:05')
  })
})
