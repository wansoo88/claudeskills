# 사용 설명서 (USAGE)

> data-product-studio를 실제로 쓰는 법. 팀원 온보딩용. 설치는 [INSTALL.md](INSTALL.md) 참고.

---

## 이게 뭔가요
데이터 프로덕트를 **1인이 AI와 함께** 설계→구현→테스트→인수인계까지 만드는 스킬셋입니다. 부족한 역할(인프라·SW·DB 아키텍트, React 프론트, Docker 백엔드, QA)을 AI 서브에이전트가 맡고, 각 단계마다 산출물이 나오며, 리뷰는 강제됩니다.

---

## 🧭 진행 방식: 가이드 모드 (확인 후 이어감)

**각 단계가 끝나면 요약 + "다음 단계로 갈까요?"를 묻고, "예"면 자동으로 다음 단계로 이어갑니다.** 매번 커맨드를 다시 칠 필요 없이 흐르되, **멈춤 지점(검토·승인)은 유지**됩니다.

| 궁금증 | 답 |
|---|---|
| `/init-project` 하면 설계·구현까지 이어지나요? | **예 — 확인하면서.** 인터뷰+골격 생성 후 "설계로 갈까요?" → 예 → 자동으로 2단계, 각 단계 끝마다 요약+확인. |
| 중간에 멈출 수 있나요? | 예. 각 확인에서 **[예 / 이번 단계 수정 / 여기서 멈춤]**. 멈추면 나중에 `/next-stage`로 재개. |
| 3단계 리뷰는 건너뛰나요? | **아니요 — 하드 스톱.** code·security-review가 모두 passed 되기 전엔 진행·커밋 불가(훅 차단). |
| `/refresh-skills`는 자동 실행? | **아니요.** 월 1회 유지보수용, init/adopt와 **완전 별개**. |
| 확인 없이 쭉 진행하고 싶어요 | `/next-stage 쭉 진행` 처럼 지시하면 소프트 확인을 줄입니다(3단계 리뷰 게이트는 항상 유지). |

**왜 이 방식?** 단계마다 산출물을 **당신이 검토·승인**하면서도(요구사항) 흐름은 끊기지 않게 — 통제와 속도의 균형입니다.

---

## 시나리오 A. 신규 데이터 프로덕트 (가이드 모드)

```
1) 새 프로젝트 폴더에서 Claude Code 열기
2) /init-project
   → 한국어 인터뷰 4라운드 → CLAUDE.md·skill.md·docs 골격 생성
   → "2단계 설계로 갈까요?" [예/수정/멈춤]
3) 예 → 2단계 설계(draw.io+ERD+보안) → 요약 → "구현으로?" 
   → 예 → 3단계 구현(계획→개발→★리뷰 통과해야 진행/커밋)
   → 예 → 4단계 테스트 → 5단계 모니터링 → 6단계 인수인계
   (각 단계 끝에 요약+확인. 멈추면 나중에 /next-stage로 재개)
4) /write-readme → 프로젝트 README 생성 (원하는 시점 언제든)
```
한 번 시작하면 **확인하며 흐릅니다.** 중간에 "멈춤"을 고르면 그 자리에서 서고, `/next-stage`로 다시 이어갑니다.

---

## 시나리오 B. 이미 진행 중인(기존) 프로젝트

```
1) 기존 프로젝트 폴더에서 Claude Code 열기
2) /adopt-project
   → 스캔 → 갭 리포트(단계별 있음/부분/없음 + 권장 시작 단계)
   → 못 알아낸 것만 짧게 보강 인터뷰
   → 기존 파일 보존, 없는 것만 추가 (기존 CLAUDE.md는 CLAUDE.generated.md로 → 병합)
   → 권장 시작 단계 확인 [예/다른 단계/멈춤]
3) 확정한 단계부터 가이드 모드로 진행(각 단계 끝 요약+확인)
```
> 예: 코드는 있는데 테스트·리뷰가 없으면 → "3단계 리뷰 게이트 적용 + 4단계 테스트"부터 제안.

---

## 단계별 산출물

| 단계 | 커맨드 | 산출물(docs/) | 담당 역할 |
|---|---|---|---|
| 1 인터뷰 | /init-project · /adopt-project | 01-interview/ requirements.md, CLAUDE.md, skill.md | service-strategist |
| 2 설계 | /next-stage | 02-design/ architecture.drawio · erd.md · security.md | infra/software/db-architect |
| 3 구현 | /next-stage | 03-build/ implementation-plan.md · 코드 · 리뷰로그 | frontend-react · backend-docker |
| — 리뷰 | (3단계 내) | .review-state.json (게이트) | code-reviewer · security-reviewer |
| 4 테스트 | /next-stage | 04-test/ test-plan.md · test-report.md | qa-engineer |
| 5 모니터링 | /next-stage | 05-monitoring/ monitoring-plan.md | infra-architect |
| 6 인수인계 | /next-stage | 06-handover/ handover.md | handover-check |
| README | /write-readme | README.md | readme-writer |

---

## 🔒 리뷰 게이트 (3단계)
구현 후 `git commit`/`git push`는 **code-review·security-review가 모두 통과(passed)** 해야만 허용됩니다. 안 되어 있으면 훅이 차단합니다. 위험 명령(`rm -rf /` 등)도 차단됩니다.

## 🔄 월간 갱신
월 1회 `/refresh-skills` → 최신 트렌드 반영 + 버전 상승. 상세는 [MONTHLY-REFRESH.md](MONTHLY-REFRESH.md).

---

## 커맨드 요약
| 커맨드 | 언제 |
|---|---|
| `/init-project` | 신규 프로젝트 시작 |
| `/adopt-project` | 기존/진행 중 프로젝트에 도입 |
| `/next-stage` | 다음 단계로 (한 번에 한 단계) |
| `/write-readme` | 프로젝트 README 생성/갱신 |
| `/refresh-skills` | 월 1회 스킬셋 갱신 |

## 자주 묻는 질문
- **Q. 발동 안 돼요.** → 설치+재시작 확인(INSTALL.md). `/` 입력 시 커맨드가 보여야 함.
- **Q. 단계가 자동으로 넘어가요/안 넘어가요.** → 가이드 모드는 각 단계 끝에 **묻고** 이어갑니다. "멈춤"을 고르면 서고, `/next-stage`로 재개. "쭉 진행"이라고 하면 소프트 확인을 줄입니다.
- **Q. 3단계에서 막혀요.** → 리뷰 게이트입니다. code·security-review를 통과(passed)시켜야 진행·커밋됩니다.
- **Q. 기존 CLAUDE.md가 안 바뀌어요.** → adopt는 기존을 보존하고 `CLAUDE.generated.md`를 만듭니다. 병합하세요.
