#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scan_secure_coding.py — 사내 시큐어코딩 가이드 v1.0(E.S11.G07) 위반 '후보'를 정적으로 사전 점검.

security-review 스킬 2단계에서 실행한다. 이 스크립트는 **게이트가 아니다.**
가이드 제19조 3항("도구 결과는 오탐 여부를 검토하되, 오탐 처리 시에도 판단 근거를 기록")에 따라
여기서 나온 항목은 전부 리뷰어가 확인하고 취약/오탐 중 하나로 **근거와 함께** 판정해야 한다.

사용:
    python scan_secure_coding.py                      # 현재 폴더 전체
    python scan_secure_coding.py --root src           # 특정 경로
    python scan_secure_coding.py --changed-only       # git 변경분만 (커밋 전 리뷰 기본)
    python scan_secure_coding.py --json               # 기계 판독용
    python scan_secure_coding.py --strict             # 후보가 있으면 exit 1 (CI용)

출력: 가이드 조항별로 file:line 과 매칭 내용. 조항 번호는 reference/secure-coding-guide-ko.md 와 동일.
"""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

SKIP_DIRS = {
    ".git", "node_modules", "__pycache__", ".venv", "venv", "env", "dist", "build",
    ".next", ".nuxt", "out", "target", "vendor", "site-packages", ".mypy_cache",
    ".pytest_cache", ".terraform", "coverage", ".idea", ".vscode", "migrations",
}
SKIP_SUFFIX = (".min.js", ".min.css", ".map", ".lock", ".svg", ".png", ".jpg", ".gif", ".pdf", ".ico")
PY = {".py"}
JS = {".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs", ".vue", ".svelte"}
WEB = JS | {".html", ".htm", ".hbs", ".ejs", ".jinja", ".jinja2", ".j2"}
ALL = PY | WEB | {".sql", ".yml", ".yaml", ".tf", ".sh", ".env", ".ini", ".cfg", ".toml", ".json"}

MAX_LINE = 500      # 압축/생성 코드 방어
MAX_FILES = 4000

# 비밀값 오탐 제외: 환경변수·시크릿매니저 참조, 자리표시자
SECRET_SAFE = re.compile(
    r"(?i)(os\.environ|os\.getenv|process\.env|getenv|secrets?manager|parameter_?store|vault|"
    r"\$\{|<[^>]{1,40}>|x{4,}|\*{3,}|placeholder|example|dummy|sample|changeme|your[_-]|test[_-]?only|"
    r"fake|redacted|None|null|\"\"|''|#\s)"
)
USER_INPUT = r"(?:request|req\.|params|query|body|args|form|input|payload|user_?input|searchParams)"

# (조항, 규칙ID, 설명, 확장자, 패턴, 같은 창(window)에 있으면 넘어갈 패턴, 등급힌트)
RULES = [
    # ── 제6조 SQL/NoSQL/ORM 주입 ─────────────────────────────
    ("제6조", "sql-concat", "SQL 문자열에 + 결합 — 파라미터 바인딩으로 전환", ALL,
     r"""(?i)["'][^"']*\b(select|insert\s+into|update|delete\s+from)\b[^"']*["']\s*\+""", None, "높음"),
    ("제6조", "sql-fstring", "SQL f-string/템플릿 보간 — 파라미터 바인딩으로 전환", ALL,
     r"""(?i)(f["']|`)[^"'`]*\b(select|insert\s+into|update|delete\s+from)\b[^"'`]*(\{|\$\{)""", None, "높음"),
    ("제6조", "sql-percent", "SQL % 포매팅 — execute(sql, params) 바인딩으로 전환", PY,
     r"""(?i)["'][^"']*\b(select|insert\s+into|update|delete\s+from)\b[^"']*["']\s*%\s*[(\w]""", None, "높음"),
    ("제6조", "sql-dynamic-ident", "동적 테이블/컬럼/정렬키 — 허용목록에서 선택했는지 확인", ALL,
     r"""(?i)\b(order\s+by|group\s+by|from|table)\b\s*["'`]?\s*(\{|\$\{|\+\s*\w)""", None, "보통"),

    # ── 제7조 명령어·코드 실행 ───────────────────────────────
    ("제7조", "shell-true", "subprocess shell=True — 배열 인자로 분리 (제17조 2항)", PY,
     r"""\bshell\s*=\s*True\b""", None, "긴급"),
    ("제7조", "os-system", "os.system / os.popen — 원칙적 금지", PY,
     r"""\bos\.(system|popen)\s*\(""", None, "긴급"),
    ("제7조", "py-eval-exec", "eval / exec 동적 실행 — 원칙적 금지", PY,
     r"""(?<![\w.])(eval|exec)\s*\(""", None, "긴급"),
    ("제7조", "js-eval", "eval / new Function — 금지 (제18조 1항)", JS,
     r"""(?<![\w.])eval\s*\(|\bnew\s+Function\s*\(""", None, "긴급"),
    ("제7조", "js-timer-string", "문자열 기반 setTimeout/setInterval — 금지 (제18조 1항)", JS,
     r"""\b(setTimeout|setInterval)\s*\(\s*["'`]""", None, "높음"),
    ("제7조", "node-shell", "child_process exec / shell 옵션 — spawn + 배열 인자로 (제18조 3항)", JS,
     r"""\b(child_process\.)?(exec|execSync)\s*\(|\bshell\s*:\s*true\b""", None, "긴급"),

    # ── 제8조 XSS ────────────────────────────────────────────
    ("제8조", "dom-html-sink", "innerHTML/outerHTML/insertAdjacentHTML — textContent 또는 정화 적용", WEB,
     r"""\.(innerHTML|outerHTML)\s*=|\binsertAdjacentHTML\s*\(""", None, "높음"),
    ("제8조", "react-dangerous", "dangerouslySetInnerHTML — 정화 정책 확인", JS,
     r"""dangerouslySetInnerHTML""", None, "높음"),
    ("제8조", "template-raw", "템플릿 자동 이스케이프 해제(raw/safe/v-html/삼중괄호)", WEB,
     r"""\bv-html\b|\|\s*safe\b|\{\{\{|\{%\s*autoescape\s+(off|false)""", None, "높음"),
    ("제8조", "url-scheme", "javascript: 스킴 — URL 스킴 허용목록 검증 필요", WEB,
     r"""(?i)["'`]\s*javascript:""", None, "보통"),

    # ── 제9조 경로 조작·파일 처리 ────────────────────────────
    ("제9조", "zip-slip", "압축 해제(extractall/zip slip) — 경로 정규화 후 하위경로 확인", ALL,
     r"""\.extractall\s*\(|\bzipfile\.ZipFile\s*\(""", None, "높음"),
    ("제9조", "path-from-input", "사용자 입력으로 경로 구성 — 기준 디렉터리 정규화·하위경로 검증", ALL,
     rf"""(?i)\b(os\.path\.join|Path|open|readFile|createReadStream|path\.join)\s*\([^)]*{USER_INPUT}""", None, "높음"),
    ("제9조", "file-serve", "파일 전송 API — 경로 조작 방지 + 객체별 권한 검증 확인", ALL,
     r"""\b(send_file|send_from_directory|sendFile|res\.download|FileResponse)\s*\(""", None, "보통"),

    # ── 제11조 세션·토큰 ─────────────────────────────────────
    ("제11조", "cookie-flags", "쿠키에 Secure/HttpOnly/SameSite 미확인", ALL,
     r"""\b(set_cookie|res\.cookie|cookies\.set|Set-Cookie)\b""",
     r"""(?i)httponly""", "높음"),
    ("제11조", "jwt-verify-off", "토큰 서명 검증 비활성화 또는 alg=none", ALL,
     r"""(?i)verify_signature\s*[:=]\s*False|algorithms?\s*[:=]\s*\[?\s*["']none["']|"""
     r"""\b(jwt|token)\w*\s*[^=\n]{0,40}\bverify\s*[:=]\s*False\b""",
     None, "긴급"),
    ("제11조", "jwt-claims", "JWT 디코드 — audience/issuer/만료 검증 여부 확인", ALL,
     r"""\bjwt\.decode\s*\(|jsonwebtoken\.verify\s*\(|\bjwtDecode\s*\(""",
     r"""(?i)(audience|issuer|aud|iss)""", "보통"),

    # ── 제12조 암호화·중요정보 ───────────────────────────────
    ("제12조", "tls-verify-off", "TLS 인증서 검증 비활성화 — 금지", ALL,
     r"""(?i)\bverify\s*=\s*False\b|rejectUnauthorized\s*:\s*false|NODE_TLS_REJECT_UNAUTHORIZED|"""
     r"""ssl\._create_unverified_context|CERT_NONE|--insecure\b|curl\s+-k\b""", None, "긴급"),
    ("제12조", "weak-hash", "취약 해시(MD5/SHA1) — 비밀번호는 Argon2/bcrypt/PBKDF2 + 고유 Salt≥16B", ALL,
     r"""(?i)\bhashlib\.(md5|sha1)\s*\(|createHash\s*\(\s*["'](md5|sha1)["']|\bmd5\s*\(""", None, "높음"),
    ("제12조", "weak-cipher", "취약 암호 알고리즘/모드(DES/RC4/ECB)", ALL,
     r"""(?i)\b(DES3?|RC4|ARC4)\b|MODE_ECB|["']aes-\d+-ecb["']""", None, "높음"),
    ("제12조", "pw-reversible", "비밀번호를 가역 암호화/평문 저장한 정황 — 단방향 해시만 허용", ALL,
     r"""(?i)(encrypt|decrypt|b64encode|base64)\s*\([^)]*\bpass(word|wd)?\b|"""
     r"""\bpass(word|wd)?\b[^=\n]{0,20}=\s*(encrypt|decrypt|base64)""", None, "긴급"),
    ("제12조", "secret-literal", "비밀값 하드코딩 의심 — 비밀관리 체계/환경설정으로 이관", ALL,
     r"""(?i)\b(password|passwd|pwd|secret|api[_-]?key|apikey|access[_-]?token|refresh[_-]?token|"""
     r"""private[_-]?key|client[_-]?secret|auth[_-]?token)\b\s*[:=]\s*["'][^"'\s]{6,}["']""",
     None, "긴급"),
    ("제12조", "secret-pattern", "자격증명 형태의 문자열(AWS 키/개인키/JWT)", ALL,
     r"""AKIA[0-9A-Z]{16}|-----BEGIN [A-Z ]*PRIVATE KEY-----|\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.""",
     None, "긴급"),

    # ── 제13조 오류 처리·로그 ────────────────────────────────
    ("제13조", "stacktrace-exposed", "스택트레이스/내부정보가 응답에 실릴 수 있음", ALL,
     r"""(?i)traceback\.format_exc|printStackTrace|\berr(or)?\.stack\b|app\.run\([^)]*debug\s*=\s*True|"""
     r"""\bDEBUG\s*=\s*True\b""", None, "높음"),
    ("제13조", "log-injection", "외부 입력을 로그에 그대로 기록 — 개행·제어문자 제거·인코딩 필요", ALL,
     rf"""(?i)\b(logger|logging|log|console)\.(info|debug|warn|warning|error|critical|log|exception)\s*\([^)]*{USER_INPUT}""",
     r"""(?i)(sanitiz|escape|replace\s*\(|strip\s*\(|encode\s*\()""", "보통"),
    ("제13조", "log-sensitive", "민감정보를 로그에 기록 — 마스킹 또는 기록 제외", ALL,
     r"""(?i)\b(logger|logging|log|console)\.\w+\s*\([^)]*\b(password|passwd|token|secret|api[_-]?key|"""
     r"""ssn|jumin|resident|passport|card[_-]?(no|num|number)|account[_-]?(no|num|number))\b""",
     r"""(?i)(mask|redact|\*{3,})""", "높음"),

    # ── 제14조 역직렬화·파서 ─────────────────────────────────
    ("제14조", "unsafe-deser", "위험한 역직렬화(pickle/marshal/joblib) — 신뢰불가 데이터 금지 (제17조 1항)", PY,
     r"""\b(pickle|cPickle|marshal|dill|joblib)\.(load|loads)\s*\(""", None, "긴급"),
    ("제14조", "yaml-unsafe", "yaml.load — safe_load 사용 + 스키마 검증", PY,
     r"""\byaml\.(load|unsafe_load|full_load)\s*\(""", r"""SafeLoader|safe_load""", "높음"),
    ("제14조", "xxe", "XML 파서 — 외부 엔터티/DTD 처리 비활성화 확인", ALL,
     r"""\b(etree|ElementTree|minidom|xmlrpc|libxmljs|DOMParser)\b.*\b(fromstring|parse|parseFromString)\s*\(|"""
     r"""\bresolve_entities\s*=\s*True""", r"""defusedxml""", "높음"),
    ("제14조", "js-deser", "JS 객체 자동 복원 계열 — 신뢰불가 데이터 금지", JS,
     r"""\bnode-serialize\b|\bunserialize\s*\(|\bdeserialize\s*\(""", None, "높음"),

    # ── 제15조 외부연동·SSRF ─────────────────────────────────
    ("제15조", "ssrf-dynamic-url", "동적 URL 외부 호출 — 허용목록·사설망 차단 확인", ALL,
     r"""\b(requests|httpx)\.(get|post|put|patch|delete|head|request)\s*\(\s*(?!["'])|"""
     r"""\b(axios|fetch)\s*\(\s*(?!["'`])""", None, "높음"),
    ("제15조", "open-redirect", "동적 리다이렉트 — 목적지 허용목록 확인", ALL,
     r"""\b(redirect|res\.redirect|RedirectResponse)\s*\(\s*(?!["'])""", None, "보통"),
    ("제15조", "metadata-endpoint", "클라우드 메타데이터 주소 — 차단 대상인지 확인", ALL,
     r"""169\.254\.169\.254|metadata\.google\.internal""", None, "높음"),

    # ── 제16조 · 제17조 3항 자원/타임아웃 ────────────────────
    ("제16조", "no-timeout", "HTTP 호출에 timeout 미지정 — connect/read timeout 필요", PY,
     r"""\b(requests|httpx)\.(get|post|put|patch|delete|head|request)\s*\(""", r"""timeout\s*=""", "보통"),
    ("제16조", "unbounded-read", "무제한 읽기/조회 — 크기·페이징 상한 확인", ALL,
     r"""\.read\s*\(\s*\)|\bfetchall\s*\(\s*\)|\.json\s*\(\s*\)\s*$""", None, "낮음"),

    # ── 제18조 4항 프로토타입 오염 ───────────────────────────
    ("제18조", "proto-pollution", "객체 병합/복사 — __proto__·constructor·prototype 차단 + 스키마 검증", JS,
     rf"""\b(_\.(merge|mergeWith|defaultsDeep|set)|deepmerge|extend)\s*\(|"""
     rf"""\bObject\.assign\s*\(\s*\w+\s*,\s*{USER_INPUT}""", r"""__proto__""", "높음"),

    # ── 제10조 인가 (정황) ───────────────────────────────────
    ("제10조", "client-role-trust", "클라이언트가 보낸 역할/사용자 ID를 권한 판단에 사용한 정황", ALL,
     rf"""(?i){USER_INPUT}\s*[\[.]\s*["']?(role|is_?admin|user_?id|permission|grade|auth)""", None, "긴급"),
]

