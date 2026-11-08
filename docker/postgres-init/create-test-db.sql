-- 테스트 전용 DB를 만들어요. 개발용 DB(agentlab)는 compose.yaml의 POSTGRES_DB가 만들어요.
-- 이 파일은 볼륨이 비어 있을 때(DB를 처음 만들 때) 한 번만 실행돼요.
CREATE DATABASE agentlab_test;
