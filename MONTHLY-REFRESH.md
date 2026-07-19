# 월간 갱신 루틴 (로컬/수동)

> 목적: 스킬셋을 매월 최신 트렌드로 유지. (리서치 검증: 세션 예약작업은 **7일 후 만료**되어 월간 자동화에 부적합 → 로컬/수동 루틴 채택.)

## 왜 버전 bump가 핵심인가
Claude Code는 `plugin.json`의 `version`이 바뀔 때만 사용자/팀에게 업데이트를 전달한다. 따라서 **월 1회 버전 올리기 = 배포 트리거**.

## 매월 1회 절차 (약 15~30분)
1. Claude Code를 이 플러그인 저장소에서 열고 **`/refresh-skills`** 실행.
2. 조사 → 변경점 요약 → `reference/*.md` 갱신 → `bump_version.py`로 버전 상승까지 스킬이 안내.
3. 변경을 커밋(팀 공유 저장소면 push).

## 수동으로 버전만 올릴 때
```bash
python skills/refresh-skills/scripts/bump_version.py --level minor --note "2026-08 트렌드 반영"
```

## 리마인더 거는 법 (택1, 무료)
- **캘린더 반복 일정**(매월 1일) — 가장 단순.
- **OS 예약 작업**: Windows 작업 스케줄러 / cron 으로 매월 알림 스크립트.
- (선택) 사내 GitHub이 생기면 GitHub Actions `schedule: cron`으로 자동화 가능 — 지금은 로컬/수동.

## 갱신 시 점검 포인트
- Claude Skills 스펙 변화는 **agentskills.io** 기준(구 anthropics/skills 스펙은 stub).
- 파괴적/중요 변경은 `CHANGELOG.md`에 명확히.
- reference 갱신 후 각 SKILL.md 본문이 여전히 500줄 미만인지 확인.

## 버전 규칙(semver)
- **minor**(기본): 트렌드 반영·항목 추가.
- **patch**: 오탈자·소규모 수정.
- **major**: 구조·호환성 변경.
