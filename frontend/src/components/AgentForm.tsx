import type { SubmitEvent } from 'react'
import { useState } from 'react'

import { createAgent } from '../api/agents'

type AgentFormProps = {
  onCreated: () => void
}

export function AgentForm({ onCreated }: AgentFormProps) {
  // 입력칸 하나에 state 하나예요. 입력칸에는 늘 state 값이 보여요. (제어 컴포넌트)
  const [name, setName] = useState('')
  const [description, setDescription] = useState('')
  const [model, setModel] = useState('mock')
  const [systemPrompt, setSystemPrompt] = useState('You are a helpful assistant.')
  const [temperature, setTemperature] = useState(0.7)
  const [maxSteps, setMaxSteps] = useState(5)

  const [created, setCreated] = useState<string | null>(null)

  // 보내는 중이면 true예요. 그동안 버튼을 막아서 두 번 누르지 못하게 해요.
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // 폼을 제출하면(만들기 버튼이나 엔터) 불려요.
  async function handleSubmit(event: SubmitEvent<HTMLFormElement>) {
    // 브라우저 기본 동작(페이지 새로고침)을 막아요.
    event.preventDefault()
    setSubmitting(true)
    setError(null)

    try {
      setCreated(null)
      await createAgent({
        name,
        // ||: 왼쪽이 빈 글자면 오른쪽 값을 써요. 설명이 비었으면 null로 보내요.
        description: description || null,
        model,
        system_prompt: systemPrompt,
        temperature,
        max_steps: maxSteps,
      })
      // 성공하면 이름과 설명 칸을 비우고, 부모(App)에게 알려요.
      setCreated(name)
      setName('')
      setDescription('')
      onCreated() // 만들기에 성공하면 목록을 다시 불러요.
    } catch (err) {
      // createAgent가 던진 Error의 문구를 보여줘요.
      setError((err as Error).message)
    } finally {
      setSubmitting(false)
    }
  }

  return (
    // onSubmit: 폼을 제출할 때 부를 함수예요.
    <form className="agent-form" onSubmit={handleSubmit}>
      <label>
        이름
        <input value={name} onChange={(e) => setName(e.target.value)} required maxLength={100} />
      </label>

      <label>
        설명
        <input
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          maxLength={500}
        />
      </label>

      <label>
        모델
        <input
          value={model}
          onChange={(e) => setModel(e.target.value)}
          required
          maxLength={100}
        />
      </label>

      <label>
        시스템 프롬프트
        <textarea
          value={systemPrompt}
          onChange={(e) => setSystemPrompt(e.target.value)}
          rows={3}
        />
      </label>

      <label>
        temperature
        <input
          type="number"
          min={0}
          max={1}
          step={0.1}
          value={temperature}
          onChange={(e) => setTemperature(Number(e.target.value))}
        />
      </label>

      <label>
        최대 스텝
        <input
          type="number"
          min={1}
          max={20}
          step={1}
          value={maxSteps}
          onChange={(e) => setMaxSteps(Number(e.target.value))}
        />
      </label>

      {error && <p className="error">{error}</p>}
      {created && <p className="success">만들었어요: {created}</p>}
      <button type="submit" disabled={submitting}>
        {submitting ? '만드는 중...' : '만들기'}
      </button>
    </form>
  )
}
