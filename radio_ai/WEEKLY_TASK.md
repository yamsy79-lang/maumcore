# 매주 월요일 자동 원고 작성 절차

예약 작업(매주 월요일 06:47 KST)이 새 Claude 세션을 열고 이 문서대로 진행합니다.
사람이 직접 돌릴 때도 같은 순서를 따르면 됩니다.

1. **회차 결정**: `radio_ai/curriculum.yaml` 에서 `status: todo` 중 `air` 날짜가 이번 주 금요일인 회차.
   (이번 주 금요일 회차가 이미 done이면 다음 todo 회차)
2. **최신 기능 확인**: 회차의 `tool` 이 지금도 되는지, 한국어·모바일 지원, 무료/유료 범위를
   웹 검색으로 확인한다. 공식 도움말·공식 블로그를 우선. 더 쉽고 새로운 기능이 나왔으면
   그걸로 바꾸고 curriculum.yaml 의 tool 을 고친다. **확인 못 한 내용은 원고에 단정적으로 쓰지 않는다.**
3. **원고 작성**: `radio_ai/STYLE_GUIDE.md`(특히 3-1 대중 해설, 3-2 듣는 라디오)를 지키고 `radio_ai/episodes/ep02.md`(전달 스타일 기준)와 `ep01.md`(형식 기준)를 참고해
   `radio_ai/episodes/epNN.md` 작성 (본문 1,800~2,300자, 질문 7개, 시연 3개, 숙제 1개, 제작메모 포함).
   지난 회차 숙제를 인사에서 가볍게 이어받고, 제작메모에 다음 주 예고를 적는다.
4. **HWP 생성**: `pip install -r requirements.txt` 후
   `python tools/render_script.py radio_ai/episodes/epNN.md --contact <강사 연락처> --out output`
   → `python tools/hwp_to_text.py "output/알아두면 쓸모있는 AI_YYMMDD.hwp"` 로 내용·분량 확인.
5. **기록**: curriculum.yaml 의 해당 회차 `status: done`. `output/` 은 커밋하지 않는다(.gitignore).
   epNN.md 와 curriculum.yaml 을 커밋·푸시한다.
6. **전달**: 생성한 .hwp 와 예비본 .hwpx 를 첨부해 담당자 메일로 발송.
   제목 `[알아두면 쓸모있는 AI] N회차 원고 (MM/DD 방송) - 제목`,
   본문에 회차 요약 3줄 + 제작메모(준비물·팩트체크 출처·주의사항) + 다음 주 예고.
