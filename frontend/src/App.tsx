import { useEffect, useState } from 'react'

import { fetchAgents } from './api/agents'
import { AgentForm } from './components/AgentForm'
import { AgentList } from './components/AgentList'
import type { Agent } from './types/agent'
import './App.css'

function App() {
  // useState: 값이 바뀌면 화면을 다시 그려 주는 변수예요. [지금 값, 값을 바꾸는 함수]를 돌려줘요.
  const [agents, setAgents] = useState<Agent[]>([])
  // 처음에는 아직 불러오는 중이라서 true예요.
  const [loading, setLoading] = useState(true)
  // 에러 문구예요. 에러가 없으면 null이에요.
  const [error, setError] = useState<string | null>(null)

  // 목록을 불러오는 함수예요. 화면이 처음 그려질 때, 그리고 에이전트를 만든 뒤에 불러요.
  function loadAgents() {
    fetchAgents()
      .then((data) => {
        setAgents(data) // 성공하면 목록을 넣고,
        setError(null) // 전에 났던 에러 문구는 지워요.
      })
      .catch((e: Error) => setError(e.message)) // 실패하면 에러 문구를 넣어요.
      .finally(() => setLoading(false)) // 성공하든 실패하든 "불러오는 중"을 끝내요.
  }

  // useEffect: 화면이 그려진 다음에 할 일이에요. []: 처음 한 번만 실행해요.
  useEffect(() => {
    loadAgents()
  }, [])

  return (
    <main>
      <h1>AgentLab</h1>
      <p className="subtitle">LLM 에이전트를 실행하고, 기록하고, 비교·평가하는 테스트베드</p>

      <h2>에이전트 만들기</h2>
      {/* onCreated={loadAgents}: 만들기에 성공하면 목록을 다시 불러요. (함수도 props로 넘길 수 있어요) */}
      <AgentForm onCreated={loadAgents} />

      <h2>에이전트 목록 ({agents.length})</h2>
      {/* 조건 && 화면: 조건이 true일 때만 화면을 보여줘요. */}
      {loading && <p>불러오는 중...</p>}
      {error && <p className="error">{error}</p>}
      {!loading && !error && <AgentList agents={agents} />}
    </main>
  )
}

export default App