COMPILED = [(art, rid, desc, exts, re.compile(pat), re.compile(unless) if unless else None, sev)
            for art, rid, desc, exts, pat, unless, sev in RULES]

SEV_ORDER = {"긴급": 0, "높음": 1, "보통": 2, "낮음": 3}


def iter_files(root: Path, only: list[Path] | None):
    if only is not None:
        for p in only:
            if p.is_file() and p.suffix.lower() in ALL and not p.name.endswith(SKIP_SUFFIX):
                yield p
        return
    count = 0
    for p in root.rglob("*"):
        if count >= MAX_FILES:
            break
        if not p.is_file():
            continue
        if any(part in SKIP_DIRS for part in p.parts):
            continue
        if p.suffix.lower() not in ALL or p.name.endswith(SKIP_SUFFIX):
            continue
        count += 1
        yield p


def changed_files(root: Path) -> list[Path]:
    """git 변경분(스테이지 + 워킹트리 + HEAD 미추적)."""
    out: set[str] = set()
    for cmd in (["git", "diff", "--name-only", "HEAD"],
                ["git", "diff", "--name-only", "--cached"],
                ["git", "ls-files", "--others", "--exclude-standard"]):
        try:
            r = subprocess.run(cmd, cwd=root, capture_output=True, text=True, timeout=20)
            if r.returncode == 0:
                out.update(x.strip() for x in r.stdout.splitlines() if x.strip())
        except (OSError, subprocess.SubprocessError):
            pass
    return [root / x for x in sorted(out)]


