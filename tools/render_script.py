"""에피소드 원고(.md)를 1회차 샘플과 같은 서식의 한글(.hwp) 파일로 만듭니다.

사용법:
    python tools/render_script.py radio_ai/episodes/ep02.md
    python tools/render_script.py radio_ai/episodes/ep02.md --contact 010-0000-0000 --out output/

원고 형식은 radio_ai/STYLE_GUIDE.md 의 "원고 소스 형식"을 따릅니다.
연락처는 공개 저장소에 올리지 않도록 --contact 또는 환경변수 RADIO_CONTACT 로 넣습니다.
"""
import argparse
import os
import re
import sys
import warnings
from pathlib import Path

from hwpx import HwpxDocument

warnings.filterwarnings("ignore")

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE = ROOT / "radio_ai" / "template" / "header_template.hwp"
CONTACT_PLACEHOLDER = "{{연락처}}"
PROGRAM_TITLE = "알아두면 쓸모있는 AI"

# 1회차 샘플(.hwp)에서 그대로 가져온 문단모양(para)·글자모양(char) id
PARA_BODY, PARA_OPENING, PARA_QUESTION, PARA_CLOSING = "0", "21", "23", "25"
CHAR_LABEL, CHAR_TAB, CHAR_HOST, CHAR_OPENING = "18", "14", "19", "15"
CHAR_GREETING, CHAR_BODY, CHAR_QUOTE = "16", "21", "20"

SECTION_RE = re.compile(r"^##\s*(오프닝|인사|질문(\d+)|답변(\d+)?|클로징|마무리|제작메모)\s*$")


def parse(path):
    """front matter(meta)와 [(섹션이름, 번호, 줄목록)] 을 돌려줍니다."""
    text = Path(path).read_text(encoding="utf-8")
    meta = {}
    if text.startswith("---"):
        head, text = text[3:].split("\n---", 1)
        for line in head.strip().splitlines():
            key, _, value = line.partition(":")
            meta[key.strip()] = value.strip().strip('"')
    sections, current = [], None
    for line in text.splitlines():
        m = SECTION_RE.match(line.strip())
        if m:
            name = re.sub(r"\d+", "", m.group(1))
            current = (name, m.group(2) or m.group(3), [])
            sections.append(current)
        elif current is not None:
            current[2].append(line.rstrip())
    # 섹션 앞뒤 빈 줄 정리
    cleaned = []
    for name, num, lines in sections:
        while lines and not lines[0].strip():
            lines.pop(0)
        while lines and not lines[-1].strip():
            lines.pop()
        cleaned.append((name, num, lines))
    return meta, cleaned


def _para(doc, para_id, runs):
    p = doc.add_paragraph("", para_pr_id_ref=para_id, char_pr_id_ref=runs[0][1],
                          include_run=False, inherit_style=False)
    for text, char_id in runs:
        p.add_run(text, char_pr_id_ref=char_id)
    return p


def _blank(doc, para_id=PARA_BODY, char_id=CHAR_BODY):
    _para(doc, para_id, [("", char_id)])


def render(md_path, out_dir, contact=""):
    meta, sections = parse(md_path)
    doc = HwpxDocument.open(TEMPLATE)
    for p in doc.paragraphs:
        for r in p.runs:
            if CONTACT_PLACEHOLDER in (r.text or ""):
                r.text = r.text.replace(CONTACT_PLACEHOLDER, contact)

    for name, num, lines in sections:
        if name == "오프닝":
            _blank(doc, PARA_OPENING, CHAR_TAB)
            for line in lines:
                _para(doc, PARA_OPENING, [("\t\t" + line, CHAR_OPENING)])
            _blank(doc, PARA_OPENING, CHAR_OPENING)
        elif name == "인사":
            for line in lines:
                _para(doc, PARA_BODY, [(line, CHAR_GREETING)])
            _blank(doc, PARA_BODY, "17")
        elif name == "질문":
            for i, line in enumerate(lines):
                if i == 0:
                    _para(doc, PARA_QUESTION, [(f"질문{num}", CHAR_LABEL), ("\t", CHAR_TAB),
                                               ("\t" + line, CHAR_HOST)])
                else:
                    _para(doc, PARA_QUESTION, [("\t\t" + line, CHAR_HOST)])
            _blank(doc, PARA_QUESTION, CHAR_QUOTE)
        elif name == "답변":
            for line in lines:
                if line.startswith(">"):
                    _para(doc, PARA_BODY, [(line.lstrip("> ").strip(), CHAR_QUOTE)])
                else:
                    _para(doc, PARA_BODY, [(line, CHAR_BODY)])
            _blank(doc)
        elif name == "클로징":
            for i, line in enumerate(lines):
                prefix = ">>>>>\t\t" if i == 0 else "\t\t"
                _para(doc, PARA_CLOSING, [(prefix + line, CHAR_HOST)])
            _blank(doc, PARA_CLOSING, CHAR_HOST)
        elif name == "마무리":
            for line in lines:
                _para(doc, PARA_BODY, [(line, CHAR_BODY)])
        # 제작메모는 방송 원고에 넣지 않습니다(작가·PD 전달용).

    # 한글 미리보기(PrvText)를 이번 원고 내용으로 교체 (템플릿 내용이 남지 않도록)
    preview = "\r\n".join(p.text or "" for p in doc.paragraphs)[:1024]
    doc.package.write("Preview/PrvText.txt", preview.encode("utf-8"))

    air = meta.get("air_date", "")
    stamp = air[2:].replace("-", "") if air else Path(md_path).stem
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{PROGRAM_TITLE}_{stamp}.hwp"
    doc.save_to_path(out_path)
    # 예비본: .hwp 가 열리지 않을 때를 대비한 한글 표준(OWPML) 형식
    doc.save_to_path(out_path.with_suffix(".hwpx"))
    return out_path


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("episodes", nargs="+", help="radio_ai/episodes/epNN.md")
    ap.add_argument("--out", default=str(ROOT / "output"))
    ap.add_argument("--contact", default=os.environ.get("RADIO_CONTACT", ""))
    args = ap.parse_args()
    for md in args.episodes:
        print(render(md, args.out, args.contact))


if __name__ == "__main__":
    sys.exit(main())
