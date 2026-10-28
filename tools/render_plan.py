"""curriculum.yaml 로 6개월 전체 방송 계획서(.hwp/.hwpx)를 만듭니다.

사용법:
    python tools/render_plan.py            # → output/알아두면 쓸모있는 AI_전체계획서.hwp
    python tools/render_plan.py --out 폴더

커리큘럼이 바뀌면 다시 돌리면 됩니다(완료 회차는 ✔ 표시).
"""
import argparse
import sys
import warnings
from pathlib import Path

import yaml
from hwpx import HwpxDocument

warnings.filterwarnings("ignore")

ROOT = Path(__file__).resolve().parent.parent
CURRICULUM = ROOT / "radio_ai" / "curriculum.yaml"

PARTS = [
    (1, 4, "1부. 왕초보 입문", "설치하고, 말 걸고, 사진 보여주기까지. AI와 친해지는 4주"),
    (5, 15, "2부. 겨울 생활 꿀팁", "김장·연말·새해·설 명절 일정에 맞춘 생활 문제 해결"),
    (16, 21, "3부. 일·외주·인생 2막", "견적·업체 의뢰·이력서·회의록·가게 홍보"),
    (22, 26, "4부. 봄, 나와 가족을 위한 AI", "나들이·텃밭·부모님 돌봄·사기 예방·총정리"),
]

OVERVIEW = [
    ("프로그램", "<알아두면 쓸모있는 AI> - 신중년 AI 실용교육 코너"),
    ("출연", "진행자(DJ) + 민지희 강사(AI인문학 강사)"),
    ("대상", "50대 이상 신중년 왕초보 청취자 (휴대폰 중심, 글자 입력·앱 설치가 낯선 분)"),
    ("방송", "매주 금요일 30분, 1회 1꿀팁"),
    ("기간", "2026년 10월 23일 ~ 2027년 4월 16일 (6개월, 26회)"),
    ("원고", "방송 주 월요일 한글 파일 전달 (질문 7개 · 시연 3개 · 숙제 1개 구성)"),
]

INTENT = [
    "1회 방송 후 \"어디서 어떻게 깔아요?\" 문의가 쏟아짐 → 2~4회를 왕초보 입문 3부작으로 재구성",
    "단순 검색이 아니라 사진·음성·기억·자동 알림 같은 최신 기능을 휴대폰 하나로 바로 따라 하게",
    "생활 · 업무 · 가족 · 외주 서비스 의뢰 · 안전 등 신중년이 실제 겪는 문제를 해결하는 순서로",
    "계절과 명절(김장, 연말, 연말정산, 설, 봄나들이)에 맞춰 \"이번 주에 바로 쓸\" 주제 배치",
]

PRINCIPLES = [
    ("대중 해설", "한마디 정의를 먼저 → 생활 비유 2~3개 → 뉴스 숫자는 1~2개만 반올림해서 → 핵심은 '세 가지 표어'로"),
    ("걱정 먼저 풀기", "돈 나갈까, 고장 날까, 개인정보 샐까. 걱정을 먼저 꺼내 안심시키고, 진짜 주의할 점은 분명하게"),
    ("듣는 라디오", "화면 대신 모양·위치·색으로 설명 (예: 오른쪽 아래 동그란 물결 버튼). 주소·긴 영어는 말하지 않기"),
    ("따라 하기", "3단계 이내, 번호 붙여 말하기. 시연은 지금 일어나는 일을 말로 중계"),
    ("반복", "회차 표어를 답변 중간과 클로징에서 두 번 이상 들려주기"),
    ("안전", "건강·돈·법률은 '최종 확인은 전문가·공식 기관'. 주민번호·계좌·비밀번호는 AI에 넣지 않기"),
]

FORMAT = [
    ("오프닝", "진행자 인사, 강사 소개"),
    ("질문 1~2", "생활 공감 → 무엇이 어려운지 (지난주 숙제 이어받기)"),
    ("질문 3", "오늘의 해결책 한마디 정의 + 최신 소식 + 무료/유료"),
    ("질문 4~6", "시연 세 가지 (강사가 휴대폰으로 실제 대화를 중계)"),
    ("질문 7", "이번 주 숙제: 그대로 따라 말할 문장 하나"),
    ("클로징", "오늘의 표어 반복, 다음 주 예고"),
]


