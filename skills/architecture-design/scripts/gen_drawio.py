#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gen_drawio.py — project-brief.json 으로부터 AWS 3-tier 아키텍처 draw.io(.drawio) 파일을 생성.

사용:
    python gen_drawio.py --brief docs/01-interview/project-brief.json --out docs/02-design/architecture.drawio [--force]

결과: app.diagrams.net(draw.io) 및 Confluence draw.io 앱에서 열어 편집 가능한 mxGraphModel XML.
구조: Users → CloudFront/Route53 → ALB(퍼블릭 서브넷) → Web(React) → App(Docker) → DB(RDS) + CloudWatch.
"""
import argparse
import json
import sys
from pathlib import Path
from xml.sax.saxutils import escape

LABELS = {
    "frontend": {"react": "React SPA\n(CloudFront + S3)", "admin-only": "관리자 웹\n(React)",
                 "none": "(프론트 없음)", "undecided": "웹 프론트\n(React 가정)"},
    "backend": {"python-fastapi": "FastAPI\n(Docker / ECS Fargate)",
                "nodejs": "Node.js\n(Docker / ECS Fargate)",
                "java-spring": "Spring\n(Docker / ECS Fargate)",
                "undecided": "백엔드 API\n(Docker 가정)"},
    "database": {"postgresql": "RDS for PostgreSQL\n(Multi-AZ)", "mysql": "RDS for MySQL\n(Multi-AZ)",
                 "aurora": "Aurora\n(Multi-AZ)", "existing": "기존 사내 DB",
                 "undecided": "RDS\n(PostgreSQL 가정)"},
}


def lbl(brief, key):
    v = brief.get(key, "undecided")
    return LABELS.get(key, {}).get(v, str(v))


def box(cid, value, x, y, w, h, fill, stroke, parent="1", dashed=False):
    style = (f"rounded=1;whiteSpace=wrap;html=1;fillColor={fill};strokeColor={stroke};"
             f"fontColor=#232F3E;fontSize=12;verticalAlign=middle;"
             + ("dashed=1;" if dashed else ""))
    return (f'<mxCell id="{cid}" value="{escape(value)}" style="{style}" vertex="1" parent="{parent}">'
            f'<mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry"/></mxCell>')


def container(cid, value, x, y, w, h, fill, stroke, parent="1"):
    style = (f"rounded=0;whiteSpace=wrap;html=1;fillColor={fill};strokeColor={stroke};"
             f"verticalAlign=top;fontColor={stroke};fontSize=12;fontStyle=1;dashed=1;")
    return (f'<mxCell id="{cid}" value="{escape(value)}" style="{style}" vertex="1" parent="{parent}">'
            f'<mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry"/></mxCell>')


def edge(cid, source, target, label=""):
    style = "edgeStyle=orthogonalEdgeStyle;rounded=1;html=1;endArrow=block;strokeColor=#545B64;"
    return (f'<mxCell id="{cid}" value="{escape(label)}" style="{style}" edge="1" parent="1" '
            f'source="{source}" target="{target}"><mxGeometry relative="1" as="geometry"/></mxCell>')


def build_xml(brief):
    name = brief.get("project_name", "Data Product")
    cells = []
    # 색상(AWS 팔레트 근사)
    ORANGE, BLUE, GREEN, GREY = "#FF9900", "#1BA1E2", "#7AA116", "#F2F3F3"
    STROKE_O, STROKE_B, STROKE_G, STROKE_VPC = "#D68A00", "#0F6FA8", "#5B7A0F", "#232F3E"

    # 외부
    cells.append(box("users", "사용자\n(Users)", 340, 20, 160, 40, "#E8EAED", "#545B64"))
    cells.append(box("edge_cf", "Route 53 + CloudFront\n(CDN/DNS)", 320, 90, 200, 50, ORANGE, STROKE_O))

    # VPC 컨테이너
    cells.append(container("vpc", "AWS VPC", 80, 170, 680, 470, "#FBFBFB", STROKE_VPC))
    # 퍼블릭 서브넷
    cells.append(container("pub", "퍼블릭 서브넷 (Public)", 100, 210, 640, 110, "#EAF6FF", STROKE_B, parent="vpc"))
    cells.append(box("alb", "Application\nLoad Balancer", 320, 245, 200, 50, BLUE, STROKE_B, parent="pub"))

    # 프라이빗 서브넷 - 웹/앱
    cells.append(container("priv_app", "프라이빗 서브넷 (App Tier)", 100, 340, 640, 120, "#F1F8E9", STROKE_G, parent="vpc"))
    cells.append(box("web", lbl(brief, "frontend"), 150, 375, 200, 60, GREEN, STROKE_G, parent="priv_app"))
    cells.append(box("app", lbl(brief, "backend"), 470, 375, 200, 60, GREEN, STROKE_G, parent="priv_app"))

    # 프라이빗 서브넷 - 데이터
    cells.append(container("priv_db", "프라이빗 서브넷 (Data Tier)", 100, 480, 640, 120, "#FFF3E0", STROKE_O, parent="vpc"))
    cells.append(box("db", lbl(brief, "database"), 320, 515, 200, 60, ORANGE, STROKE_O, parent="priv_db"))

    # 관측/보안 (사이드)
    cells.append(box("cw", "CloudWatch\n(모니터링/로그)", 800, 245, 160, 50, "#E8EAED", "#545B64"))
    cells.append(box("sm", "Secrets Manager\n(비밀정보)", 800, 340, 160, 50, "#E8EAED", "#545B64"))

    # 엣지
    cells.append(edge("e1", "users", "edge_cf"))
    cells.append(edge("e2", "edge_cf", "alb", "HTTPS"))
    cells.append(edge("e3", "alb", "web"))
    cells.append(edge("e4", "web", "app", "REST API"))
    cells.append(edge("e5", "app", "db", "SQL"))
    cells.append(edge("e6", "app", "cw", "logs/metrics"))
    cells.append(edge("e7", "app", "sm", "secrets"))

    body = "\n        ".join(cells)
    return f"""<mxfile host="data-product-studio" version="1.0">
  <diagram name="{escape(name)} - AWS 3-tier" id="arch-1">
    <mxGraphModel dx="1024" dy="768" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="1100" pageHeight="850" math="0" shadow="0">
      <root>
        <mxCell id="0"/>
        <mxCell id="1" parent="0"/>
        {body}
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--brief", required=True)
    ap.add_argument("--out", default="docs/02-design/architecture.drawio")
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

    brief_path = Path(args.brief)
    if not brief_path.exists():
        print(f"[오류] 브리프 없음: {brief_path}", file=sys.stderr)
        return 1
    brief = json.loads(brief_path.read_text(encoding="utf-8"))

    out = Path(args.out)
    if out.exists() and not args.force:
        print(f"[건너뜀] 이미 존재: {out} (덮어쓰려면 --force)")
        return 0
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(build_xml(brief), encoding="utf-8")
    print(f"[생성] AWS 3-tier 아키텍처: {out}")
    print("draw.io(app.diagrams.net) 또는 Confluence draw.io 앱에서 열어 편집하세요.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