def logical_window(lines: list[str], i: int, max_extra: int = 4) -> str:
    """호출이 여러 줄에 걸칠 때만 다음 줄을 포함한다(괄호가 닫힐 때까지).

    단순히 i..i+3 을 보면 무관한 다음 줄 때문에 탐지가 죽는다.
    (예: `yaml.load(x)` 바로 아래 줄의 `yaml.safe_load(y)` 가 unless 에 걸려 누락)
    """
    buf = [lines[i]]
    depth = lines[i].count("(") - lines[i].count(")")
    j = i + 1
    while depth > 0 and j < len(lines) and (j - i) <= max_extra:
        buf.append(lines[j])
        depth += lines[j].count("(") - lines[j].count(")")
        j += 1
    return "\n".join(buf)


def scan_file(path: Path, root: Path) -> list[dict]:
    if path.name == Path(__file__).name:
        return []  # 규칙 문자열이 자기 자신에 매칭되는 노이즈 제거
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return []
    ext = path.suffix.lower()
    hits = []
    for i, line in enumerate(lines):
        if len(line) > MAX_LINE:
            continue
        stripped = line.strip()
        if stripped.startswith(("#", "//", "*", "<!--")):
            continue  # 주석은 예시일 가능성이 커서 제외 (놓치면 리뷰어가 본문에서 확인)
        window = logical_window(lines, i)
        for art, rid, desc, exts, pat, unless, sev in COMPILED:
            if ext not in exts:
                continue
            if not pat.search(line):
                continue
            if unless and unless.search(window):
                continue
            if rid.startswith("secret") and SECRET_SAFE.search(line):
                continue
            hits.append({
                "article": art, "rule": rid, "severity": sev, "desc": desc,
                "file": str(path.relative_to(root)).replace("\\", "/"),
                "line": i + 1, "code": stripped[:160],
            })
    return hits