class Writer:
    def __init__(self):
        self.doc = HwpxDocument.new()
        props = self.doc.sections[0].properties
        props.set_page_margins(left=4252, right=4252, top=4252, bottom=4252)  # 15mm
        self.title = self.doc.ensure_run_style(bold=True, size=20, color="#1F3864")
        self.h2 = self.doc.ensure_run_style(bold=True, size=14, color="#1F3864")
        self.h3 = self.doc.ensure_run_style(bold=True, size=11.5, color="#2E5597")
        self.body = self.doc.ensure_run_style(size=10.5)
        self.small = self.doc.ensure_run_style(size=9)
        self.small_bold = self.doc.ensure_run_style(size=9, bold=True)
        self.muted = self.doc.ensure_run_style(size=9, color="#666666")
        first = self.doc.paragraphs[0]
        first.add_run("", char_pr_id_ref=self.body)

    def _index(self):
        return len(self.doc.paragraphs) - 1

    def para(self, text, style=None, *, align=None, before=None, after=None, bottom_border=False):
        self.doc.add_paragraph(text, char_pr_id_ref=style or self.body, inherit_style=False)
        fmt = {}
        if align:
            fmt["alignment"] = align
        if before is not None:
            fmt["spacing_before_pt"] = before
        if after is not None:
            fmt["spacing_after_pt"] = after
        if bottom_border:
            fmt["bottom_border"] = True
        if fmt:
            self.doc.set_paragraph_format(paragraph_index=self._index(), **fmt)

    def heading(self, text):
        self.para(text, self.h2, before=14, after=4, bottom_border=True)

    def bullets(self, items):
        for item in items:
            self.para("• " + item, self.body, after=2)

    def table(self, rows, widths, header=True, header_fill="#DCE6F2", label_col=False):
        t = self.doc.add_table(len(rows), len(rows[0]))
        t.set_column_widths(widths)
        for r, row in enumerate(rows):
            for c, value in enumerate(row):
                cell = t.cell(r, c)
                cell.set_text(str(value))
                bold = (header and r == 0) or (label_col and c == 0)
                for p in cell.paragraphs:
                    for run in p.runs:
                        run.char_pr_id_ref = self.small_bold if bold else self.small
                if header and r == 0:
                    t.set_cell_shading(r, c, header_fill)
                elif label_col and c == 0:
                    t.set_cell_shading(r, c, "#F2F2F2")
        if header:
            # 표가 쪽을 넘어가면 제목 줄을 다음 쪽에도 반복
            t.element.set("repeatHeader", "1")
            for c in range(len(rows[0])):
                t.cell(0, c).element.set("header", "1")
        return t


def build(out_dir):
    data = yaml.safe_load(CURRICULUM.read_text(encoding="utf-8"))
    episodes = data["episodes"]
    w = Writer()

    w.para(f"<{data['program']}>", w.h3, align="CENTER")
    w.para("6개월 방송 계획서", w.title, align="CENTER", after=2)
    w.para("신중년 왕초보를 위한 생활 밀착 AI 실용교육 · 26회", w.muted, align="CENTER", after=10)

    w.heading("1. 개요")
    w.table(OVERVIEW, [18, 82], header=False, label_col=True)

    w.heading("2. 기획 의도")
    w.bullets(INTENT)

    w.heading("3. 전달 원칙 - 쉽게, 대중적으로, 듣는 라디오답게")
    w.table([("원칙", "방법")] + PRINCIPLES, [18, 82])

    w.heading("4. 매회 구성 (30분)")
    w.table([("순서", "내용")] + FORMAT, [18, 82])

    w.heading("5. 4부 구성")
    w.table([("구분", "회차", "방향")] +
            [(name, f"{a}~{b}회", desc) for a, b, name, desc in PARTS], [26, 12, 62])

    w.heading("6. 회차별 계획")
    for a, b, name, desc in PARTS:
        w.para(f"{name}  ({a}~{b}회)", w.h3, before=8, after=3)
        rows = [("회", "방송일", "영역", "주제", "활용 기능", "오늘의 표어")]
        for ep in episodes:
            if a <= ep["ep"] <= b:
                air = str(ep["air"])
                done = " ✔" if ep.get("status") == "done" else ""
                rows.append((f"{ep['ep']}{done}", f"{air[5:7]}/{air[8:10]}", ep["category"],
                             ep["title"], ep["tool"], ep.get("takeaway", "")))
        w.table(rows, [6, 8, 8, 30, 30, 18])

    w.heading("7. 운영 메모")
    w.bullets([
        "원고는 방송 주 월요일 오전에 한글 파일로 전달 (✔ = 원고 완료 회차)",
        "AI 기능과 요금제는 자주 바뀌므로, 원고 작성 주에 공식 자료로 다시 확인하고 필요하면 주제의 활용 기능을 바꿈",
        "시연의 AI 답변은 예시. 생방송은 미리 녹음한 시연 음성을 준비",
        "청취자 문의가 많은 주제는 이후 회차에 반영 (1회 후 설치 문의 → 2~4회 입문편 재구성)",
    ])

    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / f"{data['program']}_전체계획서.hwp"
    preview = "\r\n".join(p.text or "" for p in w.doc.paragraphs)[:1024]
    w.doc.package.write("Preview/PrvText.txt", preview.encode("utf-8"))
    w.doc.save_to_path(out)
    w.doc.save_to_path(out.with_suffix(".hwpx"))
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=str(ROOT / "output"))
    print(build(ap.parse_args().out))


if __name__ == "__main__":
    sys.exit(main())
