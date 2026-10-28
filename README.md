# maumcore

## 라디오 <알아두면 쓸모있는 AI> 원고 자동화

50대 이상 신중년 대상 라디오 AI 실용교육 코너(매주 금요일, 6개월 26회)의 원고를
1회차 샘플과 **같은 한글(.hwp) 서식**으로 매주 월요일 만들어 전달합니다.

| 경로 | 내용 |
|---|---|
| `radio_ai/curriculum.yaml` | 26회 주제표 (생활·업무·가족·외주의뢰·안전, 1회 1꿀팁) |
| `radio_ai/STYLE_GUIDE.md` | 샘플 원고에서 뽑은 구성·문체 규칙, 원고 소스 형식 |
| `radio_ai/WEEKLY_TASK.md` | 매주 월요일 자동 작성 절차 |
| `radio_ai/episodes/epNN.md` | 회차별 원고 소스 |
| `radio_ai/template/header_template.hwp` | 1회차 샘플에서 머리말만 남긴 서식 템플릿 (연락처는 자리표시자) |
| `tools/render_script.py` | 원고 소스 → `.hwp` (샘플의 문단·글자 모양 그대로) |
| `tools/render_plan.py` | curriculum.yaml → 6개월 전체 계획서 `.hwp` |
| `tools/hwp_to_text.py` | `.hwp` → 텍스트 (검수용) |

```bash
pip install -r requirements.txt
python tools/render_script.py radio_ai/episodes/ep02.md --contact 010-0000-0000
# → output/알아두면 쓸모있는 AI_261030.hwp
python tools/render_plan.py
# → output/알아두면 쓸모있는 AI_전체계획서.hwp
```

- 강사 연락처는 공개 저장소에 올리지 않습니다. `--contact` 또는 환경변수 `RADIO_CONTACT` 로 넣습니다.
- GitHub Actions(`.github/workflows/render-scripts.yml`)가 원고가 바뀔 때마다 .hwp 를 만들어
  Actions 아티팩트로 올립니다. 연락처를 넣으려면 저장소 Secret `RADIO_CONTACT` 를 등록하세요.
- HWP 쓰기는 [python-hwpx](https://github.com/airmang/python-hwpx) 를 사용합니다.
