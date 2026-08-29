# -*- coding: utf-8 -*-
"""2026 ISTANS 논문경진대회 공식 양식에 맞춘 국문 논문 PDF 생성."""
import base64, os
from playwright.sync_api import sync_playwright

OUT = os.path.dirname(os.path.abspath(__file__))
FIGROOT = os.path.join(OUT, "..", "istans_work", "results", "public_ai_real")
def b64(name):
    p = os.path.join(FIGROOT, name)
    return "data:image/png;base64," + base64.b64encode(open(p, "rb").read()).decode() if os.path.exists(p) else ""
FIG_FRONTIER = b64("03_policy_frontier.png")
FIG_DYN = b64("01_policy_dynamics.png")

TITLE = "산업통계로 본 공공 AI 정책의 경제 양극화 효과"
SUBTITLE = "한국 공식통계와 합성 인구를 이용한 이질적 에이전트 시뮬레이션 — ‘모두의 AI’ 사업에의 함의"
AUTHOR = "최낙초"
AFFIL = "삼성디스플레이"

CSS = """
<style>
@page { size:A4; margin:20mm 20mm 18mm 20mm;
  @top-center { content:"2026 ISTANS 논문경진대회"; font-family:'NanumGothic'; font-size:9pt; color:#555; }
  @bottom-center { content: counter(page); font-family:'NanumGothic'; font-size:9pt; color:#555; } }
*{box-sizing:border-box;}
body{font-family:'NanumMyeongjo',serif; color:#111; font-size:11pt; line-height:1.7; margin:0;}
.cover{height:257mm; display:flex; flex-direction:column; justify-content:center; text-align:center; page-break-after:always;}
.cover .badge{font-family:'NanumGothic'; font-size:13pt; color:#333; letter-spacing:2px; margin-bottom:40mm;}
.cover h1{font-family:'NanumGothic'; font-size:20pt; font-weight:800; line-height:1.4; margin:0 8mm;}
.cover h2{font-family:'NanumMyeongjo'; font-size:13pt; font-weight:400; color:#333; margin:6mm 10mm 40mm;}
.cover .date{font-size:12pt; margin-bottom:14mm;}
.cover table{margin:0 auto; border-collapse:collapse;}
.cover td{border:none; padding:2mm 6mm; font-size:12pt;}
.cover td.k{font-family:'NanumGothic'; font-weight:700; text-align:right; color:#333;}
.pagebreak{page-break-after:always;}
h3.ch{font-family:'NanumGothic'; font-size:15pt; font-weight:800; margin:6mm 0 3mm; color:#12345a; border-bottom:2px solid #12345a; padding-bottom:1.5mm;}
h4.sec{font-family:'NanumGothic'; font-size:12.5pt; font-weight:800; margin:4mm 0 1.5mm;}
h5.sub{font-family:'NanumGothic'; font-size:11.5pt; font-weight:700; margin:3mm 0 1mm; color:#333;}
p{margin:1.6mm 0; text-align:justify;}
ul{margin:1mm 0 2mm 6mm;} li{margin:0.6mm 0;}
b.k{font-family:'NanumGothic';}
.summary{font-family:'NanumGothic'; font-size:13pt; font-weight:800; text-align:center; margin:4mm 0 4mm;}
.toc h4{font-family:'NanumGothic'; font-size:12pt; margin:4mm 0 1mm;}
.toc div{margin:0.8mm 0;} .toc .i1{margin-left:4mm;} .toc .i2{margin-left:10mm;}
table.data{width:100%; border-collapse:collapse; margin:2mm 0; font-size:10pt;}
table.data td, table.data th{border:1px solid #555; padding:1.4mm 2mm; text-align:center;}
table.data th{background:#eef2f7; font-family:'NanumGothic';}
table.data td.l{text-align:left;}
.capT{font-family:'NanumGothic'; font-size:10pt; font-weight:700; margin:3mm 0 0.5mm;}
.capF{font-family:'NanumGothic'; font-size:10pt; font-weight:700; text-align:center; margin:3mm 0 0.5mm;}
img.fig{width:80%; display:block; margin:1mm auto; border:1px solid #ccc;}
.src{font-size:9pt; color:#555; margin:0.5mm 0 2mm;}
.refs{font-size:10pt;} .refs p{margin:1mm 0; text-indent:-6mm; margin-left:6mm;}
</style>
"""

