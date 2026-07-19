---
description: 현재 프로젝트의 README.md를 산출물·코드 기반으로 생성/갱신한다.
---

`readme-writer` 스킬을 사용해 이 프로젝트의 `README.md`를 작성/갱신하라.

절차(스킬 순서를 따름):
1. `CLAUDE.md`·`skill.md`·`docs/`와 실제 설정(package.json/requirements/Dockerfile/compose)을 읽는다.
2. `reference/readme-template-ko.md` 구조로, 처음 보는 사람이 30분 내 실행 가능한 README를 작성.
3. 적은 명령·경로가 실제로 존재하는지 교차 확인(추측 금지).
4. 기존 README가 있으면 덮어쓰기 전 확인하고 좋은 부분은 병합.

추가 지시(강조할 섹션 등): $ARGUMENTS
