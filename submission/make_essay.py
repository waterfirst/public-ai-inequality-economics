# -*- coding: utf-8 -*-
"""ISTANS 활용수기 — 국문 3페이지(양식3 규격) PDF 생성."""
import base64, os
from playwright.sync_api import sync_playwright

OUT = os.path.dirname(os.path.abspath(__file__))
FIG = os.path.join(OUT, "..", "istans_work", "results", "public_ai_real", "03_policy_frontier.png")
b64 = base64.b64encode(open(FIG, "rb").read()).decode() if os.path.exists(FIG) else ""
img_tag = f"<img class='fig' src='data:image/png;base64,{b64}'/>" if b64 else ""

TITLE = "산업통계로 본 ‘모두의 AI’: 산업별 고용·생산성 데이터를 활용한 공공 AI 정책의 양극화 효과 시뮬레이션"

CSS = """
<style>
@page { size:A4; margin:15mm 20mm 15mm 20mm; }
*{box-sizing:border-box;}
body{font-family:'NanumMyeongjo',serif; color:#111; font-size:11pt; line-height:1.62; margin:0;}
h1{font-family:'NanumGothic',sans-serif; font-size:13pt; font-weight:800; text-align:center; margin:0 0 2mm; line-height:1.4;}
.meta{font-size:9pt; color:#444; text-align:center; margin-bottom:3mm; border-bottom:1px solid #ccc; padding-bottom:2mm;}
.sec{font-family:'NanumGothic',sans-serif; font-weight:800; font-size:11pt; margin:3.2mm 0 1mm; color:#12345a;}
p{margin:1.4mm 0; text-align:justify;}
ul{margin:1mm 0 1.5mm 5mm;} li{margin:0.5mm 0;}
b.k{font-family:'NanumGothic',sans-serif;}
table{width:100%; border-collapse:collapse; margin:1.5mm 0; font-size:9.5pt;}
td,th{border:1px solid #666; padding:1.2mm 2mm; text-align:center;}
th{background:#eef2f7; font-family:'NanumGothic',sans-serif;}
td.l{text-align:left;}
.fig{width:78%; display:block; margin:1.5mm auto; border:1px solid #ccc;}
.cap{font-size:8.5pt; color:#555; text-align:center; margin:0 0 2mm;}
.small{font-size:9pt; color:#444;}
</style>
"""