COVER = f"""
<div class='cover'>
  <div class='badge'>2026 ISTANS 논문경진대회</div>
  <h1>{TITLE}</h1>
  <h2>{SUBTITLE}</h2>
  <div class='date'>2026.  8.</div>
  <table><tr><td class='k'>소　속</td><td>{AFFIL}</td></tr>
  <tr><td class='k'>이　름</td><td>{AUTHOR}</td></tr></table>
</div>
"""

SUMMARY = """
<div class='summary'>논문 요약</div>
<p>본 연구의 목적은 <b class='k'>보편적 공공 AI 제공이 인공지능 확산에 따른 경제 양극화를 완화할 수 있는지</b>를 산업통계에 근거해 정량적으로 규명하는 데 있다. 2026년 7월 정부가 착수한 ‘모두의 AI’ 사업은 전 국민에게 무료·무제한 국산 AI 챗봇을 제공하려 하지만, 같은 서비스를 받아도 숙련·직무·자본이 다르면 실효 이용과 성과가 벌어진다. 이에 본 연구는 산업별 취업자·산업 및 지역별 노동생산성·국민계정 노동소득분배율 등 <b class='k'>공식 산업·경제 통계로 모형의 구조 파라미터를 직접 보정</b>하고, 합성 인구(연령×성별×지역×교육×직업 층화)를 표본으로 삼아 이질적 에이전트 시뮬레이션을 수행하였다. 짝지은 몬테카를로(95% 신뢰구간)·메커니즘 제거·표본크기 스케일링으로 강건성을 검증한 결과, <b class='k'>보편적 접근은 필요조건이나 그 자체로 양극화를 되돌리지 못하며</b>, 교육·돌봄·AI 자본소유가 결합될 때에만 분배가 개선되었다. 특히 <b class='k'>양극화 완화의 주력은 ‘AI 자본소유 환류’, 취약계층 고용 개선의 주력은 ‘교육·돌봄’</b>이라는 두 채널 구조를 규명하였다. 본 결과는 ‘모두의 AI’를 이용률이 아닌 분배·전환·권리 지표로 설계·평가해야 함을 시사한다.</p>
<p class='src'>주제어: 산업통계, 공공 AI, 경제 양극화, 이질적 에이전트 시뮬레이션, 노동생산성, 노동소득분배율</p>
"""

TOC = """
<div class='toc'>
<h4>차　례</h4>
<div>제1장 연구의 목적 및 방법</div>
<div class='i1'>1. 서론: ‘모두의 AI’와 AI 활용 격차</div>
<div class='i1'>2. 연구 방법과 분석틀</div>
<div>제2장 산업통계 기반 파라미터 보정과 모형</div>
<div class='i1'>1. 활용한 산업통계와 파라미터 보정</div>
<div class='i1'>2. 이질적 에이전트 모형과 정책 시나리오</div>
<div>제3장 시뮬레이션 분석 결과와 정책 함의</div>
<div class='i1'>1. 실인구 시뮬레이션 결과</div>
<div class='i2'>(1) 정책별 분배·고용 효과</div>
<div class='i2'>(2) 강건성: 신뢰구간·메커니즘 분해·표본크기</div>
<div class='i1'>2. 정책 논의와 결론</div>
<div class='i2'>(1) ‘모두의 AI’ 설계 제언</div>
<div class='i2'>(2) 한계와 결론</div>
<div>참고문헌</div>
<h4 style='margin-top:6mm'>표 차례</h4>
<div>&lt;표 2-1&gt; 산업통계 기반 파라미터 보정 결과</div>
<div>&lt;표 3-1&gt; 정책 시나리오별 분배·고용 효과(실인구, 95% 신뢰구간)</div>
<div>&lt;표 3-2&gt; 종합안 메커니즘 제거(ablation) 분해</div>
<h4 style='margin-top:6mm'>그림 차례</h4>
<div>&lt;그림 3-1&gt; 효율–양극화 정책 프런티어</div>
<div>&lt;그림 3-2&gt; 정책조합별 분배 동학</div>
</div>
"""

