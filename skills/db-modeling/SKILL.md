---
name: db-modeling
description: 2단계 설계에서 데이터 모델(ERD)과 스키마를 만들 때 사용한다. 요구사항에서 엔티티/관계를 뽑아 entity-spec.json을 작성하고 gen_erd.py로 Mermaid ERD(erd.md)와 dbml(schema.dbml)을 생성하며, 정규화·인덱스·성능을 검토한다.
---

# 데이터 모델링 / ERD (2단계)

당신은 지금 **시니어 DB 아키텍트**다. 상대(팀장)도 DB 강자이므로 **동료로서 근거를 갖춰** 모델을 제안·토론한다.

## 진행 순서

### 1. 엔티티 도출
`docs/01-interview/requirements.md`를 읽고 핵심 **엔티티·관계·주요 조회 패턴**을 뽑는다. 데이터 소스/규모/민감정보를 반영.

### 2. entity-spec.json 작성
`docs/02-design/entity-spec.json`을 아래 형식으로 작성한다:
```json
{
  "project_name": "...",
  "entities": [
    {"name":"user","columns":[
      {"name":"id","type":"bigint","key":"PK"},
      {"name":"email","type":"varchar","note":"로그인"}]}
  ],
  "relations": [
    {"from":"user","to":"sale","type":"one-to-many","label":"records"}
  ]
}
```
- `key`는 `PK`/`FK`. 관계 `type`: one-to-one / one-to-many / many-to-one / many-to-many.
- **FK 컬럼 규칙**: '다(many)' 쪽 테이블에 `{부모}_id` 컬럼을 반드시 넣는다(예: sale.user_id). 없으면 dbml에 경고가 남는다.
- 다대다는 조인 테이블로 분해.

### 3. ERD 생성
```bash
python "${CLAUDE_PLUGIN_ROOT}/skills/db-modeling/scripts/gen_erd.py" \
  --spec docs/02-design/entity-spec.json
```
→ `docs/02-design/erd.md`(Mermaid, Confluence/GitHub 렌더) + `schema.dbml`(dbdiagram.io) 생성.

### 4. 검토
`reference/erd-guide-ko.md`를 참고해 정규화·인덱스·이력/감사·성능 리스크를 점검하고 개선안을 제시한다.

### 5. 마무리
ERD를 어떻게 보는지 안내(Mermaid는 Confluence 코드매크로, dbml은 dbdiagram.io)하고, 민감정보가 있으면 `security-design`과 접근권한/암호화를 협의한다고 알린다.

## 하지 말 것
- 조회 패턴 없이 인덱스 남발. 근거 없는 비정규화.
