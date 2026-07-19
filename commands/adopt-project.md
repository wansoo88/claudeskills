---
description: 이미 진행 중인 기존 프로젝트에 이 스킬셋을 도입한다(기존 파일 보존, 없는 것만 추가).
---

`project-adopt` 스킬을 사용해 **현재 폴더의 기존 프로젝트**에 스킬셋을 도입하라.

절차(스킬 순서를 따름):
1. 기존 코드/설정/문서를 스캔해 스택과 진행 단계를 추정한다.
2. 스캔으로 못 알아낸 것만 짧게 한국어로 보강 인터뷰(AskUserQuestion).
3. `mode:"adopt"`와 추정 `current_stage`를 담아 project-brief.json 작성.
4. `scaffold_project.py --adopt --stage <N>` 실행(기존 보존, `*.generated.md`는 병합 안내).
5. 어느 단계부터 시작할지 제안하고 `/next-stage`로 연결.

기존 파일은 절대 임의로 덮어쓰지 말 것. 추가 지시: $ARGUMENTS
