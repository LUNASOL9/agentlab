import type { Agent } from '../types/agent'
import { formatDateTime } from '../utils/format'

// 이 컴포넌트가 받는 값(props)의 모양이에요. 함수 매개변수의 타입과 같아요.
type AgentListProps = {
  agents: Agent[]
}

// 컴포넌트: 화면 조각을 그리는 함수예요. 이름은 대문자로 시작해요.
// { agents }: 받은 props 객체에서 agents만 꺼내요. (구조 분해)
export function AgentList({ agents }: AgentListProps) {
  // 목록이 비어 있으면 표 대신 안내 문구를 보여줘요.
  if (agents.length === 0) {
    return <p className="empty">아직 에이전트가 없어요. /docs에서 하나 만들어 보세요.</p>
  }

  // 돌려주는 값이 화면이에요. HTML처럼 생겼지만 JSX라는 자바스크립트 문법이에요.
  // class 대신 className을 써요. (class는 자바스크립트 예약어라서요)
  return (
    <table className="agent-table">
      <thead>
        <tr>
          <th>이름</th>
          <th>설명</th>
          <th>모델</th>
          <th>temperature</th>
          <th>최대 스텝</th>
          <th>만든 시각</th>
        </tr>
      </thead>
      <tbody>
        {/* { }: JSX 안에서 자바스크립트 값을 쓸 때 감싸요. */}
        {/* map: 배열의 에이전트 하나하나를 <tr> 한 줄로 바꿔요. (Java Stream의 map과 같아요) */}
        {agents.map((agent) => (
          // key: React가 줄을 구분하는 이름표예요. 겹치지 않는 값(id)을 써요.
          <tr key={agent.id}>
            <td>{agent.name}</td>
            {/* ??: 왼쪽 값이 null이면 오른쪽 값을 써요. */}
            <td>{agent.description ?? '-'}</td>
            <td>{agent.model}</td>
            <td>{agent.temperature}</td>
            <td>{agent.max_steps}</td>
            <td>{formatDateTime(agent.created_at)}</td>
          </tr>
        ))}
      </tbody>
    </table>
  )
}
