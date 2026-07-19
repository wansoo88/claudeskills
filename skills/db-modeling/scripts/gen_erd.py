#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gen_erd.py — 엔티티 스펙(entity-spec.json)으로부터 ERD 산출물을 생성.
  - docs/02-design/erd.md      : Mermaid erDiagram (Confluence/GitHub/마크다운에서 렌더)
  - docs/02-design/schema.dbml : dbml (dbdiagram.io에서 시각화)

사용:
    python gen_erd.py --spec docs/02-design/entity-spec.json [--out-dir docs/02-design] [--force]

entity-spec.json 예:
{
  "entities": [
    {"name":"user","columns":[{"name":"id","type":"bigint","key":"PK"},
                              {"name":"email","type":"varchar","note":"로그인"}]},
    {"name":"sale","columns":[{"name":"id","type":"bigint","key":"PK"},
                              {"name":"user_id","type":"bigint","key":"FK"},
                              {"name":"amount","type":"numeric"}]}
  ],
  "relations": [
    {"from":"user","to":"sale","type":"one-to-many","label":"places"}
  ]
}
"""
import argparse
import json
import sys
from pathlib import Path

MERMAID_CARD = {
    "one-to-one": "||--||",
    "one-to-many": "||--o{",
    "many-to-one": "}o--||",
    "many-to-many": "}o--o{",
}


def mermaid(spec):
    lines = ["erDiagram"]
    for rel in spec.get("relations", []):
        card = MERMAID_CARD.get(rel.get("type", "one-to-many"), "||--o{")
        a = rel["from"].upper()
        b = rel["to"].upper()
        label = rel.get("label", "rel").replace(" ", "_")
        lines.append(f"    {a} {card} {b} : {label}")
    for ent in spec.get("entities", []):
        lines.append(f"    {ent['name'].upper()} {{")
        for col in ent.get("columns", []):
            key = col.get("key", "")
            key_str = f" {key}" if key in ("PK", "FK") else ""
            # Mermaid: type name [PK|FK]  (주석은 렌더 제약으로 생략)
            lines.append(f"        {col.get('type','string')} {col['name']}{key_str}")
        lines.append("    }")
    return "\n".join(lines)


def dbml(spec):
    out = []
    for ent in spec.get("entities", []):
        out.append(f"Table {ent['name']} {{")
        for col in ent.get("columns", []):
            attrs = []
            if col.get("key") == "PK":
                attrs.append("pk")
            note = col.get("note")
            if note:
                attrs.append(f"note: '{note}'")
            attr_str = f" [{', '.join(attrs)}]" if attrs else ""
            out.append(f"  {col['name']} {col.get('type','varchar')}{attr_str}")
        out.append("}")
        out.append("")
    for rel in spec.get("relations", []):
        out.append(_dbml_ref(spec, rel))
    return "\n".join(out)


def _dbml_ref(spec, rel):
    """관계 → dbml Ref. FK는 '다(many)' 쪽 테이블의 '{부모}_id' 규칙으로 해석하고 실제 존재를 검증."""
    frm, to = rel["from"], rel["to"]
    rtype = rel.get("type", "one-to-many")
    if rtype == "one-to-many":
        parent, child = frm, to
    elif rtype == "many-to-one":
        parent, child = to, frm
    elif rtype == "many-to-many":
        return (f"// {frm} <> {to} (다대다): 조인 테이블 필요 — "
                f"Table {frm}_{to} {{ {frm}_id, {to}_id }} 로 분해하세요.")
    else:  # one-to-one
        parent, child = frm, to
    pk = _find_pk(spec, parent) or (parent, "id")
    fk_col = f"{parent}_id"
    if _has_column(spec, child, fk_col):
        return f"Ref: {child}.{fk_col} > {parent}.{pk[1]}"
    # 관례상 FK 컬럼이 없으면 명시적 경고(주석)로 남긴다 — 잘못된 Ref를 만들지 않음.
    return (f"// Ref: {child}.{fk_col} > {parent}.{pk[1]}  "
            f"(주의: {child}에 FK 컬럼 '{fk_col}' 미정의 — entity-spec 보완 필요)")


def _find_pk(spec, ent_name):
    for e in spec.get("entities", []):
        if e["name"] == ent_name:
            for c in e.get("columns", []):
                if c.get("key") == "PK":
                    return (ent_name, c["name"])
    return None


def _has_column(spec, ent_name, col_name):
    for e in spec.get("entities", []):
        if e["name"] == ent_name:
            return any(c["name"] == col_name for c in e.get("columns", []))
    return False


def erd_md(spec):
    name = spec.get("project_name", "데이터 모델")
    return f"""# ERD — {name}

> db-modeling 스킬 산출물. Mermaid erDiagram (Confluence 코드매크로/ GitHub에서 렌더). dbml은 `schema.dbml` 참조(dbdiagram.io).

```mermaid
{mermaid(spec)}
```

## 엔티티 요약
| 엔티티 | 주요 컬럼 | PK/FK |
|---|---|---|
""" + "\n".join(
        f"| {e['name']} | {', '.join(c['name'] for c in e.get('columns', []))} | "
        f"{', '.join(c['name']+'('+c['key']+')' for c in e.get('columns', []) if c.get('key') in ('PK','FK'))} |"
        for e in spec.get("entities", [])
    ) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--spec", required=True)
    ap.add_argument("--out-dir", default="docs/02-design")
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

    spec_path = Path(args.spec)
    if not spec_path.exists():
        print(f"[오류] 스펙 없음: {spec_path}", file=sys.stderr)
        return 1
    spec = json.loads(spec_path.read_text(encoding="utf-8"))

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    targets = [(out_dir / "erd.md", erd_md(spec)), (out_dir / "schema.dbml", dbml(spec))]
    for path, content in targets:
        if path.exists() and not args.force:
            print(f"[건너뜀] 이미 존재: {path} (--force로 덮어쓰기)")
            continue
        path.write_text(content, encoding="utf-8")
        print(f"[생성] {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