BODY = f"""
<h1>{TITLE}</h1>
<div class='meta'>활용자 유형: 직장인 · 개인 참가 &nbsp;|&nbsp; 활용 산업통계: 산업별 취업자·노동생산성·지역생산성·노동소득분배율 등</div>

<div class='sec'>1. 활용 배경과 문제의식</div>
<p>2026년 7월 과학기술정보통신부는 전 국민에게 무료·무제한으로 국산 AI 챗봇을 제공하고 공공서비스를 대신 신청해 주는 AI 에이전트를 더하는 <b class='k'>‘모두의 AI’ 프로젝트</b>에 착수하였다. 이 정책의 근거는 국민 약 3분의 1이 여전히 AI를 사용하지 못하는 <b class='k'>AI 활용 격차</b>다. 그러나 “무료 보급” 자체가 격차를 줄이는지는 자명하지 않다. 같은 서비스를 받아도 숙련, 직무 유연성, 프리미엄 모델 접근, 자본 소유가 다르면 실효 활용과 경제적 성과가 벌어지기 때문이다. 본인은 “보편적 공공 AI 제공만으로 AI가 유발하는 <b class='k'>산업·소득 양극화</b>를 완화할 수 있는가”라는 질문을, <b class='k'>산업통계에 근거한 정량 시뮬레이션</b>으로 검증하였다. 핵심은 모형의 파라미터를 임의로 가정하지 않고 <b class='k'>실제 산업통계로 보정(calibration)</b>하는 것이다.</p>

<div class='sec'>2. 활용한 산업통계 데이터</div>
<p>산업연구원 ISTANS가 제공하는 <b class='k'>산업별 생산성·부가가치·고용 등 산업통계 도메인</b>을 분석의 축으로 삼고, 동 도메인의 공식 통계를 프로그램으로 수집·연계하여 재현 가능한 형태로 구성하였다. 실제 사용한 계열은 다음과 같으며, 각 계열은 통계표 식별자·출처·조회일을 함께 기록하였다.</p>
<ul>
<li><b class='k'>산업별 취업자</b>(경제활동인구조사) — 산업 간 노동 재배치(직무 이동) 강도 추정</li>
<li><b class='k'>산업별 노동생산성지수</b> 및 <b class='k'>제조업 지역별 노동생산성</b> — 산업·지역 간 생산성 격차</li>
<li><b class='k'>국민계정 노동소득분배율</b>(피용자보수÷요소비용국민소득) — 자본소득 비중</li>
<li>인구 구조는 공개 합성 페르소나(연령×성별×지역×교육×직업)를 <b class='k'>개인식별·서사 필드를 모두 제거한 집계</b>로만 활용</li>
</ul>

<div class='sec'>3. 분석 방법</div>
<p>분석의 출발점은 <b class='k'>‘명목 접근’과 ‘실효 이용’의 구분</b>이다. 모두에게 계정을 무료로 열어 주어도(명목 접근), 개인이 AI 출력의 오류를 걸러 업무에 통합하는 역량, 대체되는 직무에서 보완적 직무로 이동할 가능성, 프리미엄 모델·데이터·조직자본의 소유가 다르면 실제로 얻는 생산성(실효 이용)은 벌어진다. 이 격차를 명시적으로 모형화하기 위해, 산업통계로 다음 <b class='k'>구조 파라미터</b>를 직접 추정하였다 — ① 산업 간 재배치 속도 ρ, ② 자본소득 비중 κ, ③ 지역 생산성 페널티. 이 값을 이질적 에이전트(heterogeneous-agent) 전이 모형에 주입하고, 시장 기준안과 5개 공공 AI 정책조합(보편접근·공교육·돌봄·종합안·저품질 실패안)을 <b class='k'>동일 난수·동일 초기인구로 짝지어(paired)</b> 비교하였다. 강건성은 40회 몬테카를로 반복의 95% 신뢰구간, 메커니즘 제거(ablation) 실험, 표본크기 250~2,000 스케일링으로 확인하였다. 인구 구조는 공개 합성 페르소나(연령×성별×지역×교육×직업 집계)를 사용하되 실제 국민 표본으로 해석하지 않으며, 모든 과정은 코드로 공개되어 재현 가능하다.</p>

<div class='sec'>4. 주요 분석 내용과 결과</div>
<p>산업통계로 보정한 결과, 한국의 산업 간 노동 재배치 속도는 <b class='k'>연 1.4%(ρ=0.0136)</b>로 흔한 ‘대격변’ 서사보다 낮았다. 노동소득분배율은 2015년 62.3%→2024년 <b class='k'>67.4%</b>로 상승하여 자본소득 비중은 약 1/3(κ=0.327), 제조업 지역 간 노동생산성 격차는 <b class='k'>상·하위 약 57%</b>였다. 이 실측 구조를 반영한 정책 시뮬레이션의 핵심 결과는 다음과 같다.</p>
<table>
<tr><th>정책 시나리오</th><th>Δ양극화(Wolfson)</th><th>95% 신뢰구간</th><th>Δ취약계층 고용</th></tr>
<tr><td class='l'>시장·프리미엄 AI(기준)</td><td>+0.192</td><td>[0.187, 0.196]</td><td>−0.2%p</td></tr>
<tr><td class='l'>전국민 무료 공공 AI</td><td>+0.190</td><td>[0.186, 0.194]</td><td>−0.2%p</td></tr>
<tr><td class='l'>공공 AI + 공교육</td><td>+0.194</td><td>[0.190, 0.198]</td><td>+2.5%p</td></tr>
<tr><td class='l'>공공 AI 종합안(교육·돌봄·자본소유)</td><td><b>+0.164</b></td><td><b>[0.161, 0.167]</b></td><td><b>+5.9%p</b></td></tr>
</table>
{img_tag}
<div class='cap'>[그림] 효율–양극화 프런티어. 종합안이 취약계층 고용(점 크기)을 키우며 양극화를 낮춘다.</div>
<p>세 가지 발견이 핵심이다. <b class='k'>첫째,</b> 재배치 속도가 낮음에도 모든 정책에서 양극화는 상승했다(신뢰구간이 모두 0 초과). 동인은 재배치 ‘속도’가 아니라 산업·교육·자본에 내재한 <b class='k'>격차 구조</b>였다. <b class='k'>둘째,</b> 종합 정책안만 양극화를 유의하게 완화했다(시장 대비 차이 +0.0275, 95% CI [0.025, 0.030]로 0 배제). <b class='k'>셋째,</b> 종합안에서 각 요소를 하나씩 제거하는 분해 실험은 <b class='k'>양극화와 고용이 서로 다른 지렛대로 움직임</b>을 보였다.</p>
<table>
<tr><th>종합안에서 제거한 요소</th><th>Δ양극화(Wolfson)</th><th>Δ취약계층 고용</th></tr>
<tr><td class='l'>제거 없음(종합안 전체)</td><td>0.164</td><td>+5.9%p</td></tr>
<tr><td class='l'>− AI 자본소유·배당 환류</td><td><b>0.190</b>(최대 악화)</td><td>+5.9%p</td></tr>
<tr><td class='l'>− 공교육</td><td>0.161</td><td>+3.2%p</td></tr>
<tr><td class='l'>− 돌봄</td><td>0.167</td><td>+2.5%p</td></tr>
</table>
<p>즉 <b class='k'>양극화 완화의 주력은 ‘AI 자본소유 환류’</b>(제거 시 악화 폭 최대)이고, <b class='k'>취약계층 고용 개선의 주력은 ‘교육·돌봄’</b>이다. ‘모두의 AI’식 <b class='k'>무료 접근만으로는 부족</b>하며, 자본소유와 역량투자가 결합될 때 비로소 분배가 개선된다.</p>

<div class='sec'>5. 정책 시사점 — ‘모두의 AI’ 설계 제언</div>
<p>본 분석은 진행 중인 국가정책에 직접 적용된다. 산업통계로 확인된 <b class='k'>‘AI 미사용 3분의 1’은 곧 저학력·비경제활동 계층</b>과 겹치며, 이들에게는 무료 챗봇만으로 소득·후생이 오르지 않았다(모형의 취약계층 순후생은 접근만으로는 음(−)). 따라서 ‘모두의 AI’의 성패는 챗봇 출시가 아니라 <b class='k'>보상적 설계</b>에 달려 있다. 구체적으로 ① 저역량층 우선 <b class='k'>AI 활용 공교육</b>, ② <b class='k'>돌봄·행정 부담 경감</b>으로 학습·구직 시간 확보, ③ <b class='k'>시민·근로자의 AI 자본(데이터·컴퓨트·플랫폼) 지분</b> 확대를 결합해야 한다. 성과지표도 이용률이 아니라 <b class='k'>분배·전환·권리 지표</b>(양극화, 취약계층 고용, 지역·교육 격차)로 전환할 것을 제언한다.</p>

<div class='sec'>6. 효과적인 산업통계 이용 방법</div>
<p>산업통계를 <b class='k'>모형 파라미터로 직접 캘리브레이션</b>하는 접근은 정책 시뮬레이션의 임의성을 줄이고, 통계표 식별자 기반 출처 추적으로 재현성과 심사 신뢰도를 높였다. 산업×지역×시점의 다차원 산업통계는 “접근 격차”가 아니라 “<b class='k'>실효 활용 격차</b>”를 드러내는 데 특히 유용하였다. 정책 담당자는 동일 방식으로 자기 지역·업종의 산업통계를 넣어 정책조합을 사전 시험할 수 있다.</p>

<div class='sec'>7. ISTANS 이용 편의성·활용성 개선 의견</div>
<ul>
<li><b class='k'>OpenAPI 제공 강화</b>: 통계청 KOSIS·한국은행 ECOS처럼 인증키 기반 REST API와 통계표 ID 체계를 제공하면 산업통계를 코드로 재현 가능하게 수집·인용할 수 있다.</li>
<li><b class='k'>다차원 결합표 일괄 다운로드</b>: 산업×지역×연도 결합 시계열을 셀 수 제한 없이 CSV/JSON으로 일괄 추출(현재는 화면 단위 조회 위주).</li>
<li><b class='k'>메타데이터·단위 표준화</b>: 각 계열의 단위·산정식·기준연도·개정이력을 기계판독 가능한 메타데이터로 병기.</li>
<li><b class='k'>인용 식별자·스냅샷</b>: 통계표별 영구 식별자와 조회일 스냅샷으로 학술·정책 인용의 추적성 확보.</li>
<li><b class='k'>재현 예제 배포</b>: 대표 산업통계 활용 코드(파라미터 추정·시각화)를 공식 노트북으로 제공.</li>
</ul>
<p class='small'>※ 근거자료(기타 활용 성과물): 데이터 수집·캘리브레이션·시뮬레이션 전 과정의 재현 코드·결과·논문을 공개.<br>
· 인터랙티브 정책 시뮬레이터: https://waterfirst.github.io/public-ai-inequality-economics/<br>
· 재현 저장소: https://github.com/waterfirst/public-ai-inequality-economics</p>
"""

HTML = f"<!doctype html><html><head><meta charset='utf-8'>{CSS}</head><body>{BODY}</body></html>"

path = os.path.join(OUT, "ISTANS_활용수기_최낙초.pdf")
with sync_playwright() as p:
    b = p.chromium.launch(headless=True)
    pg = b.new_page()
    pg.set_content(HTML, wait_until="networkidle")
    pg.pdf(path=path, format="A4", print_background=True,
           margin={"top": "15mm", "bottom": "15mm", "left": "20mm", "right": "20mm"})
    b.close()
print("wrote", path)