CH1 = """
<h3 class='ch'>제1장 연구의 목적 및 방법</h3>
<h4 class='sec'>1. 서론: ‘모두의 AI’와 AI 활용 격차</h4>
<p>ISTANS(산업통계분석시스템)는 산업통상자원부와 산업연구원이 운영하는 산업통계 빅데이터로, 산업별 생산성·부가가치·고용 등 산업의 구조와 동향을 종합적으로 분석할 수 있게 한다. 본 연구는 이러한 산업통계를 활용하여, 현재 진행 중인 국가 AI 정책의 분배 효과를 정량적으로 평가한다.</p>
<p>생성형 AI는 기초 인터페이스가 거의 즉시 확산되는 반면, 첨단 역량은 희소하고 과금되며 데이터·조직자본·인적자본과 보완적이다. 이로 인해 (i) 기기·연결성에 대한 <b class='k'>접근 격차</b>와, (ii) 모델 품질·업무 통합·모델 출력을 가치로 바꾸는 역량에 대한 <b class='k'>실효 활용 격차</b>가 동시에 발생한다. 2026년 7월 과학기술정보통신부는 전 국민에게 무료·무제한 국산 AI 챗봇과 공공서비스 AI 에이전트를 제공하는 <b class='k'>‘모두의 AI’ 프로젝트</b>에 착수하였는데, 그 근거는 국민 약 3분의 1이 여전히 AI를 쓰지 못하는 활용 격차였다.</p>
<p>본 연구의 목적은 <b class='k'>“보편적 공공 AI 제공만으로 AI가 유발하는 경제 양극화를 완화할 수 있는가”</b>라는 질문에 답하는 것이다. 핵심 문제의식은 명목 접근과 실효 이용의 구분에 있다. 무료 계정을 모두에게 열어도, 숙련·직무 유연성·프리미엄 모델 접근·자본 소유가 불평등하면 실효 이용과 경제적 성과는 벌어진다.</p>

<h4 class='sec'>2. 연구 방법과 분석틀</h4>
<p>본 연구는 세 단계로 구성된다. 첫째, 산업통계로 모형의 <b class='k'>구조 파라미터를 직접 보정</b>한다(제2장 1절). 둘째, 합성 인구를 표본으로 <b class='k'>이질적 에이전트 시뮬레이션</b>을 수행하여 시장 기준과 다섯 개 공공 AI 정책조합을 비교한다(제2장 2절). 셋째, <b class='k'>짝지은 몬테카를로(공통 난수·95% 신뢰구간)·메커니즘 제거(ablation)·표본크기 스케일링</b>으로 결과의 강건성을 검증한다(제3장).</p>
<p>모든 데이터는 통계표 식별자·출처·조회일을 기록하여 재현 가능하며, 분석 코드·데이터·결과는 공개 저장소로 배포한다. 본 연구의 수치는 모형 조건부 비교정학(comparative statics)이며 예측이나 인과효과 추정이 아님을 밝힌다.</p>
"""

