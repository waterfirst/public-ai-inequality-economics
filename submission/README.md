# ISTANS 산업통계 우수활용사례 공모전 — 제출자료

이 폴더는 「ISTANS 산업통계 우수활용사례 공모전」활용수기 트랙 제출물이다.

- `ISTANS_활용수기_최낙초.pdf` — 활용수기(A4). 본 저장소의 산업통계 기반 공공 AI·분배
  시뮬레이션 연구를 산업통계 활용사례로 정리한 글.

## 이 저장소와의 연결
활용수기의 모든 수치는 본 저장소의 재현 파이프라인에서 나온다.

- 데이터 수집: `scripts/10_download_kr_data.py` (KOSIS·ECOS OpenAPI, 통계표 ID·조회일 기록)
- 파라미터 캘리브레이션: `scripts/11_calibrate_from_kr_data.py` → `calibration.json`
- 실인구 시뮬레이션: `scripts/12_public_ai_real_simulation.py` (NVIDIA 검증 프로필)
- 출판급 강건성: `scripts/13_rigor_experiments.py` (paired MC·ablation·finite-size)
- 논문: `public_ai_economics_paper_en.qmd`

## 개인정보 관련
참가신청서·개인정보수집이용동의서는 개인정보(성명·연락처·이메일)를 포함하므로
공개 저장소에 포함하지 않는다(별도 비공개 전달).

## 유의
- 공고상 활용수기는 최종 제출 시 한글문서(.hwp) 형식이 요구될 수 있다(PDF는 참고용).
- 연락처 등 미확정 개인정보는 제출 전 반드시 확인·기입한다.
