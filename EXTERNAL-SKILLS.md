# 외부 추천 스킬 (함께 쓰는 서드파티 스킬)

> 이 스킬셋과 **같이 전역(user scope)으로 설치해 쓰는** 외부 스킬 목록과 공존 규칙.
> 출처: Jay Choi 「클로드 코드 800시간 쓰고 남은 스킬 6개」(YouTube, 2026-05-30) 추천 6종 + `impeccable`.
> 코드는 이 저장소에 **복사(vendoring)하지 않는다.** 각 원 저장소 마켓플레이스에서 설치 → 갱신은 `claude plugin update`.

## 목록

| 스킬 | 설치 id | 무엇을 | 언제 | hook | 외부 전송 |
|---|---|---|---|---|---|
| **karpathy-guidelines** | `andrej-karpathy-skills@karpathy-skills` | 가정 명시·단순함 우선·외과적 수정·검증 기준 4원칙 | 코드 작성·리뷰·리팩터 | 없음 | 없음 |
| **watch** (claude-video) | `watch@claude-video` | 영상 URL/파일 → 프레임+자막 추출 → Claude가 "시청" (`/watch <url> 질문`) | 영상 요약, 버그 재현 영상 분석 | SessionStart(상태 1줄) | 자막 없을 때만 오디오를 Whisper API(Groq/OpenAI)로 — **키를 넣었을 때만** |
| **superpowers** | `superpowers@claude-plugins-official` | 브레인스토밍→계획→TDD→서브에이전트 실행→2중 리뷰 프로세스 강제 | 기능 구현, 디버깅 | SessionStart(`using-superpowers` 주입) | 없음 |
| **understand-anything** | `understand-anything@understand-anything` | 멀티에이전트로 코드·문서 지식그래프 + 대시보드 (`/understand`, `/understand-dashboard`) | 낯선 코드베이스 온보딩, 변경 영향도 | PostToolUse(Bash)·SessionStart — `autoUpdate` 켠 repo에서만 동작 | 없음 (그래프는 프로젝트 `.understand-anything/`) |
| **agentmemory** | `agentmemory@agentmemory` | 세션 작업을 자동 기록·압축 → 다음 세션에 필요한 맥락만 주입 (BM25/벡터/그래프 검색, 뷰어 :3113) | 상시 | 12개(전 세션 캡처) + MCP 서버 | keyless 기본 = **로컬만**. LLM 공급자를 설정하면 관측 내용이 그 공급자로 감 |
| **skill-creator** | Anthropic 공식 (`anthropic-skills:skill-creator` 또는 `skill-creator@claude-plugins-official`) | 스킬 생성·테스트·패키징 | 반복 프롬프트를 스킬로 굳힐 때 | 없음 | 없음 |
| **impeccable** | `impeccable@impeccable` | 프론트 디자인 가이드 1스킬·24커맨드 + 결정적 탐지 규칙 61개 (`/impeccable audit` 등) | UI 작성·점검 | PostToolUse(Edit\|Write)·Stop 디자인 검사 | 없음 (엔진 바이너리 최초 1회 다운로드 → `~/.impeccable/bin`) |

**제외**: Remotion(영상의 보너스) — Remotion 사용자 전용이고 스킬 12개가 모든 세션 목록에 올라간다. 필요하면 `npx skills add remotion-dev/skills`.

## 설치

```powershell
# 저장소 루트에서 (멱등 — 이미 설치된 것은 건너뜀)
powershell -ExecutionPolicy Bypass -File .\tools\install_external_skills.ps1
# 실행 없이 명령만 보기: -DryRun   /  agentmemory 제외: -SkipAgentMemory   /  winget 의존성 생략: -SkipDeps
```

수동으로 하려면 Claude Code 안에서 `/plugin marketplace add <owner/repo>` → `/plugin install <설치 id>`.
설치 후 **Claude Code 재시작**(또는 `/reload-plugins`).

### Windows 추가 준비
- **watch**: `winget install Gyan.FFmpeg`, `winget install yt-dlp.yt-dlp` 후 **새 터미널**(PATH 반영).
  - 스크립트는 `python3` 대신 `python`으로 실행(`python3`는 MS Store 스텁).
  - cp949 콘솔에서 `setup.py` 출력이 `UnicodeEncodeError`로 끊기면 `PYTHONIOENCODING=utf-8`.
  - YouTube 자막이 `HTTP 429`로 실패하면 잠시 뒤 재시도하거나 `yt-dlp --skip-download --write-auto-subs --sub-langs ko-orig <url>`로 직접 받는다.
- **agentmemory**: 엔진 `iii` **v0.11.2**를 수동 설치해야 한다.
  1. [iii v0.11.2 릴리스](https://github.com/iii-hq/iii/releases/tag/iii%2Fv0.11.2)에서 `iii-x86_64-pc-windows-msvc.zip` → `iii.exe`를 `%USERPROFILE%\.agentmemory\bin\`에
  2. 별도 터미널에서 `npx -y @agentmemory/agentmemory@latest` (첫 실행은 대화형 — LLM 공급자는 **keyless** 선택)
  3. 확인: `curl http://localhost:3111/agentmemory/health`, 뷰어 http://localhost:3113
  - 서버가 꺼져 있으면 hook은 즉시 실패하고 넘어간다(작업은 막히지 않지만 기록도 안 됨).
- **impeccable**: 프로젝트마다 `/impeccable init` 1회(`PRODUCT.md` 생성).

## 공존 규칙 (충돌 시 우선순위)

1. **사람의 지시·CLAUDE.md > 이 스킬셋 규약 > 외부 스킬.** superpowers도 "CLAUDE.md가 스킬보다 우선"을 명시한다.
2. **프로세스** — 이 스킬셋이 관리하는 프로젝트(`docs/` 6단계)에서는 `orchestrator`·6단계·리뷰 게이트가 기준이다.
   superpowers는 단계 **안의 기법**으로 쓴다: 3단계 구현의 `test-driven-development`·`systematic-debugging`·`verification-before-completion`.
   - 1단계 요구사항은 `superpowers:brainstorming` 대신 `project-interview`.
   - superpowers의 코드리뷰 스킬은 `code-review`·`security-review` 게이트를 **대체하지 않는다**(원장에 기록되지 않음).
3. **UI** — `serveone-bi-ui` > `impeccable` > `dataviz`. impeccable은 audit·critique·harden·clarify 같은 품질 점검에 쓰고,
   컬러·폰트(Pretendard)·밀도는 `serveone-bi-ui`를 따른다. 탐지 결과가 사내 규약과 부딪히면 사내 규약을 유지한다.
4. **메모리** — 내장 auto memory와 agentmemory를 같이 쓴다. 확정된 규칙·결정은 CLAUDE.md/memory 파일에 두고, agentmemory는 작업 이력 검색용이다.
5. **보안** — 사내 코드·데이터를 외부 LLM/API로 보내지 않는다. agentmemory는 keyless(또는 `EMBEDDING_PROVIDER=local`)로만,
   watch는 사내·기밀 영상이면 `--no-whisper`. 외부 공급자 연결은 팀장 승인 후.
6. **karpathy-guidelines**는 이 스킬셋 작성 규칙과 충돌하지 않는다. 항상 켜 둔다.

## 갱신·제거
- 갱신: `claude plugin update <설치 id>` (마켓플레이스 `claude plugin marketplace update`).
- 제거: `claude plugin uninstall <설치 id>`.
- 월간 갱신(`/refresh-skills`) 때 외부 스킬의 **버전·hook 변경**도 같이 확인한다 — hook이 늘면 모든 세션에 영향.