CH2 = f"""
<h3 class='ch'>제2장 산업통계 기반 파라미터 보정과 모형</h3>
<h4 class='sec'>1. 활용한 산업통계와 파라미터 보정</h4>
<p>과거의 모형은 구조 파라미터를 가정으로 설정하였다. 본 연구는 그중 네 개를 통계청 KOSIS와 한국은행 ECOS의 OpenAPI에서 직접 수집한 공식 통계로 대체하였다. 사용한 계열과 보정 결과는 &lt;표 2-1&gt;과 같다.</p>
<div class='capT'>&lt;표 2-1&gt; 산업통계 기반 파라미터 보정 결과</div>
<table class='data'>
<tr><th>파라미터</th><th>모형 의미</th><th>실측 앵커</th><th>값</th><th>출처(통계표)</th></tr>
<tr><td>κ</td><td class='l'>AI 자본소득 비중</td><td class='l'>1 − 노동소득분배율(최근 5년)</td><td>0.327</td><td>ECOS 200Y116</td></tr>
<tr><td>ρ</td><td class='l'>직무 재배치 속도</td><td class='l'>산업 간 취업자 연평균 재배치</td><td>0.0136</td><td>KOSIS DT_1DA9003S</td></tr>
<tr><td>ζ</td><td class='l'>산업 생산성 격차</td><td class='l'>산업 노동생산성 증가율 표준편차</td><td>0.115</td><td>KOSIS DT_344N_1D8A_AA</td></tr>
<tr><td>ψ</td><td class='l'>지역 페널티</td><td class='l'>제조업 상·하위 지역 생산성 격차</td><td>0.569</td><td>KOSIS DT_344N_1D8B_DD</td></tr>
</table>
<p class='src'>자료: 통계청 KOSIS, 한국은행 ECOS OpenAPI. 각 계열의 통계표 ID·조회일은 재현 저장소의 MANIFEST에 기록.</p>
<p>세 가지 사실이 모형을 규율한다. 첫째, <b class='k'>노동소득분배율은 2015년 62.3%에서 2024년 67.4%로 상승</b>하여 자본소득 비중은 약 3분의 1이다. 둘째, <b class='k'>산업 간 관측 재배치는 연 1.4%로 종전 가정치(4.5%)보다 낮다.</b> 이는 대격변 서사를 완화하는 동시에, AI가 이 느린 재배치를 가속하면 미지의 영역으로 진입할 수 있음을 경고한다. 셋째, <b class='k'>제조업 지역 생산성 격차는 상·하위 약 57%</b>로, 보편 접근이 균등화하지 못하는 지역 효과의 실증적 근거가 된다.</p>

<h4 class='sec'>2. 이질적 에이전트 모형과 정책 시나리오</h4>
<p>가구는 노동소득·AI 인적자본·AI 보완자본·직업 노출·유연성·돌봄부담·취약성·초기자원 순위를 상태로 갖는다. 분석의 핵심은 <b class='k'>실효 AI 서비스</b>가 명목 접근이 아니라 품질·숙련·유연성의 함수라는 점이다. 즉 실효 서비스는 품질과 (숙련·유연성의 로지스틱 변환)의 곱으로 정의되어, 보편적 명목 접근이 숙련·유연성 불평등을 균등화하지 못함을 나타낸다. AI 자본소득은 자본·노출·실효서비스에 비례하며, 정부는 자본소득 일부를 누진 가중치로 재분배하되 예산 항등식을 강제한다.</p>
<p>인구의 인구학적 구조는 공개 합성 페르소나(연령×성별×지역×교육×직업의 3,405개 익명 층화)에서 취하되, 개인 이름·서사 필드를 제거하고 집계만 사용하며 실제 국민 표본으로 해석하지 않는다. 교육수준은 기초 숙련으로, 직업은 AI 노출·보완성으로, 지역은 실효접근 용량(제조업 지역 생산성 기반)으로 사상한다. 비교 대상 정책은 ① 시장·프리미엄 AI(기준), ② 전국민 공공 AI, ③ 공공 AI+공교육, ④ 공공 AI+돌봄, ⑤ 공공 AI 종합안(접근·교육·돌봄·자본배당·근로자소유), ⑥ 저품질 공공 AI의 여섯이다.</p>
"""