def repo_checks(root: Path) -> list[dict]:
    """파일 단위로는 안 보이는 저장소 수준 점검 (제6장 · 제17조 5항 · 제18조 5항)."""
    out = []

    def add(art, rule, sev, desc, file="."):
        out.append({"article": art, "rule": rule, "severity": sev, "desc": desc,
                    "file": file, "line": 0, "code": ""})

    if (root / "package.json").exists() and not any(
            (root / f).exists() for f in ("package-lock.json", "pnpm-lock.yaml", "yarn.lock")):
        add("제6장", "no-lockfile", "높음", "package.json은 있으나 lock 파일이 없음 — 잠금 파일 관리 필요 (제18조 5항)",
            "package.json")

    req = root / "requirements.txt"
    if req.exists():
        try:
            unpinned = [l.strip() for l in req.read_text(encoding="utf-8", errors="replace").splitlines()
                        if l.strip() and not l.strip().startswith("#") and "==" not in l and not l.strip().startswith("-")]
        except OSError:
            unpinned = []
        if unpinned:
            add("제17조", "unpinned-deps", "보통",
                f"고정되지 않은 의존성 {len(unpinned)}건: {', '.join(unpinned[:5])} — 고정 버전 사용 (제17조 5항)",
                "requirements.txt")

    try:
        r = subprocess.run(["git", "ls-files"], cwd=root, capture_output=True, text=True, timeout=20)
        tracked = r.stdout.splitlines() if r.returncode == 0 else []
    except (OSError, subprocess.SubprocessError):
        tracked = []
    for f in tracked:
        name = Path(f).name
        if name == ".env" or name.startswith(".env.") and not name.endswith((".example", ".sample", ".template")):
            add("제12조", "env-tracked", "긴급", f"{f} 가 git에 추적되고 있음 — 비밀값 노출 위험", f)
    return out


