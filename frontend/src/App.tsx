// [3단계 7] 이 줄부터 "여기까지" 줄까지 지워요. 목록 없이 제목만 있는 지금 화면이에요.
import './App.css'

function App() {
  return (
    <main>
      <h1>AgentLab</h1>
      <p className="subtitle">LLM 에이전트를 실행하고, 기록하고, 비교·평가하는 테스트베드</p>

      <h2>에이전트 목록</h2>
      <p>목록은 7번에서 보여 줄 거예요.</p>
    </main>
  )
}

export default App
// [3단계 7] 여기까지 지워요.

// [3단계 7] 위를 지운 다음, 아래 주석을 모두 풀고 ____를 채워요.
// // useState, useEffect: React가 주는 기능(훅)이에요. 이름이 use로 시작해요.
// import { useEffect, useState } from 'react'
//
// import { fetchAgents } from './api/agents'
// import { AgentList } from './components/AgentList'
// import type { Agent } from './types/agent'
// import './App.css'
//
// function App() {
//   // useState: 값이 바뀌면 화면을 다시 그려 주는 변수예요. [지금 값, 값을 바꾸는 함수]를 돌려줘요.
//   // useState<Agent[]>([]): Agent 배열을 담고, 처음 값은 빈 배열이에요.
//   const [agents, setAgents] = useState<Agent[]>(____)
//   // 처음에는 아직 불러오는 중이라서 true예요.
//   const [loading, setLoading] = useState(____)
//   // 에러 문구예요. 에러가 없으면 null이에요.
//   const [error, setError] = useState<string | null>(null)
//
//   // useEffect: 화면이 그려진 다음에 할 일이에요. 여기서 목록을 불러와요.
//   // 두 번째 인자 []: "처음 한 번만" 실행하라는 뜻이에요.
//   useEffect(() => {
//     fetchAgents()
//       .then((data) => setAgents(data)) // 성공하면 목록을 넣어요.
//       .catch((e: Error) => setError(e.message)) // 실패하면 에러 문구를 넣어요.
//       .finally(() => setLoading(____)) // 성공하든 실패하든 "불러오는 중"을 끝내요.
//   }, ____)
//
//   return (
//     <main>
//       <h1>AgentLab</h1>
//       <p className="subtitle">LLM 에이전트를 실행하고, 기록하고, 비교·평가하는 테스트베드</p>
//
//       <h2>에이전트 목록</h2>
//       {/* 조건 && 화면: 조건이 true일 때만 화면을 보여줘요. */}
//       {loading && <p>불러오는 중...</p>}
//       {error && <p className="error">{error}</p>}
//       {/* agents={...}: AgentList 컴포넌트에 props로 목록을 넘겨요. (함수에 인자를 넘기는 것과 같아요) */}
//       {!loading && !error && <AgentList agents={____} />}
//     </main>
//   )
// }
//
// export default App
