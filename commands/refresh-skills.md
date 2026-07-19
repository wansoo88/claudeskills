---
description: 월 1회 스킬셋을 최신 트렌드로 갱신하고 plugin.json 버전을 올린다(로컬/수동).
---

`refresh-skills` 스킬을 사용해 이 스킬셋을 최신 상태로 갱신하라.

절차(스킬 순서를 따름):
1. Claude Skills·AWS·React·Docker·보안·테스트 최신 동향을 조사(가능하면 deep-research).
2. 변경점을 한국어로 요약(무엇이 새롭고 무엇이 deprecated인지, 근거 링크).
3. 영향받는 `skills/*/reference/*.md`만 갱신.
4. `bump_version.py --level minor --note "..."` 로 버전 상승 + CHANGELOG 기록.
5. 변경 요약 보고.

추가 지시(특정 주제 집중 등): $ARGUMENTS