def main():
    ap = argparse.ArgumentParser(description="사내 시큐어코딩 가이드 v1.0 위반 후보 사전 점검")
    ap.add_argument("--root", default=".", help="점검 루트 (기본: 현재 폴더)")
    ap.add_argument("--changed-only", action="store_true", help="git 변경분만 점검")
    ap.add_argument("--json", action="store_true", help="JSON 출력")
    ap.add_argument("--strict", action="store_true", help="후보가 하나라도 있으면 exit 1")
    args = ap.parse_args()

    if hasattr(sys.stdout, "reconfigure"):   # Windows cp949 콘솔 대응
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")

    root = Path(args.root).resolve()
    if not root.exists():
        sys.stderr.write(f"[오류] 경로 없음: {root}\n")
        return 2

    targets = changed_files(root) if args.changed_only else None
    findings = []
    for f in iter_files(root, targets):
        findings.extend(scan_file(f, root))
    findings.extend(repo_checks(root))
    findings.sort(key=lambda h: (SEV_ORDER.get(h["severity"], 9), h["article"], h["file"], h["line"]))

    if args.json:
        print(json.dumps({"root": str(root), "count": len(findings), "findings": findings},
                         ensure_ascii=False, indent=2))
        return 1 if (args.strict and findings) else 0

    scope = "git 변경분" if args.changed_only else str(root)
    print(f"# 시큐어코딩 사전 점검 — {scope}")
    print(f"기준: 사내 시큐어코딩 가이드 v1.0 (E.S11.G07)  |  후보 {len(findings)}건\n")
    if not findings:
        print("탐지된 패턴 없음. **그래도 도구가 못 잡는 항목(인가 누락·업로드 검증·증적)은 수동 점검한다.**")
        return 0

    by_sev = {}
    for h in findings:
        by_sev.setdefault(h["severity"], []).append(h)
    print("| 등급 | 건수 |")
    print("|---|---|")
    for sev in ("긴급", "높음", "보통", "낮음"):
        if sev in by_sev:
            print(f"| {sev} | {len(by_sev[sev])} |")
    print()

    cur = None
    for h in findings:
        key = (h["article"], h["rule"])
        if key != cur:
            cur = key
            print(f"\n## [{h['severity']}] {h['article']} · {h['rule']}\n{h['desc']}")
        print(f"  - {h['file']}:{h['line']}  `{h['code']}`")

    print("\n---")
    print("이 결과는 **후보**다. 가이드 제19조 3항에 따라 각 항목을 취약/오탐으로 판정하고,")
    print("**오탐이어도 판단 근거를 `docs/03-build/security-review-log.md`에 남긴다.**")
    return 1 if (args.strict and findings) else 0


if __name__ == "__main__":
    raise SystemExit(main())
