---
name: security-review
description: 3단계 구현에서 커밋 전 '무조건' 실행하는 필수 보안리뷰. 사내 시큐어코딩 가이드 v1.0(E.S11.G07)과 OWASP 베이스라인, 2단계 보안설계 기준으로 변경 코드를 점검하고 심각도 4등급으로 판정해 security-review-log.md와 .review-state.json에 기록한다. security-reviewer 서브에이전트를 이름으로 호출해 수행.
---

# 보안리뷰 (3단계 필수 게이트)

목표: 커밋 전에 보안 취약점을 **공격자 관점**으로 점검하고 원장에 판정을 남긴다.
code-review와 함께 둘 다 통과해야 hook이 커밋을 허용한다.

**판정 기준은 사내 시큐어코딩 가이드 v1.0이다.** OWASP는 보조 기준이고, 충돌하면 사내 기준이 우선한다.

## 진행 순서

### 1. 기준 로드
- `reference/secure-coding-guide-ko.md` — **사내 시큐어코딩 가이드 v1.0**(제5~18조·심각도 등급·예외처리·별첨1 체크리스트 20항목). **주 기준.**
- `../security-design/reference/security-baseline-ko.md` — OWASP Top 10 / AWS 보조 기준.
- `docs/02-design/security.md` — 이 프로젝트의 security-review 체크리스트.

### 2. 사전 정적점검 (자동)
```bash
python <스킬경로>/scripts/scan_secure_coding.py --changed-only
```
(`<스킬경로>` = `${CLAUDE_PLUGIN_ROOT}/skills/security-review` 또는 `~/.claude/skills/security-review`)

가이드 위반 **후보**를 조항별로 뽑는다. **이건 게이트가 아니라 입력**이다. 도구가 못 보는 항목
(인가 누락·업로드 검증·세션 재발급·증적)은 3단계에서 사람/에이전트가 직접 본다.

### 3. security-reviewer 호출
`security-reviewer` 서브에이전트를 **이름으로 명시 호출**한다. 2단계 스캔 결과와 변경 파일 목록을 넘기고,
가이드 **제5조~제18조 + 별첨1 20항목**을 기준으로 점검하도록 지시한다.

가이드 제7장상 아래에 해당하면 **자동화 점검과 코드리뷰가 필수**다(생략 불가):
인터넷 공개 서비스 · 개인정보 처리 · 관리자 기능 · 외부 연동 · 중요정보 처리.

### 4. 판정 (제20조 심각도 4등급)
| 등급 | 예시 | 판정 |
|---|---|---|
| 긴급 | 원격 코드 실행, 인증 우회, 대규모 중요정보 유출 | **failed** |
| 높음 | 권한 상승, SQL 주입, 저장형 XSS, 비밀값 하드코딩, TLS 검증 비활성화 | **failed** |
| 보통 | 제한적 조건에서 악용 가능 | passed 가능 — **`docs/00-orchestration/followups.md`에 기한과 함께 등재 필수** |
| 낮음 | 악용 난이도 높고 영향 경미 | passed — 코멘트 |

판단은 **공격 가능성 · 노출 범위 · 정보 중요도 · 보완 통제 존재**를 함께 본다.
조치 후에는 **재리뷰로 유효성을 확인**하고 나서 닫는다(수정했다는 말만으로 닫지 않는다).

### 5. 기록 (게이트 핵심)
**`docs/03-build/security-review-log.md`** — 아래 4개 절을 모두 쓴다.
1. **취약점**: 위치(파일:라인) · 등급 · **가이드 조항** · CWE/OWASP · 재현 시나리오 · 수정안
2. **오탐 판정**: 스캔 후보 중 오탐으로 넘긴 항목과 **판단 근거** (가이드 제19조 3항 — 근거 없는 오탐 처리 금지)
3. **별첨1 체크리스트 20항목**: 적합 / 해당없음 / 개선필요 + 근거
4. **재리뷰**: 이전 지적의 조치 확인 결과

**`docs/03-build/.review-state.json`** — `security_review` 갱신 (code_review 항목은 병합·보존):
```json
{"security_review": {"status": "passed", "at": "2026-08-24T18:05:00",
                     "notes": "긴급·높음 0건 / 보통 1건 followups 등재",
                     "guide": "E.S11.G07 v1.0"}}
```

**증적은 별도 기준이 없으면 최소 3년 보관**하고, 로그에 중요정보가 들어가지 않도록 **마스킹**한다(제21조).

### 6. 예외처리 (가이드 제9장) — 남용 금지
긴급·높음이 남았는데 **배포 전 조치가 곤란**할 때만 쓴다. 사용자(개발책임자)에게 **AskUserQuestion으로 명시 승인**을 받고
아래 5개 필드를 **전부** 채운 뒤 `status`를 `"exception"`으로 기록한다. 하나라도 비면 훅이 차단한다.

```json
{"security_review": {
  "status": "exception", "at": "2026-08-24T18:05:00",
  "exception": {
    "target": "api/report.py:88 동적 정렬키",
    "reason": "레거시 리포트 스키마 의존, 허용목록 전환에 2주 필요",
    "risk": "내부망 한정·조회 전용, 인증 사용자만 도달",
    "compensating_controls": ["WAF 룰 추가", "감사로그 상시 수집"],
    "remediation_plan": "허용목록 전환 — 담당 김OO, 검증: 재리뷰",
    "expires_on": "2026-09-30",
    "approved_by": "개발책임자/정보보호사무국"
  }}}
```
- **`expires_on`이 지나면 훅이 자동으로 커밋을 다시 차단**한다. 영구 면제가 아니다.
- 예외는 followups.md에도 등재하고 만료 전에 닫는다.

### 7. 결과 안내
- **passed** & code-review도 passed → 커밋 가능.
- **failed** → 등급·조항·수정안 요약, 수정 후 **재리뷰**. 커밋은 계속 차단.
- **exception** → 승인 사실·만료일을 사용자에게 명시하고 followups 등재를 확인.

## 하지 말 것
- 형식적 통과. 민감정보를 다루는데 기본 항목(인증·암호화·비밀관리·로그 마스킹) 생략.
- 스캔 결과를 **근거 없이** 오탐 처리 (제19조 3항 위반).
- 사용자 승인 없이 `exception` 기록하거나, `.review-state.json`을 손으로 `passed`로 고치기.