CH3 = f"""
<h3 class='ch'>제3장 시뮬레이션 분석 결과와 정책 함의</h3>
<h4 class='sec'>1. 실인구 시뮬레이션 결과</h4>
<h5 class='sub'>(1) 정책별 분배·고용 효과</h5>
<p>24개 시드·6개 정책(144회 짝비교, 15기)에서 정책 순위는 유지되되 수준이 유의미하게 이동한다(&lt;표 3-1&gt;). 실측된 낮은 재배치율에도 <b class='k'>모든 정책에서 양극화(Wolfson 지수)가 상승</b>한다. 동인은 재배치 속도가 아니라 실제 인구가 지닌 교육–직업–자본 격차다.</p>
<div class='capT'>&lt;표 3-1&gt; 정책 시나리오별 분배·고용 효과(실인구, 40시드 95% 신뢰구간)</div>
<table class='data'>
<tr><th>정책</th><th>Δ Wolfson</th><th>95% CI</th><th>Δ 취약계층 고용</th></tr>
<tr><td class='l'>시장·프리미엄 AI(기준)</td><td>0.1915</td><td>[0.187, 0.196]</td><td>−0.2%p</td></tr>
<tr><td class='l'>전국민 공공 AI</td><td>0.1903</td><td>[0.186, 0.194]</td><td>−0.2%p</td></tr>
<tr><td class='l'>공공 AI + 공교육</td><td>0.1943</td><td>[0.190, 0.198]</td><td>+2.5%p</td></tr>
<tr><td class='l'>공공 AI + 돌봄</td><td>0.1866</td><td>[0.183, 0.191]</td><td>+3.2%p</td></tr>
<tr><td class='l'><b>공공 AI 종합안</b></td><td><b>0.1639</b></td><td><b>[0.161, 0.167]</b></td><td><b>+5.9%p</b></td></tr>
<tr><td class='l'>저품질 공공 AI</td><td>0.1924</td><td>[0.188, 0.197]</td><td>+1.6%p</td></tr>
</table>
<p><b class='k'>종합안만이 양극화를 유의하게 완화</b>한다. 시장 대비 감소분은 +0.0275, 95% 신뢰구간 [0.0252, 0.0298]로 0을 배제한다. 종합안은 취약계층 고용을 5%p 이상 높이는 유일한 안이기도 하다.</p>
<div class='capF'>&lt;그림 3-1&gt; 효율–양극화 정책 프런티어</div>
<img class='fig' src='{FIG_FRONTIER}'/>
<p class='src'>주: 점 크기는 취약계층 고용 개선폭. 종합안이 고용을 키우며 양극화를 낮추는 위치에 있다.</p>

<h5 class='sub'>(2) 강건성: 신뢰구간·메커니즘 분해·표본크기</h5>
<p>거버넌스 검증(금지 서사 필드 없음)을 통과한 프로필에서 강건성을 확인하였다. 짝지은 몬테카를로에서 모든 정책의 Δ Wolfson 신뢰구간이 0을 초과하여(가설 H1 확증), 보편 접근만으로 양극화가 역전되지 않음을 보인다. 메커니즘 제거 실험(&lt;표 3-2&gt;)은 <b class='k'>양극화와 고용이 서로 다른 지렛대로 움직임</b>을 드러낸다.</p>
<div class='capT'>&lt;표 3-2&gt; 종합안 메커니즘 제거(ablation) 분해</div>
<table class='data'>
<tr><th>종합안에서 제거한 요소</th><th>Δ Wolfson</th><th>Δ 취약계층 고용</th></tr>
<tr><td class='l'>제거 없음(종합안 전체)</td><td>0.1639</td><td>+5.9%p</td></tr>
<tr><td class='l'>− AI 자본소유·배당 환류</td><td><b>0.1899</b>(최대 악화)</td><td>+5.9%p</td></tr>
<tr><td class='l'>− 돌봄</td><td>0.1667</td><td>+2.5%p</td></tr>
<tr><td class='l'>− 공교육</td><td>0.1607</td><td>+3.2%p</td></tr>
<tr><td class='l'>− 보상적 설계</td><td>0.1643</td><td>+5.9%p</td></tr>
</table>
<p>자본소유·배당 환류를 제거하면 양극화가 가장 크게 악화(0.164→0.190)되어 <b class='k'>AI 자본소유의 광범위화가 양극화 완화의 주력 메커니즘</b>임을 보인다. 반면 교육·돌봄 제거는 취약계층 고용 개선을 절반가량 줄이면서 양극화는 거의 바꾸지 않아, <b class='k'>교육·돌봄이 고용 포용의 주력 메커니즘</b>임을 보인다. 나아가 시장 대 종합안의 순서는 표본크기 250~2,000에서 안정적이어서 소표본 아티팩트가 아니다.</p>

<h4 class='sec'>2. 정책 논의와 결론</h4>
<h5 class='sub'>(1) ‘모두의 AI’ 설계 제언</h5>
<p>본 분석은 진행 중인 국가정책에 직접 적용된다. ‘AI 미사용 3분의 1’은 저학력·비경제활동 계층과 겹치며, 이들에게 무료 챗봇만으로는 순후생이 오르지 않았다. 따라서 성패는 챗봇 출시가 아니라 보상적 설계에 달려 있다. 구체적으로 (i) 저역량층 우선 <b class='k'>AI 활용 공교육</b>(수료가 아니라 무보조 재현역량으로 측정), (ii) <b class='k'>돌봄·행정 부담 경감</b>으로 학습·구직 시간 확보, (iii) 연금·근로자 지분·지역 컴퓨트 기금 등 <b class='k'>시민의 AI 자본 청구권</b> 확대를 결합해야 한다. 정책 평가 지표도 이용률이 아니라 양극화·역량격차·취약계층 고용·권리의 공동 통과조건으로 전환할 것을 제언한다.</p>
<h5 class='sub'>(2) 한계와 결론</h5>
<p>본 모형은 부분균형이며 임금·가격이 균형에서 청산되지 않고, 정책 품질·신뢰는 가정이며, 합성 인구의 결합분포 대표성은 감사되지 않았다. 따라서 본 연구는 이론 보조 정책 설계로 읽혀야 하며 실제 프로그램을 서열화하지 않는다. 그럼에도 <b class='k'>공식 산업통계로 파라미터를 보정</b>했을 때에도 “보편 접근만으로는 양극화를 되돌리지 못하고, 자본소유·교육·돌봄의 결합이 필요하다”는 결론이 강건하게 유지된다는 점은 정책적으로 유의미하다. 산업통계를 정책 시뮬레이션의 파라미터로 직접 활용하는 본 접근은, 예산 투입 전에 실패 조합을 식별하고 산업통계의 정책 활용도를 높이는 방법을 제시한다.</p>
"""

