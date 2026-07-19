---
name: architecture-design
description: 2단계 설계에서 AWS 3-tier(웹/WAS/DB) 아키텍처를 설계하고 draw.io 다이어그램을 생성할 때 사용한다. requirements.md와 project-brief.json을 읽어 gen_drawio.py로 architecture.drawio를 만들고, 트래픽 흐름·보안·확장 전략을 문서화한다.
---

# 아키텍처 설계 (2단계)

당신은 지금 **시니어 인프라 아키텍트**다. 목표는 요구사항에 맞는 **AWS 3-tier 아키텍처**를 그리고, 왜 그렇게 설계했는지 쉬운 한국어로 설명하는 것이다.

## 진행 순서

### 1. 입력 읽기
`docs/01-interview/requirements.md`와 `docs/01-interview/project-brief.json`을 읽는다. 규모(data_scale/scale_users)·민감정보·스택을 확인한다.

### 2. draw.io 생성
```bash
python "${CLAUDE_PLUGIN_ROOT}/skills/architecture-design/scripts/gen_drawio.py" \
  --brief docs/01-interview/project-brief.json \
  --out docs/02-design/architecture.drawio
```
생성되는 기본 구조: 사용자 → Route53/CloudFront → ALB(퍼블릭) → Web(React) → App(Docker) → RDS(프라이빗) + CloudWatch/Secrets Manager.

### 3. 프로젝트에 맞게 보정
`reference/aws-3tier-patterns.md`를 참고해 규모/요구에 맞게 조정:
- 소규모면 단순화(예: ECS 대신 단일 컨테이너), 대규모면 Auto Scaling·읽기 복제본 추가.
- 실시간 요구면 큐/스트림(SQS/Kinesis) 추가 검토.
- 민감정보면 프라이빗 서브넷·암호화·접근권한 분리 강조.

### 4. 설명서 작성
`docs/02-design/`에 구성요소·트래픽 흐름·확장 전략·대략 비용·단일장애점 대응을 한국어로 정리. Confluence 업로드는 사용자 확인 후.

### 5. 마무리
다이어그램을 어떻게 열어 보는지 안내(app.diagrams.net 또는 Confluence draw.io 앱)하고, DB 상세는 `db-modeling`, 보안은 `security-design`으로 이어간다고 알린다.

## 하지 말 것
- 규모에 안 맞는 과설계. 확정 안 된 스택을 단정하지 말 것(가정 표시).
