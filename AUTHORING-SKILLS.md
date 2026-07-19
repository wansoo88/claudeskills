# 스킬 만드는 법 가이드 (직접 확장하기)

> 이 스킬셋에 새 스킬·커맨드·서브에이전트·훅을 추가하는 법. 팀이 스스로 확장·전파할 수 있도록. (근거: `background/research/claude-skills-트렌드-리서치-2026-07.md`, 검증 25/25)

---

## 1. 4개 부품 — 언제 무엇을 쓰나

| 부품 | 위치 | 쓸 때 |
|---|---|---|
| **Skill** | `skills/<name>/SKILL.md` | 절차·지식·산출물 생성법 ("이렇게 하라") |
| **Subagent** | `agents/<name>.md` | 격리된 전문 역할 ("~처럼 판단하라") |
| **Command** | `commands/<name>.md` | 사용자가 `/name`으로 부르는 진입점 |
| **Hook** | `hooks/hooks.json` + 스크립트 | 특정 시점 강제/자동화(차단·기록) |

> 원칙: 절차=스킬, 역할=서브에이전트, 진입=커맨드, 강제=훅, 외부연결=MCP.

---

## 2. SKILL.md 규칙 (검증된 스펙)

```markdown
---
name: my-skill              # 소문자·숫자·하이픈만, ≤64자, 'claude'/'anthropic' 금지
description: <무엇을 + 언제>  # ≤1024자. 이 문장이 "자동 발동"을 결정하므로 트리거를 명확히
---

# 제목
(본문: 실행 절차. 500줄 미만 권장)
```

- **필수는 name, description 둘뿐.** description에 "언제 쓰는지"를 꼭 넣는다(예: "…할 때 사용. /my-skill 실행 시 발동").
- **본문 500줄 미만.** 넘치면 아래로 분리:
  - `reference/*.md` — 긴 지식·체크리스트·템플릿 (읽을 때만 로드).
  - `scripts/*` — 결정적 작업(파일 생성 등). **스크립트는 결과만 컨텍스트에 올라가** 토큰 절약.
- 참조는 **한 단계 깊이**로(Claude가 파일 전체를 읽도록).

### 스크립트 vs 스킬 판단
- **결정적·반복적**(파일 골격 생성, 버전 bump, 다이어그램 XML) → **스크립트**.
- **맥락 판단이 필요**(README 작성, 코드리뷰, 설계) → **스킬로 Claude가 직접**. (예: readme-writer는 일부러 스크립트 없이 스킬로 둠)

---

## 3. 새 스킬 추가 5단계 (readme-writer를 예로)

1. **폴더 생성**: `skills/readme-writer/`
2. **SKILL.md 작성**: frontmatter(name/description) + 절차 본문. "언제 발동"을 description에 명시.
3. **긴 내용 분리**: 템플릿·원칙을 `reference/readme-template-ko.md`로.
4. **(선택) 커맨드**: `commands/write-readme.md` — 스킬을 `/write-readme`로 부르게.
5. **테스트 & 버전**: 스크립트가 있으면 직접 실행해 검증. `bump_version.py`로 버전 올림.

---

## 4. 서브에이전트 / 커맨드 / 훅 뼈대

**서브에이전트** (`agents/x.md`):
```markdown
---
name: my-role
description: <이 역할이 뭘 하고 언제 쓰나>
tools: Read, Write, Bash      # 최소 권한만
model: inherit
---
(시스템 프롬프트: 이 역할의 관점·원칙·산출물)
```

**커맨드** (`commands/x.md`): frontmatter `description` + 본문(무엇을 하라). `$ARGUMENTS`로 인자 전달.

**훅** (`hooks/hooks.json`): PreToolUse로 **차단**(exit 2), SubagentStop `matcher`로 **역할별 발동**. 스크립트는 stdin JSON을 읽어 판단.

---

## 5. 테스트 방법 (품질 유지)

- **스크립트**: 샘플 입력으로 **직접 실행**해 결과·exit code 확인 (예: `python scaffold_project.py --brief ...`).
- **훅**: stdin에 샘플 JSON을 파이프해 exit code 확인 (`echo '{...}' | python hook.py; echo $?`).
- **스킬 발동**: 설치 후 `/커맨드`가 뜨는지, 실제 실행 시 산출물이 나오는지 (INSTALL.md 확인법).
- ⚠️ 스크립트를 직접 돌린 것 ≠ 스킬이 Claude Code에서 발동된 것. 둘 다 확인.

---

## 6. 체크리스트 (새 스킬 추가 시)
- [ ] name: 소문자·하이픈·≤64자
- [ ] description: "무엇을 + 언제"(발동 트리거) 명시, ≤1024자
- [ ] 본문 500줄 미만, 긴 건 reference/로
- [ ] 결정적 작업은 scripts/로 분리하고 직접 테스트
- [ ] 서브에이전트는 최소 도구권한
- [ ] 필요하면 commands/에 진입점 추가
- [ ] `bump_version.py`로 버전 올림 + CHANGELOG 기록
- [ ] 스펙 확인은 agentskills.io (구 anthropics/skills 스펙은 stub)

---

## 7. 더 깊이
- 전체 설계 근거: `background/design/스킬셋-전체설계도.md`
- 최신 트렌드 리서치: `background/research/claude-skills-트렌드-리서치-2026-07.md`
- 설치·발동: `INSTALL.md` · 사용법: `USAGE.md`