REFS = """
<h3 class='ch'>참고문헌</h3>
<div class='refs'>
<p>한국은행(2025), 「인공지능의 노동시장 및 생산성 파급 효과」, 한국은행.</p>
<p>과학기술정보통신부(2026), “‘모두의 AI’ 프로젝트 추진계획”, 6월.</p>
<p>산업연구원, ISTANS 산업통계분석시스템, https://www.istans.or.kr(접속일: 2026. 8. 29).</p>
<p>Acemoglu, D. and P. Restrepo(2021), “Tasks, Automation, and the Rise in U.S. Wage Inequality”, <i>Econometrica</i>, Econometric Society.</p>
<p>Autor, D.(2015), “Why Are There Still So Many Jobs? The History and Future of Workplace Automation”, <i>Journal of Economic Perspectives</i>, 29(3), American Economic Association, pp. 3-30.</p>
<p>Brynjolfsson, E., D. Li, and L. Raymond(2023), “Generative AI at Work”, NBER Working Paper.</p>
<p>Korinek, A. and J. Stiglitz(2019), “Artificial Intelligence and Its Implications for Income Distribution and Unemployment”, in <i>The Economics of Artificial Intelligence</i>, University of Chicago Press.</p>
<p>Rockall, E. et al.(2025), <i>The Labor Market Impact of Artificial Intelligence</i>, International Monetary Fund.</p>
<p>OECD(2026), <i>Government at a Glance: AI</i>, OECD Publishing.</p>
<p>통계청, KOSIS 국가통계포털 OpenAPI, https://kosis.kr(접속일: 2026. 8. 29).</p>
<p>한국은행, ECOS 경제통계시스템 OpenAPI, https://ecos.bok.or.kr(접속일: 2026. 8. 29).</p>
<p>NVIDIA(2026), Nemotron-Personas-Korea Dataset (CC BY 4.0), https://huggingface.co/datasets/nvidia/Nemotron-Personas-Korea(접속일: 2026. 8. 29).</p>
</div>
<p class='src' style='margin-top:4mm'>※ 재현 코드·데이터·인터랙티브 시뮬레이터: https://github.com/waterfirst/public-ai-inequality-economics · https://waterfirst.github.io/public-ai-inequality-economics/</p>
"""

HTML = f"<!doctype html><html><head><meta charset='utf-8'>{CSS}</head><body>{COVER}{SUMMARY}<div class='pagebreak'></div>{TOC}<div class='pagebreak'></div>{CH1}{CH2}{CH3}{REFS}</body></html>"

path = os.path.join(OUT, "ISTANS_논문경진대회_논문_최낙초.pdf")
with sync_playwright() as p:
    b = p.chromium.launch(headless=True); pg = b.new_page()
    pg.set_content(HTML, wait_until="networkidle"); pg.wait_for_timeout(800)
    pg.pdf(path=path, format="A4", print_background=True,
           margin={"top":"20mm","bottom":"18mm","left":"20mm","right":"20mm"},
           display_header_footer=False)
    b.close()
print("wrote", path)
