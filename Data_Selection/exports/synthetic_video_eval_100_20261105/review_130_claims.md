# 100개 영상 합성 평가 데이터 — 검토용

원본 영상·실제 광고 발언이 아닌 JSON에 삽입한 합성 Claim의 평가 정답임.
아래 라벨은 주간 발표 기준을 적용한 작성자 정답 초안이며, 실제 A·B 출력 또는 독립 평가자 합의가 아님.

| 영상 구성 | 영상 수 |
|---|---:|
| VIOLATION 1개 추가 | 35 |
| OVERCLAIM 1개 추가 | 35 |
| 각각 1개 추가 | 10 |
| VIOLATION 2개 추가 | 10 |
| OVERCLAIM 2개 추가 | 10 |

제품 수: 1개인 영상 90편, 2개인 영상 10편. DB 제품 110개 중복 없음.
총 삽입 Claim 130개: VIOLATION 65개, OVERCLAIM 65개.

원본 Claim은 ETC 제외 후 그대로 보존함. 원본 Claim 전체는 라벨링하지 않았으므로 위 구성은 삽입 수이며 영상 전체의 실제 라벨 수가 아님.

## db_001_AKyDb1Yhaio / c70 / VIOLATION

영상 그룹: violation_1
제품: BNS혈당엔바나바 / (주)오투바이오 / DB ID 1531

BNS혈당엔바나바의 등록된 하루 섭취량은 3정이다.

**판정 근거**

같은 하루 기준에서 DB는 1정이나 Claim은 3정으로 변경함.

**DB 원문: products:1531.intake_method**

> 1일 1회, 1회 1정을 물과 함께 섭취하십시오.

## db_003_VABlVWjX9t4 / c15 / OVERCLAIM

영상 그룹: overclaim_1
제품: G4000 프로바이오틱스 / (주)충청바이오텍 / DB ID 2228

G4000 프로바이오틱스 제품은 하루 만에 장내 유해균을 99% 깨끗이 제거한다.

**판정 근거**

제품 및 원료의 인정 기능성에는 이 기간·수치·구체적 결과를 보장하는 문장이 없음. 질병 치료나 의약품 대체가 아니라, 인정 범위를 넘는 과장된 효과로 구성함. NLI 점수를 정답으로 사용하지 않으며 실제 NLI의 OVERCLAIM 출력은 별도 평가 대상임.

**DB 원문: products:2228.main_functionality**

> [프로바이오틱스]
> 유산균 증식 및 유해균 억제･배변활동 원활･장 건강에 도움을 줄 수 있음
> 
> [비타민 C]
> ①결합조직 형성과 기능유지에 필요 ②철의 흡수에 필요 ③항산화 작용을 하여 유해산소로부터 세포를 보호하는데 필요
> 
> [셀렌]
> ①유해산소로부터 세포를 보호하는데 필요
> 
> [아연]
> ①정상적인 면역기능에 필요 ②정상적인 세포분열에 필요

**DB 원문: products:2228.RAWMTRL_STD_INFO**

> [{"RCOGN_NO":"","RAWMTRL_NM":"아연","DAY_INTK_LOWLIMIT":"2.55","DAY_INTK_HIGHLIMIT":"12","INTK_UNIT":"mg","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 정상적인 면역기능에 필요\n(2) 정상적인 세포분열에 필요","IFTKN_ATNT_MATR_CN":""},{"RCOGN_NO":"","RAWMTRL_NM":"셀레늄(또는 셀렌)","DAY_INTK_LOWLIMIT":"0.0165","DAY_INTK_HIGHLIMIT":"0.135","INTK_UNIT":"mg","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 유해산소로부터 세포를 보호하는데 필요","IFTKN_ATNT_MATR_CN":""},{"RCOGN_NO":"","RAWMTRL_NM":"비타민 C","DAY_INTK_LOWLIMIT":"30","DAY_INTK_HIGHLIMIT":"1000","INTK_UNIT":"mg","INTK_MEMO":"21.7.11: 기능성 내용 변경 26.7.23 주의사항 변경","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 결합조직 형성과 기능유지에 필요\n(2) 철의 흡수에 필요\n(3) 항산화 작용을 하여 유해산소로부터 세포를 보호하는데 필요","IFTKN_ATNT_MATR_CN":"(1) 과량 섭취하지 않도록 주의할 것\n(2) 신장질환이 있는 경우 섭취 전 전문가와 상담할 것\n(3) 이상사례 발생 시 섭취를 중단하고 전문가와 상담할 것"},{"RCOGN_NO":"","RAWMTRL_NM":"프로바이오틱스","DAY_INTK_LOWLIMIT":"100000000","DAY_INTK_HIGHLIMIT":"10000000000","INTK_UNIT":"CFU","INTK_MEMO":"21.7.11: 기능성 내용 변경","SKLL_IX_IRDNT_RAWMTRL":"생균","PRIMARY_FNCLTY":"유산균 증식 및 유해균 억제･배변활동 원활･장 건강에 도움을 줄 수 있음","IFTKN_ATNT_MATR_CN":"(가) 질환이 있거나 의약품 복용 시 전문가와 상담할 것\n(나) 알레르기 체질 등은 개인에 따라 과민반응을 나타낼 수 있음\n(다) 어린이가 함부로 섭취하지 않도록 일일섭취량 방법을 지도할 것\n(라) 이상사례 발생 시 섭취를 중단하고 전문가와 상담할 것"}]

## db_005_Ehq6ZhkzjIk / c09 / OVERCLAIM

영상 그룹: overclaim_1
제품: 간에게주는밀크씨슬선물 / 주)팜크로스 / DB ID 4661

간에게주는밀크씨슬선물 제품은 한 번만 먹어도 간에 쌓인 노폐물을 깨끗이 제거한다.

**판정 근거**

제품 및 원료의 인정 기능성에는 이 기간·수치·구체적 결과를 보장하는 문장이 없음. 질병 치료나 의약품 대체가 아니라, 인정 범위를 넘는 과장된 효과로 구성함. NLI 점수를 정답으로 사용하지 않으며 실제 NLI의 OVERCLAIM 출력은 별도 평가 대상임.

**DB 원문: products:4661.main_functionality**

> ① 간 건강에 도움을 줄 수 있음

**DB 원문: products:4661.RAWMTRL_STD_INFO**

> [{"RCOGN_NO":"","RAWMTRL_NM":"밀크씨슬(카르두스 마리아누스) 추출물","DAY_INTK_LOWLIMIT":"130","DAY_INTK_HIGHLIMIT":"130","INTK_UNIT":"mg","INTK_MEMO":"(24.12.20.) 일일섭취량, 섭취시주의사항 현행화 / '24 신뢰성 확보","SKLL_IX_IRDNT_RAWMTRL":"실리마린","PRIMARY_FNCLTY":"① 간 건강에 도움을 줄 수 있음","IFTKN_ATNT_MATR_CN":"(가) 어린이, 임산부 및 수유부는 섭취를 피할 것\n(나) 알레르기 반응이 나타나는 경우에는 섭취 중단\n(다) 설사, 위통, 복부팽만 등의 위장관계 장애가 나타나는 경우에는 섭취에 주의\n(라) 이상사례 발생 시 섭취를 중단하고 전문가와 상담할 것"}]

## db_006_oUr4voFFuBo / c25 / OVERCLAIM

영상 그룹: overclaim_2
제품: 감비책 다이어트 / (주)천호엔케어 / DB ID 4769

감비책 다이어트 제품은 2주 만에 체지방 5kg을 확실히 줄인다.

**판정 근거**

제품 및 원료의 인정 기능성에는 이 기간·수치·구체적 결과를 보장하는 문장이 없음. 질병 치료나 의약품 대체가 아니라, 인정 범위를 넘는 과장된 효과로 구성함. NLI 점수를 정답으로 사용하지 않으며 실제 NLI의 OVERCLAIM 출력은 별도 평가 대상임.

**DB 원문: products:4769.main_functionality**

> [가르시니아캄보지아추출물]탄수화물이 지방으로 합성되는 것을 억제하여 체지방 감소에 도움을 줄 수 있음
> [난소화성말토덱스트린]식후 혈당상승 억제·혈중 중성지질 개선·배변활동 원활에 도움을 줄 수 있음

**DB 원문: products:4769.RAWMTRL_STD_INFO**

> [{"RCOGN_NO":"","RAWMTRL_NM":"난소화성말토덱스트린","DAY_INTK_LOWLIMIT":"4","DAY_INTK_HIGHLIMIT":"30","INTK_UNIT":"g","INTK_MEMO":"식후 혈당상승억제:난소화성말토덱스트린식이섬유로서11.9～30g,혈중중성지질개선:난소화성말토덱스트린식이섬유로서12.7～30g,배변활동원활:난소화성말토덱스트린식이섬유로서2.5～30g","SKLL_IX_IRDNT_RAWMTRL":"난소화성말토덱스트린 식이섬유","PRIMARY_FNCLTY":"(1)기능성 내용 : 식후 혈당상승 억제･혈중 중성지질 개선･배변활동 원활에 도움을 줄 수 있음\n(2) 일일섭취량\n (가)식후 혈당상승 억제에 도움을 줄 수 있음 : 난소화성말토덱스트린 식이섬유로서 4.0~30 g (액상원료는 4.0~44 g)\n (나)혈중 중성지질 개선에 도움을 줄 수 있음 : 난소화성말토덱스트린 식이섬유로서 5.0~30 g (액상원료는 5.0~44 g)\n (다)배변활동 원활에 도움을 줄 수 있음 : 난소화성말토덱스트린 식이섬유로서 4.2~30 g (액상원료는 4.2~44 g)","IFTKN_ATNT_MATR_CN":"(3) 섭취 시 주의사항\n (가)반드시 충분한 물과 함께 섭취할 것(액상제외)\n (나)이상사례 발생 시 섭취를 중단하고 전문가와 상담할 것"},{"RCOGN_NO":"","RAWMTRL_NM":"가르시니아캄보지아 추출물","DAY_INTK_LOWLIMIT":"750","DAY_INTK_HIGHLIMIT":"1500","INTK_UNIT":"mg","INTK_MEMO":"(24.12.23.) 섭취시주의사항, 일일섭취량 현행화 / '24 신뢰성 확보","SKLL_IX_IRDNT_RAWMTRL":"총(-)-Hydroxycitric acid","PRIMARY_FNCLTY":"(1) 탄수화물이 지방으로 합성되는 것을 억제하여 체지방 감소에 도움을 줄 수 있음","IFTKN_ATNT_MATR_CN":"(가) 어린이, 임산부 및 수유부는 섭취를 피할 것\n(나) 간･신장･심장질환, 알레르기 및 천식이 있거나 의약품 복용 시 전문가와 상담할 것\n(다) 남성의 경우 과다 섭취를 피할 것\n(라) 이상사례 발생 시 섭취를 중단하고 전문가와 상담할 것"}]

## db_006_oUr4voFFuBo / c26 / OVERCLAIM

영상 그룹: overclaim_2
제품: 감비책 다이어트 / (주)천호엔케어 / DB ID 4769

감비책 다이어트 제품은 식사량을 줄이지 않아도 일주일 만에 뱃살만 골라 30% 없애 준다.

**판정 근거**

제품 및 원료의 인정 기능성에는 이 기간·수치·구체적 결과를 보장하는 문장이 없음. 질병 치료나 의약품 대체가 아니라, 인정 범위를 넘는 과장된 효과로 구성함. NLI 점수를 정답으로 사용하지 않으며 실제 NLI의 OVERCLAIM 출력은 별도 평가 대상임.

**DB 원문: products:4769.main_functionality**

> [가르시니아캄보지아추출물]탄수화물이 지방으로 합성되는 것을 억제하여 체지방 감소에 도움을 줄 수 있음
> [난소화성말토덱스트린]식후 혈당상승 억제·혈중 중성지질 개선·배변활동 원활에 도움을 줄 수 있음

**DB 원문: products:4769.RAWMTRL_STD_INFO**

> [{"RCOGN_NO":"","RAWMTRL_NM":"난소화성말토덱스트린","DAY_INTK_LOWLIMIT":"4","DAY_INTK_HIGHLIMIT":"30","INTK_UNIT":"g","INTK_MEMO":"식후 혈당상승억제:난소화성말토덱스트린식이섬유로서11.9～30g,혈중중성지질개선:난소화성말토덱스트린식이섬유로서12.7～30g,배변활동원활:난소화성말토덱스트린식이섬유로서2.5～30g","SKLL_IX_IRDNT_RAWMTRL":"난소화성말토덱스트린 식이섬유","PRIMARY_FNCLTY":"(1)기능성 내용 : 식후 혈당상승 억제･혈중 중성지질 개선･배변활동 원활에 도움을 줄 수 있음\n(2) 일일섭취량\n (가)식후 혈당상승 억제에 도움을 줄 수 있음 : 난소화성말토덱스트린 식이섬유로서 4.0~30 g (액상원료는 4.0~44 g)\n (나)혈중 중성지질 개선에 도움을 줄 수 있음 : 난소화성말토덱스트린 식이섬유로서 5.0~30 g (액상원료는 5.0~44 g)\n (다)배변활동 원활에 도움을 줄 수 있음 : 난소화성말토덱스트린 식이섬유로서 4.2~30 g (액상원료는 4.2~44 g)","IFTKN_ATNT_MATR_CN":"(3) 섭취 시 주의사항\n (가)반드시 충분한 물과 함께 섭취할 것(액상제외)\n (나)이상사례 발생 시 섭취를 중단하고 전문가와 상담할 것"},{"RCOGN_NO":"","RAWMTRL_NM":"가르시니아캄보지아 추출물","DAY_INTK_LOWLIMIT":"750","DAY_INTK_HIGHLIMIT":"1500","INTK_UNIT":"mg","INTK_MEMO":"(24.12.23.) 섭취시주의사항, 일일섭취량 현행화 / '24 신뢰성 확보","SKLL_IX_IRDNT_RAWMTRL":"총(-)-Hydroxycitric acid","PRIMARY_FNCLTY":"(1) 탄수화물이 지방으로 합성되는 것을 억제하여 체지방 감소에 도움을 줄 수 있음","IFTKN_ATNT_MATR_CN":"(가) 어린이, 임산부 및 수유부는 섭취를 피할 것\n(나) 간･신장･심장질환, 알레르기 및 천식이 있거나 의약품 복용 시 전문가와 상담할 것\n(다) 남성의 경우 과다 섭취를 피할 것\n(라) 이상사례 발생 시 섭취를 중단하고 전문가와 상담할 것"}]

## db_009_l4gd8qQFSak / c20 / OVERCLAIM

영상 그룹: overclaim_1
제품: 고려은단 멀티비타민 올인원 / 고려은단 헬스케어(주) / DB ID 5216

고려은단 멀티비타민 올인원 제품은 일주일 만에 피부 수분량을 두 배로 높이는 효과가 확실하다.

**판정 근거**

제품 및 원료의 인정 기능성에는 이 기간·수치·구체적 결과를 보장하는 문장이 없음. 질병 치료나 의약품 대체가 아니라, 인정 범위를 넘는 과장된 효과로 구성함. NLI 점수를 정답으로 사용하지 않으며 실제 NLI의 OVERCLAIM 출력은 별도 평가 대상임.

**DB 원문: products:5216.main_functionality**

> [비타민A] ①어두운 곳에서 시각 적응을 위해 필요 ②피부와 점막을 형성하고 기능을 유지하는데 필요 ③상피세포의 성장과 발달에 필요
> [비타민D] ①칼슘과 인이 흡수되고 이용되는데 필요 ②뼈의 형성과 유지에 필요 ③골다공증발생 위험 감소에 도움을 줌
> [비타민E] 항산화 작용을 하여 유해산소로부터 세포를 보호하는데 필요
> [비타민K] ①정상적인 혈액응고에 필요 ②뼈의 구성에 필요
> [비타민B1] 탄수화물과 에너지 대사에 필요 
> [비타민B2] 체내 에너지 생성에 필요
> [나이아신] 체내 에너지 생성에 필요
> [판토텐산] 지방, 탄수화물, 단백질 대사와 에너지 생성에 필요
> [비타민B6] ①단백질 및 아미노산 이용에 필요 ②혈액의 호모시스테인 수준을 정상으로 유지하는데 필요
> [엽산] ①세포와 혈액생성에 필요 ②태아 신경관의 정상 발달에 필요 ③혈액의 호모시스테인 수준을 정상으로 유지하는데 필요
> [비타민B12] 정상적인 엽산 대사에 필요
> [비오틴] 지방, 탄수화물, 단백질 대사와 에너지 생성에 필요
> [비타민C] ①결합조직 형성과 기능유지에 필요 ②철의 흡수에 필요 ③항산화 작용을 하여 유해산소로부터 세포를 보호하는데 필요
> [칼슘] ①뼈와 치아 형성에 필요 ②신경과 근육 기능 유지에 필요 ③정상적인 혈액응고에 필요 ④골다공증발생 위험 감소에 도움을 줌
> [마그네슘] ①에너지 이용에 필요 ②신경과 근육 기능 유지에 필요
> [철] ①체내 산소운반과 혈액생성에 필요 ②에너지 생성에 필요
> [아연] ①정상적인 면역기능에 필요 ②정상적인 세포분열에 필요
> [구리] ①철의 운반과 이용에 필요 ②유해산소로부터 세포를 보호하는데 필요 
> [셀레늄] 유해산소로부터 세포를 보호하는데 필요
> [요오드] ①갑상선 호르몬의 합성에 필요 ②에너지 생성에 필요 ③신경발달에 필요
> [망간] ①뼈 형성에 필요 ②에너지 이용에 필요 ③유해산소로부터 세포를 보호하는데 필요
> [몰리브덴] 산화·환원 효소의 활성에 필요
> [크롬] 체내 탄수화물, 지방, 단백질 대사에 관여

**DB 원문: products:5216.RAWMTRL_STD_INFO**

> [{"RCOGN_NO":"","RAWMTRL_NM":"판토텐산","DAY_INTK_LOWLIMIT":"1.5","DAY_INTK_HIGHLIMIT":"200","INTK_UNIT":"mg","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 지방, 탄수화물, 단백질 대사와 에너지 생성에 필요","IFTKN_ATNT_MATR_CN":"(1) 이상사례 발생 시 섭취를 중단하고 전문가와 상담할 것"},{"RCOGN_NO":"","RAWMTRL_NM":"비타민 B6","DAY_INTK_LOWLIMIT":"0.45","DAY_INTK_HIGHLIMIT":"67","INTK_UNIT":"mg","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 단백질 및 아미노산 이용에 필요\n(2) 혈액의 호모시스테인 수준을 정상으로 유지하는데 필요","IFTKN_ATNT_MATR_CN":"(1) 손발 따끔거림, 작열감 또는 저림 등의 이상사례 발생 시 섭취를 중단하고 전문가와 상담할 것"},{"RCOGN_NO":"","RAWMTRL_NM":"엽산","DAY_INTK_LOWLIMIT":"120","DAY_INTK_HIGHLIMIT":"400","INTK_UNIT":"μg","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 세포와 혈액생성에 필요\n(2) 태아 신경관의 정상 발달에 필요\n(3) 혈액의 호모시스테인 수준을 정상으로 유지하는데 필요","IFTKN_ATNT_MATR_CN":""},{"RCOGN_NO":"","RAWMTRL_NM":"비타민 B12","DAY_INTK_LOWLIMIT":"0.00072","DAY_INTK_HIGHLIMIT":"2","INTK_UNIT":"mg","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 정상적인 엽산 대사에 필요","IFTKN_ATNT_MATR_CN":"(1) 이상사례 발생 시 섭취를 중단하고 전문가와 상담할 것"},{"RCOGN_NO":"","RAWMTRL_NM":"비오틴","DAY_INTK_LOWLIMIT":"0.009","DAY_INTK_HIGHLIMIT":"0.9","INTK_UNIT":"mg","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 지방, 탄수화물, 단백질 대사와 에너지 생성에 필요","IFTKN_ATNT_MATR_CN":"(1) 이상사례 발생 시 섭취를 중단하고 전문가와 상담할 것"},{"RCOGN_NO":"","RAWMTRL_NM":"비타민 C","DAY_INTK_LOWLIMIT":"30","DAY_INTK_HIGHLIMIT":"1000","INTK_UNIT":"mg","INTK_MEMO":"21.7.11: 기능성 내용 변경 26.7.23 주의사항 변경","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 결합조직 형성과 기능유지에 필요\n(2) 철의 흡수에 필요\n(3) 항산화 작용을 하여 유해산소로부터 세포를 보호하는데 필요","IFTKN_ATNT_MATR_CN":"(1) 과량 섭취하지 않도록 주의할 것\n(2) 신장질환이 있는 경우 섭취 전 전문가와 상담할 것\n(3) 이상사례 발생 시 섭취를 중단하고 전문가와 상담할 것"},{"RCOGN_NO":"","RAWMTRL_NM":"칼슘","DAY_INTK_LOWLIMIT":"210","DAY_INTK_HIGHLIMIT":"800","INTK_UNIT":"mg","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 뼈와 치아 형성에 필요\n(2) 신경과 근육 기능 유지에 필요\n(3) 정상적인 혈액응고에 필요\n(4) 골다공증발생 위험 감소에 도움을 줌","IFTKN_ATNT_MATR_CN":""},{"RCOGN_NO":"","RAWMTRL_NM":"마그네슘","DAY_INTK_LOWLIMIT":"94.5","DAY_INTK_HIGHLIMIT":"250","INTK_UNIT":"mg","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 에너지 이용에 필요\n(2) 신경과 근육 기능 유지에 필요","IFTKN_ATNT_MATR_CN":""},{"RCOGN_NO":"","RAWMTRL_NM":"철","DAY_INTK_LOWLIMIT":"3.6","DAY_INTK_HIGHLIMIT":"15","INTK_UNIT":"mg","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 체내 산소운반과 혈액생성에 필요\n(2) 에너지 생성에 필요","IFTKN_ATNT_MATR_CN":"특히 6세 이하는 과량섭취하지 않도록 주의"},{"RCOGN_NO":"","RAWMTRL_NM":"아연","DAY_INTK_LOWLIMIT":"2.55","DAY_INTK_HIGHLIMIT":"12","INTK_UNIT":"mg","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 정상적인 면역기능에 필요\n(2) 정상적인 세포분열에 필요","IFTKN_ATNT_MATR_CN":""},{"RCOGN_NO":"","RAWMTRL_NM":"구리","DAY_INTK_LOWLIMIT":"0.24","DAY_INTK_HIGHLIMIT":"7","INTK_UNIT":"mg","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 철의 운반과 이용에 필요\n(2) 유해산소로부터 세포를 보호하는데 필요","IFTKN_ATNT_MATR_CN":""},{"RCOGN_NO":"","RAWMTRL_NM":"셀레늄(또는 셀렌)","DAY_INTK_LOWLIMIT":"0.0165","DAY_INTK_HIGHLIMIT":"0.135","INTK_UNIT":"mg","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 유해산소로부터 세포를 보호하는데 필요","IFTKN_ATNT_MATR_CN":""},{"RCOGN_NO":"","RAWMTRL_NM":"요오드","DAY_INTK_LOWLIMIT":"0.045","DAY_INTK_HIGHLIMIT":"0.15","INTK_UNIT":"mg","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 갑상선 호르몬의 합성에 필요\n(2) 에너지 생성에 필요\n(3) 신경발달에 필요","IFTKN_ATNT_MATR_CN":""},{"RCOGN_NO":"","RAWMTRL_NM":"망간","DAY_INTK_LOWLIMIT":"0.9","DAY_INTK_HIGHLIMIT":"3.5","INTK_UNIT":"mg","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 뼈 형성에 필요\n(2) 에너지 이용에 필요\n(3) 유해산소로부터 세포를 보호하는데 필요","IFTKN_ATNT_MATR_CN":""},{"RCOGN_NO":"","RAWMTRL_NM":"몰리브덴","DAY_INTK_LOWLIMIT":"0.0075","DAY_INTK_HIGHLIMIT":"0.23","INTK_UNIT":"mg","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 산화·환원 효소의 활성에 필요","IFTKN_ATNT_MATR_CN":""},{"RCOGN_NO":"","RAWMTRL_NM":"크롬","DAY_INTK_LOWLIMIT":"0.009","DAY_INTK_HIGHLIMIT":"9","INTK_UNIT":"mg","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 체내 탄수화물, 지방, 단백질 대사에 관여","IFTKN_ATNT_MATR_CN":"(1) 당뇨병이 있는 경우 섭취 전 전문가와 상담할 것\n(2) 이상사례 발생 시 섭취를 중단하고 전문가와 상담할 것"},{"RCOGN_NO":"","RAWMTRL_NM":"나이아신","DAY_INTK_LOWLIMIT":"4.5","DAY_INTK_HIGHLIMIT":"670","INTK_UNIT":"mg","INTK_MEMO":"니코틴산 4.5～23 mg, 니코틴산아미드 4.5～670 mg","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 체내 에너지 생성에 필요","IFTKN_ATNT_MATR_CN":""},{"RCOGN_NO":"","RAWMTRL_NM":"비타민 B2","DAY_INTK_LOWLIMIT":"0.42","DAY_INTK_HIGHLIMIT":"40","INTK_UNIT":"mg","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 체내 에너지 생성에 필요","IFTKN_ATNT_MATR_CN":"(1) 이상사례 발생 시 섭취를 중단하고 전문가와 상담할 것"},{"RCOGN_NO":"","RAWMTRL_NM":"비타민 B1","DAY_INTK_LOWLIMIT":"0.36","DAY_INTK_HIGHLIMIT":"100","INTK_UNIT":"mg","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 탄수화물과 에너지 대사에 필요","IFTKN_ATNT_MATR_CN":"(1) 이상사례 발생 시 섭취를 중단하고 전문가와 상담할 것"},{"RCOGN_NO":"","RAWMTRL_NM":"비타민 K","DAY_INTK_LOWLIMIT":"0.021","DAY_INTK_HIGHLIMIT":"1","INTK_UNIT":"mg","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 정상적인 혈액응고에 필요\n(2) 뼈의 구성에 필요","IFTKN_ATNT_MATR_CN":"(1) 항응고제 등 복용 시 전문가와 상담할 것\n(2) 이상사례 발생 시 섭취를 중단하고 전문가와 상담할 것"},{"RCOGN_NO":"","RAWMTRL_NM":"비타민 E","DAY_INTK_LOWLIMIT":"3.3","DAY_INTK_HIGHLIMIT":"400","INTK_UNIT":"mg α-TE","INTK_MEMO":"2021.7.11: 기능성 내용 변경","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"항산화 작용을 하여 유해산소로부터 세포를 보호하는데 필요","IFTKN_ATNT_MATR_CN":""},{"RCOGN_NO":"","RAWMTRL_NM":"비타민 A","DAY_INTK_LOWLIMIT":"210","DAY_INTK_HIGHLIMIT":"1000","INTK_UNIT":"μg RAE","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 어두운 곳에서 시각 적응을 위해 필요\n(2) 피부와 점막을 형성하고 기능을 유지하는데 필요\n(3) 상피세포의 성장과 발달에 필요","IFTKN_ATNT_MATR_CN":""},{"RCOGN_NO":"","RAWMTRL_NM":"비타민 D","DAY_INTK_LOWLIMIT":"0.003","DAY_INTK_HIGHLIMIT":"0.01","INTK_UNIT":"mg","INTK_MEMO":"일일섭취량 : 3~10 μg(120∼400 IU)","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 칼슘과 인이 흡수되고 이용되는데 필요\n(2) 뼈의 형성과 유지에 필요\n(3) 골다공증발생 위험 감소에 도움을 줌","IFTKN_ATNT_MATR_CN":"(가) 고칼슘혈증이 있거나 의약품 복용 시 전문가와 상담할 것\n(나) 이상사례 발생 시 섭취를 중단하고 전문가와 상담할 것"}]

## db_013_NrsycE3cMV8 / c15 / VIOLATION

영상 그룹: violation_1_overclaim_1
제품: 고려은단 코엔자임Q10 / (주)서흥 / DB ID 5239

고려은단 코엔자임Q10 제품은 고혈압약을 대신할 수 있다.

**판정 근거**

건강 보조 기능을 질병 예방·치료 또는 의약품 대체 주장으로 바꿈. 주간 발표의 질병·의약품 주장 기준에 따른 정답임.

**DB 원문: products:5239.main_functionality**

> 코엔자임Q10 : 항산화·높은 혈압 감소에 도움을 줄 수 있음
> 비타민E : 항산화 작용을 하여 유해산소로부터 세포를 보호하는데 필요

## db_013_NrsycE3cMV8 / c16 / OVERCLAIM

영상 그룹: violation_1_overclaim_1
제품: 고려은단 코엔자임Q10 / (주)서흥 / DB ID 5239

고려은단 코엔자임Q10 제품은 일주일 만에 혈압 변동 폭을 90% 줄이는 효과가 확실하다.

**판정 근거**

제품 및 원료의 인정 기능성에는 이 기간·수치·구체적 결과를 보장하는 문장이 없음. 질병 치료나 의약품 대체가 아니라, 인정 범위를 넘는 과장된 효과로 구성함. NLI 점수를 정답으로 사용하지 않으며 실제 NLI의 OVERCLAIM 출력은 별도 평가 대상임.

**DB 원문: products:5239.main_functionality**

> 코엔자임Q10 : 항산화·높은 혈압 감소에 도움을 줄 수 있음
> 비타민E : 항산화 작용을 하여 유해산소로부터 세포를 보호하는데 필요

**DB 원문: products:5239.RAWMTRL_STD_INFO**

> [{"RCOGN_NO":"","RAWMTRL_NM":"비타민 E","DAY_INTK_LOWLIMIT":"3.3","DAY_INTK_HIGHLIMIT":"400","INTK_UNIT":"mg α-TE","INTK_MEMO":"2021.7.11: 기능성 내용 변경","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"항산화 작용을 하여 유해산소로부터 세포를 보호하는데 필요","IFTKN_ATNT_MATR_CN":""},{"RCOGN_NO":"","RAWMTRL_NM":"코엔자임Q10","DAY_INTK_LOWLIMIT":"90","DAY_INTK_HIGHLIMIT":"100","INTK_UNIT":"mg","INTK_MEMO":"(24.12.20.) 섭취시주의사항, 주된기능성 현행화 / '24 신뢰성 확보","SKLL_IX_IRDNT_RAWMTRL":"코엔자임Q10(CoenzymeQ10)","PRIMARY_FNCLTY":"(1) 기능성 내용 : 항산화･높은 혈압 감소에 도움을 줄 수 있음","IFTKN_ATNT_MATR_CN":"(가) 수유부는 섭취를 피할 것\n(나) 항응고제 복용 시 전문가와 상담할 것\n(다) 이상사례 발생 시 섭취를 중단하고 전문가와 상담할 것"}]

## db_014_E5uL0UwVQsQ / c17 / OVERCLAIM

영상 그룹: overclaim_2
제품: 고려은단비타민C1000 / 고려은단(주) / DB ID 5247

고려은단비타민C1000 제품은 일주일 만에 철 흡수율을 세 배로 높이는 효과가 확실하다.

**판정 근거**

제품 및 원료의 인정 기능성에는 이 기간·수치·구체적 결과를 보장하는 문장이 없음. 질병 치료나 의약품 대체가 아니라, 인정 범위를 넘는 과장된 효과로 구성함. NLI 점수를 정답으로 사용하지 않으며 실제 NLI의 OVERCLAIM 출력은 별도 평가 대상임.

**DB 원문: products:5247.main_functionality**

> ①결합조직 형성과 기능유지에 필요②철의 흡수에 필요③항산화 작용을 하여 유해산소로부터 세포를 보호하는데 필요

**DB 원문: products:5247.RAWMTRL_STD_INFO**

> [{"RCOGN_NO":"","RAWMTRL_NM":"비타민 C","DAY_INTK_LOWLIMIT":"30","DAY_INTK_HIGHLIMIT":"1000","INTK_UNIT":"mg","INTK_MEMO":"21.7.11: 기능성 내용 변경 26.7.23 주의사항 변경","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 결합조직 형성과 기능유지에 필요\n(2) 철의 흡수에 필요\n(3) 항산화 작용을 하여 유해산소로부터 세포를 보호하는데 필요","IFTKN_ATNT_MATR_CN":"(1) 과량 섭취하지 않도록 주의할 것\n(2) 신장질환이 있는 경우 섭취 전 전문가와 상담할 것\n(3) 이상사례 발생 시 섭취를 중단하고 전문가와 상담할 것"}]

## db_014_E5uL0UwVQsQ / c18 / OVERCLAIM

영상 그룹: overclaim_2
제품: 고려은단비타민C1000 / 고려은단(주) / DB ID 5247

고려은단비타민C1000 제품은 한 번만 먹어도 철분 이용 효율이 두 배로 높아진다.

**판정 근거**

제품 및 원료의 인정 기능성에는 이 기간·수치·구체적 결과를 보장하는 문장이 없음. 질병 치료나 의약품 대체가 아니라, 인정 범위를 넘는 과장된 효과로 구성함. NLI 점수를 정답으로 사용하지 않으며 실제 NLI의 OVERCLAIM 출력은 별도 평가 대상임.

**DB 원문: products:5247.main_functionality**

> ①결합조직 형성과 기능유지에 필요②철의 흡수에 필요③항산화 작용을 하여 유해산소로부터 세포를 보호하는데 필요

**DB 원문: products:5247.RAWMTRL_STD_INFO**

> [{"RCOGN_NO":"","RAWMTRL_NM":"비타민 C","DAY_INTK_LOWLIMIT":"30","DAY_INTK_HIGHLIMIT":"1000","INTK_UNIT":"mg","INTK_MEMO":"21.7.11: 기능성 내용 변경 26.7.23 주의사항 변경","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 결합조직 형성과 기능유지에 필요\n(2) 철의 흡수에 필요\n(3) 항산화 작용을 하여 유해산소로부터 세포를 보호하는데 필요","IFTKN_ATNT_MATR_CN":"(1) 과량 섭취하지 않도록 주의할 것\n(2) 신장질환이 있는 경우 섭취 전 전문가와 상담할 것\n(3) 이상사례 발생 시 섭취를 중단하고 전문가와 상담할 것"}]

## db_021_7cxBqUhRcXs / c23 / VIOLATION

영상 그룹: violation_1
제품: 관절선생 / (주)비오팜 / DB ID 6214

관절선생 제품은 퇴행성 관절염을 치료한다.

**판정 근거**

건강 보조 기능을 질병 예방·치료 또는 의약품 대체 주장으로 바꿈. 주간 발표의 질병·의약품 주장 기준에 따른 정답임.

**DB 원문: products:6214.main_functionality**

> [엠에스엠]
> ① 관절 및 연골건강에 도움을 줄 수 있음
> [N-아세틸글루코사민]
> ①관절 및 연골 건강에 도움을 줄 수 있음
> [칼슘]
> ①뼈와 치아 형성에 필요②신경과 근육 기능 유지에 필요③정상적인 혈액응고에 필요④골다공증발생 위험 감소에 도움을 줌

## db_022_Y6gkveTxNxc / c17 / VIOLATION

영상 그룹: violation_2
제품: 관절엔 소연골 뮤코다당단백 콘드로이친 골드 / 코스맥스바이오(주) / DB ID 6307

관절엔 소연골 뮤코다당단백 콘드로이친 골드 제품은 퇴행성 관절염을 치료한다.

**판정 근거**

건강 보조 기능을 질병 예방·치료 또는 의약품 대체 주장으로 바꿈. 주간 발표의 질병·의약품 주장 기준에 따른 정답임.

**DB 원문: products:6307.main_functionality**

> 1) 뮤코다당·단백 : 관절 및 연골건강에 도움을 줄 수 있음.
> 2) 비타민D : 칼슘과 인이 흡수되고 이용되는데 필요, 뼈의 형성과 유지에 필요, 골다공증발생 위험 감소에 도움을 줌.
> 3) 망간 : 뼈 형성에 필요, 에너지 이용에 필요, 유해산소로부터 세포를 보호하는데 필요.

## db_022_Y6gkveTxNxc / c18 / VIOLATION

영상 그룹: violation_2
제품: 관절엔 소연골 뮤코다당단백 콘드로이친 골드 / 코스맥스바이오(주) / DB ID 6307

관절엔 소연골 뮤코다당단백 콘드로이친 골드의 소비기한은 제조일로부터 36개월이다.

**판정 근거**

DB의 제조일 기준 24개월을 같은 기준의 36개월로 변경함.

**DB 원문: products:6307.shelf_life**

> 제조일로부터 2년

## db_023_Cf6dBCMBMmE / c11 / OVERCLAIM

영상 그룹: overclaim_1
제품: 관절엔 아나파랙틴 정제 / 광동헬스바이오(주) 2공장 / DB ID 6324

관절엔 아나파랙틴 정제 제품은 일주일 만에 관절 유연성을 두 배로 높이는 효과가 확실하다.

**판정 근거**

제품 및 원료의 인정 기능성에는 이 기간·수치·구체적 결과를 보장하는 문장이 없음. 질병 치료나 의약품 대체가 아니라, 인정 범위를 넘는 과장된 효과로 구성함. NLI 점수를 정답으로 사용하지 않으며 실제 NLI의 OVERCLAIM 출력은 별도 평가 대상임.

**DB 원문: products:6324.main_functionality**

> [천심련추출물(ParActin®)(제2022-37호)]
> (국문) 관절 건강에 도움을 줄 수 있음
> (영문) May help to maintain healthy joint 
> [비타민D] ①칼슘과 인이 흡수되고 이용되는데 필요 ②뼈의 형성과 유지에 필요 ③골다공증발생 위험 감소에 도움을 줌
> [비타민K] ①정상적인 혈액응고에 필요 ②뼈의 구성에 필요

**DB 원문: products:6324.RAWMTRL_STD_INFO**

> [{"RCOGN_NO":"","RAWMTRL_NM":"비타민 K","DAY_INTK_LOWLIMIT":"0.021","DAY_INTK_HIGHLIMIT":"1","INTK_UNIT":"mg","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 정상적인 혈액응고에 필요\n(2) 뼈의 구성에 필요","IFTKN_ATNT_MATR_CN":"(1) 항응고제 등 복용 시 전문가와 상담할 것\n(2) 이상사례 발생 시 섭취를 중단하고 전문가와 상담할 것"},{"RCOGN_NO":"","RAWMTRL_NM":"비타민 D","DAY_INTK_LOWLIMIT":"0.003","DAY_INTK_HIGHLIMIT":"0.01","INTK_UNIT":"mg","INTK_MEMO":"일일섭취량 : 3~10 μg(120∼400 IU)","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 칼슘과 인이 흡수되고 이용되는데 필요\n(2) 뼈의 형성과 유지에 필요\n(3) 골다공증발생 위험 감소에 도움을 줌","IFTKN_ATNT_MATR_CN":"(가) 고칼슘혈증이 있거나 의약품 복용 시 전문가와 상담할 것\n(나) 이상사례 발생 시 섭취를 중단하고 전문가와 상담할 것"},{"RCOGN_NO":"2022-37","RAWMTRL_NM":"천심련추출물(ParActinⓇ)(제2022-37호)","DAY_INTK_LOWLIMIT":"300","DAY_INTK_HIGHLIMIT":"300","INTK_UNIT":"mg/일","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"안드로그라폴라이드(Andrographolide)","PRIMARY_FNCLTY":"(국문) 관절 건강에 도움을 줄 수 있음\n(영문) May help to maintain healthy joint","IFTKN_ATNT_MATR_CN":"(1) 영·유아, 어린이, 청소년, 임산부 및 수유부, 임신을 계획하고 있는 자는 섭취하지 말 것\n(2) 특정질환(알레르기 체질 등)이 있는 분은 섭취에 주의\n(3) 이상사례 발생 시 섭취를 중단하고 전문가와 상담할 것\n(4) 의약품을 복용하시는 분은 섭취 전 전문의와 상담할 것"}]

## db_027_V5k04vnSlJo / c14 / VIOLATION

영상 그룹: violation_1
제품: 관절연골엔 구절초 / (주)알피바이오 / DB ID 6407

관절연골엔 구절초 제품은 퇴행성 관절염을 치료한다.

**판정 근거**

건강 보조 기능을 질병 예방·치료 또는 의약품 대체 주장으로 바꿈. 주간 발표의 질병·의약품 주장 기준에 따른 정답임.

**DB 원문: products:6407.main_functionality**

> (국문) 관절 및 연골 건강에 도움을 줄 수 있음
> (영문) May help to maintain healthy joint and cartilage

## db_035_y_0fmF3xgck / c18 / VIOLATION

영상 그룹: violation_1
제품: 관절연골엔보스웰리아 / 주식회사 노바렉스 / DB ID 6478

관절연골엔보스웰리아의 등록된 하루 섭취량은 4정이다.

**판정 근거**

같은 하루 기준에서 DB는 2정이나 Claim은 4정으로 변경함.

**DB 원문: products:6478.intake_method**

> 1일 1회, 1회 2정(1정당 850mg)을 충분한 물과 함께 섭취하십시오.

## db_039_zptASsSd0nY / c11 / VIOLATION

영상 그룹: violation_2
제품: 관절팔팔 / (주)씨스팡 / DB ID 6569

관절팔팔 제품은 퇴행성 관절염을 치료한다.

**판정 근거**

건강 보조 기능을 질병 예방·치료 또는 의약품 대체 주장으로 바꿈. 주간 발표의 질병·의약품 주장 기준에 따른 정답임.

**DB 원문: products:6569.main_functionality**

> 관절건강에 도움을 줄 수 있음.

## db_039_zptASsSd0nY / c12 / VIOLATION

영상 그룹: violation_2
제품: 혈관팔팔 / (주)씨스팡 / DB ID 43407

혈관팔팔 제품은 혈전증을 치료한다.

**판정 근거**

건강 보조 기능을 질병 예방·치료 또는 의약품 대체 주장으로 바꿈. 주간 발표의 질병·의약품 주장 기준에 따른 정답임.

**DB 원문: products:43407.main_functionality**

> -산화스트레스로부터 인체를 보호하는데 도움을 줄 수 있습니다.
> -혈관벽 두께(내중막 두께 : IMT) 증가 억제를 통한 혈행개선에 도움을 줄 수 있음
> -자외선에 의한 피부홍반개선으로 피부건강에 도움을 줄 수 있음

## db_040_1dcPKN8GH8Y / c24 / VIOLATION

영상 그룹: violation_1
제품: 그린요오드 / (주)비오팜 / DB ID 7168

그린요오드의 등록된 하루 섭취량은 3정이다.

**판정 근거**

같은 하루 기준에서 DB는 1정이나 Claim은 3정으로 변경함.

**DB 원문: products:7168.intake_method**

> 1일 1회, 1회 1정을 물과 함께 섭취하십시오.

## db_041_csK3fHk-MRw / c08 / VIOLATION

영상 그룹: violation_1_overclaim_1
제품: 나우그린 간 건강 프리미엄 밀크씨슬 / 동서바이오팜(주) 안성공장 / DB ID 7816

나우그린 간 건강 프리미엄 밀크씨슬 제품은 간염을 치료한다.

**판정 근거**

건강 보조 기능을 질병 예방·치료 또는 의약품 대체 주장으로 바꿈. 주간 발표의 질병·의약품 주장 기준에 따른 정답임.

**DB 원문: products:7816.main_functionality**

> [밀크씨슬 추출물]간 건강에 도움을 줄 수 있음
> 
> [나이아신]체내 에너지 생성에 필요
> 
> [판토텐산]지방, 탄수화물, 단백질 대사와 에너지 생성에 필요
> 
> [비타민B6]①단백질 및 아미노산 이용에 필요②혈액의 호모시스테인 수준을 정상으로 유지하는데 필요
> 
> [비타민B1]탄수화물과 에너지 대사에 필요
> 
> [비타민B2]체내 에너지 생성에 필요

## db_041_csK3fHk-MRw / c09 / OVERCLAIM

영상 그룹: violation_1_overclaim_1
제품: 나우그린 간 건강 프리미엄 밀크씨슬 / 동서바이오팜(주) 안성공장 / DB ID 7816

나우그린 간 건강 프리미엄 밀크씨슬 제품은 한 번만 먹어도 간에 쌓인 노폐물을 깨끗이 제거한다.

**판정 근거**

제품 및 원료의 인정 기능성에는 이 기간·수치·구체적 결과를 보장하는 문장이 없음. 질병 치료나 의약품 대체가 아니라, 인정 범위를 넘는 과장된 효과로 구성함. NLI 점수를 정답으로 사용하지 않으며 실제 NLI의 OVERCLAIM 출력은 별도 평가 대상임.

**DB 원문: products:7816.main_functionality**

> [밀크씨슬 추출물]간 건강에 도움을 줄 수 있음
> 
> [나이아신]체내 에너지 생성에 필요
> 
> [판토텐산]지방, 탄수화물, 단백질 대사와 에너지 생성에 필요
> 
> [비타민B6]①단백질 및 아미노산 이용에 필요②혈액의 호모시스테인 수준을 정상으로 유지하는데 필요
> 
> [비타민B1]탄수화물과 에너지 대사에 필요
> 
> [비타민B2]체내 에너지 생성에 필요

**DB 원문: products:7816.RAWMTRL_STD_INFO**

> [{"RCOGN_NO":"","RAWMTRL_NM":"밀크씨슬(카르두스 마리아누스) 추출물","DAY_INTK_LOWLIMIT":"130","DAY_INTK_HIGHLIMIT":"130","INTK_UNIT":"mg","INTK_MEMO":"(24.12.20.) 일일섭취량, 섭취시주의사항 현행화 / '24 신뢰성 확보","SKLL_IX_IRDNT_RAWMTRL":"실리마린","PRIMARY_FNCLTY":"① 간 건강에 도움을 줄 수 있음","IFTKN_ATNT_MATR_CN":"(가) 어린이, 임산부 및 수유부는 섭취를 피할 것\n(나) 알레르기 반응이 나타나는 경우에는 섭취 중단\n(다) 설사, 위통, 복부팽만 등의 위장관계 장애가 나타나는 경우에는 섭취에 주의\n(라) 이상사례 발생 시 섭취를 중단하고 전문가와 상담할 것"},{"RCOGN_NO":"","RAWMTRL_NM":"나이아신","DAY_INTK_LOWLIMIT":"4.5","DAY_INTK_HIGHLIMIT":"670","INTK_UNIT":"mg","INTK_MEMO":"니코틴산 4.5～23 mg, 니코틴산아미드 4.5～670 mg","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 체내 에너지 생성에 필요","IFTKN_ATNT_MATR_CN":""},{"RCOGN_NO":"","RAWMTRL_NM":"판토텐산","DAY_INTK_LOWLIMIT":"1.5","DAY_INTK_HIGHLIMIT":"200","INTK_UNIT":"mg","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 지방, 탄수화물, 단백질 대사와 에너지 생성에 필요","IFTKN_ATNT_MATR_CN":"(1) 이상사례 발생 시 섭취를 중단하고 전문가와 상담할 것"},{"RCOGN_NO":"","RAWMTRL_NM":"비타민 B6","DAY_INTK_LOWLIMIT":"0.45","DAY_INTK_HIGHLIMIT":"67","INTK_UNIT":"mg","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 단백질 및 아미노산 이용에 필요\n(2) 혈액의 호모시스테인 수준을 정상으로 유지하는데 필요","IFTKN_ATNT_MATR_CN":"(1) 손발 따끔거림, 작열감 또는 저림 등의 이상사례 발생 시 섭취를 중단하고 전문가와 상담할 것"},{"RCOGN_NO":"","RAWMTRL_NM":"비타민 B1","DAY_INTK_LOWLIMIT":"0.36","DAY_INTK_HIGHLIMIT":"100","INTK_UNIT":"mg","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 탄수화물과 에너지 대사에 필요","IFTKN_ATNT_MATR_CN":"(1) 이상사례 발생 시 섭취를 중단하고 전문가와 상담할 것"},{"RCOGN_NO":"","RAWMTRL_NM":"비타민 B2","DAY_INTK_LOWLIMIT":"0.42","DAY_INTK_HIGHLIMIT":"40","INTK_UNIT":"mg","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 체내 에너지 생성에 필요","IFTKN_ATNT_MATR_CN":"(1) 이상사례 발생 시 섭취를 중단하고 전문가와 상담할 것"}]

## db_045_kzP_81Cub6Y / c08 / OVERCLAIM

영상 그룹: overclaim_1
제품: 뇌보 / (주)휴온스엔 / DB ID 8341

뇌보 제품은 3일 만에 면역세포 활성도를 세 배로 높이는 효과가 확실하다.

**판정 근거**

제품 및 원료의 인정 기능성에는 이 기간·수치·구체적 결과를 보장하는 문장이 없음. 질병 치료나 의약품 대체가 아니라, 인정 범위를 넘는 과장된 효과로 구성함. NLI 점수를 정답으로 사용하지 않으며 실제 NLI의 OVERCLAIM 출력은 별도 평가 대상임.

**DB 원문: products:8341.main_functionality**

> ①면역력 증진·피로개선에 도움을 줄 수 있음
> ·
> ②혈소판 응집억제를 통한 혈액흐름·기억력 개선·항산화에 도움을 줄 수 있음

**DB 원문: products:8341.RAWMTRL_STD_INFO**

> [{"RCOGN_NO":"","RAWMTRL_NM":"홍삼","DAY_INTK_LOWLIMIT":"2.4","DAY_INTK_HIGHLIMIT":"80","INTK_UNIT":"mg","INTK_MEMO":"면역력증진·피로개선:진세노사이드Rg1,Rb1및Rg3의합계로서3～80mg,혈소판응집억제를 통한 혈액흐름·기억력 개선·항산화:진세노사이드Rg1,Rb1및Rg3의합계로서2.4～80mg,갱년기여성의 건강:진세노사이드Rg1,Rb1및Rg3의합계로서25∼80mg","SKLL_IX_IRDNT_RAWMTRL":"진세노사이드 Rg1, Rb1 및 Rg3 의 합","PRIMARY_FNCLTY":"(1)기능성 내용 : 면역력 증진･피로개선･혈소판 응집억제를 통한 혈액흐름･기억력 개선･항산화･갱년기 여성의 건강에 도움을 줄 수 있음\n(2) 일일섭취량\n (가)면역력 증진･피로개선에 도움을 줄 수 있음 : 진세노사이드 Rg1, Rb1 및 Rg3의 합계로서 3~80 mg\n (나)혈소판 응집억제를 통한 혈액흐름･기억력 개선･항산화에 도움을 줄 수 있음 : 진세노사이드 Rg1, Rb1 및 Rg3의 합계로서 2.4~80 mg\n (다)갱년기 여성의 건강에 도움을 줄 수 있음 : 진세노사이드 Rg1, Rb1 및 Rg3의 합계로서 25~80 mg","IFTKN_ATNT_MATR_CN":"(3) 섭취 시 주의사항 \n (가)당뇨치료제 및 혈액항응고제 복용 시 섭취에 주의\n (나)알레르기 체질 등은 개인에 따라 과민반응을 나타낼 수 있음\n (다)이상사례 발생 시 섭취를 중단하고 전문가와 상담할 것"}]

## db_049_P-YTAviQgIM / c27 / OVERCLAIM

영상 그룹: overclaim_1
제품: 데이팩 올인원 / 콜마비앤에이치(주)음성공장 / DB ID 11268

데이팩 올인원 제품은 단 하루 만에 눈의 피로를 90%까지 확실히 줄인다.

**판정 근거**

제품 및 원료의 인정 기능성에는 이 기간·수치·구체적 결과를 보장하는 문장이 없음. 질병 치료나 의약품 대체가 아니라, 인정 범위를 넘는 과장된 효과로 구성함. NLI 점수를 정답으로 사용하지 않으며 실제 NLI의 OVERCLAIM 출력은 별도 평가 대상임.

**DB 원문: products:11268.main_functionality**

> - 마리골드꽃추출물 : 노화로 인해 감소될 수 있는 황반색소밀도를 유지하여 눈 건강에 도움을 줄 수 있음
> - 프로바이오틱스 : 유산균 증식 및 유해균 억제･배변활동 원활･장 건강에 도움을 줄 수 있음
> - EPA 및 DHA 함유 유지 : 혈중 중성지질 개선･혈행 개선에 도움을 줄 수 있음
> - 비타민A : 어두운 곳에서 시각 적응을 위해 필요, 피부와 점막을 형성하고 기능을 유지하는데 필요, 상피세포의 성장과 발달에 필요
> - 비타민B1 : 탄수화물과 에너지 대사에 필요
> - 비타민B2 : 체내 에너지 생성에 필요
> - 비타민B6 : 단백질 및 아미노산 이용에 필요, 혈액의 호모시스테인 수준을 정상으로 유지하는데 필요
> - 비타민B12 : 정상적인 엽산 대사에 필요
> - 비타민C : 결합조직 형성과 기능유지에 필요, 철의 흡수에 필요, 항산화 작용을 하여 유해산소로부터 세포를 보호하는데 필요
> - 비타민D : 칼슘과 인이 흡수되고 이용되는데 필요, 뼈의 형성과 유지에 필요, 골다공증발생 위험 감소에 도움을 줌
> - 비타민E : 항산화 작용을 하여 유해산소로부터 세포를 보호하는데 필요
> - 비타민K : 정상적인 혈액응고에 필요, 뼈의 구성에 필요
> - 나이아신 : 체내 에너지 생성에 필요
> - 판토텐산 : 지방, 탄수화물, 단백질 대사와 에너지 생성에 필요
> - 엽산 : 세포와 혈액생성에 필요, 태아 신경관의 정상 발달에 필요, 혈액의 호모시스테인 수준을 정상으로 유지하는데 필요
> - 비오틴 : 지방, 탄수화물, 단백질 대사와 에너지 생성에 필요
> - 철 : 체내 산소운반과 혈액생성에 필요, 에너지 생성에 필요
> - 아연 : 정상적인 면역기능에 필요, 정상적인 세포분열에 필요
> - 구리 : 철의 운반과 이용에 필요, 유해산소로부터 세포를 보호하는데 필요
> - 셀렌 : 유해산소로부터 세포를 보호하는데 필요
> - 요오드 : 갑상선 호르몬의 합성에 필요, 에너지 생성에 필요, 신경발달에 필요
> - 망간 : 뼈 형성에 필요, 에너지 이용에 필요, 유해산소로부터 세포를 보호하는데 필요
> - 몰리브덴 : 산화･환원 효소의 활성에 필요
> - 크롬 : 체내 탄수화물, 지방, 단백질 대사에 관여

**DB 원문: products:11268.RAWMTRL_STD_INFO**

> [{"RCOGN_NO":"","RAWMTRL_NM":"크롬","DAY_INTK_LOWLIMIT":"0.009","DAY_INTK_HIGHLIMIT":"9","INTK_UNIT":"mg","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 체내 탄수화물, 지방, 단백질 대사에 관여","IFTKN_ATNT_MATR_CN":"(1) 당뇨병이 있는 경우 섭취 전 전문가와 상담할 것\n(2) 이상사례 발생 시 섭취를 중단하고 전문가와 상담할 것"},{"RCOGN_NO":"","RAWMTRL_NM":"몰리브덴","DAY_INTK_LOWLIMIT":"0.0075","DAY_INTK_HIGHLIMIT":"0.23","INTK_UNIT":"mg","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 산화·환원 효소의 활성에 필요","IFTKN_ATNT_MATR_CN":""},{"RCOGN_NO":"","RAWMTRL_NM":"망간","DAY_INTK_LOWLIMIT":"0.9","DAY_INTK_HIGHLIMIT":"3.5","INTK_UNIT":"mg","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 뼈 형성에 필요\n(2) 에너지 이용에 필요\n(3) 유해산소로부터 세포를 보호하는데 필요","IFTKN_ATNT_MATR_CN":""},{"RCOGN_NO":"","RAWMTRL_NM":"요오드","DAY_INTK_LOWLIMIT":"0.045","DAY_INTK_HIGHLIMIT":"0.15","INTK_UNIT":"mg","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 갑상선 호르몬의 합성에 필요\n(2) 에너지 생성에 필요\n(3) 신경발달에 필요","IFTKN_ATNT_MATR_CN":""},{"RCOGN_NO":"","RAWMTRL_NM":"셀레늄(또는 셀렌)","DAY_INTK_LOWLIMIT":"0.0165","DAY_INTK_HIGHLIMIT":"0.135","INTK_UNIT":"mg","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 유해산소로부터 세포를 보호하는데 필요","IFTKN_ATNT_MATR_CN":""},{"RCOGN_NO":"","RAWMTRL_NM":"구리","DAY_INTK_LOWLIMIT":"0.24","DAY_INTK_HIGHLIMIT":"7","INTK_UNIT":"mg","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 철의 운반과 이용에 필요\n(2) 유해산소로부터 세포를 보호하는데 필요","IFTKN_ATNT_MATR_CN":""},{"RCOGN_NO":"","RAWMTRL_NM":"아연","DAY_INTK_LOWLIMIT":"2.55","DAY_INTK_HIGHLIMIT":"12","INTK_UNIT":"mg","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 정상적인 면역기능에 필요\n(2) 정상적인 세포분열에 필요","IFTKN_ATNT_MATR_CN":""},{"RCOGN_NO":"","RAWMTRL_NM":"철","DAY_INTK_LOWLIMIT":"3.6","DAY_INTK_HIGHLIMIT":"15","INTK_UNIT":"mg","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 체내 산소운반과 혈액생성에 필요\n(2) 에너지 생성에 필요","IFTKN_ATNT_MATR_CN":"특히 6세 이하는 과량섭취하지 않도록 주의"},{"RCOGN_NO":"","RAWMTRL_NM":"비오틴","DAY_INTK_LOWLIMIT":"0.009","DAY_INTK_HIGHLIMIT":"0.9","INTK_UNIT":"mg","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 지방, 탄수화물, 단백질 대사와 에너지 생성에 필요","IFTKN_ATNT_MATR_CN":"(1) 이상사례 발생 시 섭취를 중단하고 전문가와 상담할 것"},{"RCOGN_NO":"","RAWMTRL_NM":"엽산","DAY_INTK_LOWLIMIT":"120","DAY_INTK_HIGHLIMIT":"400","INTK_UNIT":"μg","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 세포와 혈액생성에 필요\n(2) 태아 신경관의 정상 발달에 필요\n(3) 혈액의 호모시스테인 수준을 정상으로 유지하는데 필요","IFTKN_ATNT_MATR_CN":""},{"RCOGN_NO":"","RAWMTRL_NM":"판토텐산","DAY_INTK_LOWLIMIT":"1.5","DAY_INTK_HIGHLIMIT":"200","INTK_UNIT":"mg","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 지방, 탄수화물, 단백질 대사와 에너지 생성에 필요","IFTKN_ATNT_MATR_CN":"(1) 이상사례 발생 시 섭취를 중단하고 전문가와 상담할 것"},{"RCOGN_NO":"","RAWMTRL_NM":"나이아신","DAY_INTK_LOWLIMIT":"4.5","DAY_INTK_HIGHLIMIT":"670","INTK_UNIT":"mg","INTK_MEMO":"니코틴산 4.5～23 mg, 니코틴산아미드 4.5～670 mg","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 체내 에너지 생성에 필요","IFTKN_ATNT_MATR_CN":""},{"RCOGN_NO":"","RAWMTRL_NM":"비타민 K","DAY_INTK_LOWLIMIT":"0.021","DAY_INTK_HIGHLIMIT":"1","INTK_UNIT":"mg","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 정상적인 혈액응고에 필요\n(2) 뼈의 구성에 필요","IFTKN_ATNT_MATR_CN":"(1) 항응고제 등 복용 시 전문가와 상담할 것\n(2) 이상사례 발생 시 섭취를 중단하고 전문가와 상담할 것"},{"RCOGN_NO":"","RAWMTRL_NM":"비타민 E","DAY_INTK_LOWLIMIT":"3.3","DAY_INTK_HIGHLIMIT":"400","INTK_UNIT":"mg α-TE","INTK_MEMO":"2021.7.11: 기능성 내용 변경","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"항산화 작용을 하여 유해산소로부터 세포를 보호하는데 필요","IFTKN_ATNT_MATR_CN":""},{"RCOGN_NO":"","RAWMTRL_NM":"비타민 D","DAY_INTK_LOWLIMIT":"0.003","DAY_INTK_HIGHLIMIT":"0.01","INTK_UNIT":"mg","INTK_MEMO":"일일섭취량 : 3~10 μg(120∼400 IU)","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 칼슘과 인이 흡수되고 이용되는데 필요\n(2) 뼈의 형성과 유지에 필요\n(3) 골다공증발생 위험 감소에 도움을 줌","IFTKN_ATNT_MATR_CN":"(가) 고칼슘혈증이 있거나 의약품 복용 시 전문가와 상담할 것\n(나) 이상사례 발생 시 섭취를 중단하고 전문가와 상담할 것"},{"RCOGN_NO":"","RAWMTRL_NM":"비타민 C","DAY_INTK_LOWLIMIT":"30","DAY_INTK_HIGHLIMIT":"1000","INTK_UNIT":"mg","INTK_MEMO":"21.7.11: 기능성 내용 변경 26.7.23 주의사항 변경","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 결합조직 형성과 기능유지에 필요\n(2) 철의 흡수에 필요\n(3) 항산화 작용을 하여 유해산소로부터 세포를 보호하는데 필요","IFTKN_ATNT_MATR_CN":"(1) 과량 섭취하지 않도록 주의할 것\n(2) 신장질환이 있는 경우 섭취 전 전문가와 상담할 것\n(3) 이상사례 발생 시 섭취를 중단하고 전문가와 상담할 것"},{"RCOGN_NO":"","RAWMTRL_NM":"비타민 B12","DAY_INTK_LOWLIMIT":"0.00072","DAY_INTK_HIGHLIMIT":"2","INTK_UNIT":"mg","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 정상적인 엽산 대사에 필요","IFTKN_ATNT_MATR_CN":"(1) 이상사례 발생 시 섭취를 중단하고 전문가와 상담할 것"},{"RCOGN_NO":"","RAWMTRL_NM":"비타민 B6","DAY_INTK_LOWLIMIT":"0.45","DAY_INTK_HIGHLIMIT":"67","INTK_UNIT":"mg","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 단백질 및 아미노산 이용에 필요\n(2) 혈액의 호모시스테인 수준을 정상으로 유지하는데 필요","IFTKN_ATNT_MATR_CN":"(1) 손발 따끔거림, 작열감 또는 저림 등의 이상사례 발생 시 섭취를 중단하고 전문가와 상담할 것"},{"RCOGN_NO":"","RAWMTRL_NM":"비타민 B2","DAY_INTK_LOWLIMIT":"0.42","DAY_INTK_HIGHLIMIT":"40","INTK_UNIT":"mg","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 체내 에너지 생성에 필요","IFTKN_ATNT_MATR_CN":"(1) 이상사례 발생 시 섭취를 중단하고 전문가와 상담할 것"},{"RCOGN_NO":"","RAWMTRL_NM":"비타민 B1","DAY_INTK_LOWLIMIT":"0.36","DAY_INTK_HIGHLIMIT":"100","INTK_UNIT":"mg","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 탄수화물과 에너지 대사에 필요","IFTKN_ATNT_MATR_CN":"(1) 이상사례 발생 시 섭취를 중단하고 전문가와 상담할 것"},{"RCOGN_NO":"","RAWMTRL_NM":"비타민 A","DAY_INTK_LOWLIMIT":"210","DAY_INTK_HIGHLIMIT":"1000","INTK_UNIT":"μg RAE","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 어두운 곳에서 시각 적응을 위해 필요\n(2) 피부와 점막을 형성하고 기능을 유지하는데 필요\n(3) 상피세포의 성장과 발달에 필요","IFTKN_ATNT_MATR_CN":""},{"RCOGN_NO":"","RAWMTRL_NM":"EPA 및 DHA 함유 유지","DAY_INTK_LOWLIMIT":"0.5","DAY_INTK_HIGHLIMIT":"2.24","INTK_UNIT":"g","INTK_MEMO":"건강기능식품의 기준 및 규격 2-16","SKLL_IX_IRDNT_RAWMTRL":"EPA와 DHA","PRIMARY_FNCLTY":"(1) 기능성 내용 : 혈중 중성지질 개선･혈행 개선･기억력 개선･건조한 눈을 개선하여 눈 건강에 도움을 줄 수 있음","IFTKN_ATNT_MATR_CN":"(가) 의약품(항응고제, 항혈소판제, 혈압강하제 등) 복용 시 전문가와 상담할 것\n(나) 개인에 따라 피부 관련 이상반응이 발생할 수 있음\n(다) 이상사례 발생 시 섭취를 중단하고 전문가와 상담할 것"},{"RCOGN_NO":"","RAWMTRL_NM":"프로바이오틱스","DAY_INTK_LOWLIMIT":"100000000","DAY_INTK_HIGHLIMIT":"10000000000","INTK_UNIT":"CFU","INTK_MEMO":"21.7.11: 기능성 내용 변경","SKLL_IX_IRDNT_RAWMTRL":"생균","PRIMARY_FNCLTY":"유산균 증식 및 유해균 억제･배변활동 원활･장 건강에 도움을 줄 수 있음","IFTKN_ATNT_MATR_CN":"(가) 질환이 있거나 의약품 복용 시 전문가와 상담할 것\n(나) 알레르기 체질 등은 개인에 따라 과민반응을 나타낼 수 있음\n(다) 어린이가 함부로 섭취하지 않도록 일일섭취량 방법을 지도할 것\n(라) 이상사례 발생 시 섭취를 중단하고 전문가와 상담할 것"},{"RCOGN_NO":"","RAWMTRL_NM":"마리골드꽃추출물","DAY_INTK_LOWLIMIT":"10","DAY_INTK_HIGHLIMIT":"20","INTK_UNIT":"mg","INTK_MEMO":"(24.12.23.) 섭취시주의사항, 주된기능성 현행화 / '24 신뢰성 확보","SKLL_IX_IRDNT_RAWMTRL":"루테인(Lutein)","PRIMARY_FNCLTY":"(1) 노화로 인해 감소될 수 있는 황반색소밀도를 유지하여 눈 건강에 도움을 줄 수 있음","IFTKN_ATNT_MATR_CN":"(가) 영‧유아, 어린이, 임산부 및 수유부는 섭취를 피할 것\n(나) 흡연자는 섭취 시 전문가와 상담할 것\n(다) 과다 섭취 시 일시적으로 피부가 황색으로 변할 수 있음\n(라) 이상사례 발생 시 섭취를 중단하고 전문가와 상담할 것"}]

## db_050_OuBJfCjsgak / c30 / VIOLATION

영상 그룹: violation_1
제품: 듀오락 골드 / (주)쎌바이오텍 / DB ID 11946

듀오락 골드 제품은 장염을 치료한다.

**판정 근거**

건강 보조 기능을 질병 예방·치료 또는 의약품 대체 주장으로 바꿈. 주간 발표의 질병·의약품 주장 기준에 따른 정답임.

**DB 원문: products:11946.main_functionality**

> 유산균 증식 및 유해균 억제･배변활동 원활･장 건강에 도움을 줄 수 있음

## db_055_UPPksFnfOcU / c25 / OVERCLAIM

영상 그룹: overclaim_1
제품: 드시모네 4500 / 코스맥스엔비티(주) / DB ID 12084

드시모네 4500 제품은 하루 만에 장내 유해균을 99% 깨끗이 제거한다.

**판정 근거**

제품 및 원료의 인정 기능성에는 이 기간·수치·구체적 결과를 보장하는 문장이 없음. 질병 치료나 의약품 대체가 아니라, 인정 범위를 넘는 과장된 효과로 구성함. NLI 점수를 정답으로 사용하지 않으며 실제 NLI의 OVERCLAIM 출력은 별도 평가 대상임.

**DB 원문: products:12084.main_functionality**

> [프로바이오틱스(드시모네)(제2009-28호)] 
> ① 유익한 유산균 증식, 유해균 억제, 배변활동 원활
> ② 장면역을 조절하여 장 건강에 도움을 줄 수 있음

**DB 원문: products:12084.RAWMTRL_STD_INFO**

> [{"RCOGN_NO":"2009-28","RAWMTRL_NM":"프로바이오틱스(드시모네)(기능성원료인정제2009-28호)","DAY_INTK_LOWLIMIT":"100000000","DAY_INTK_HIGHLIMIT":"3000000000000","INTK_UNIT":"","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"Streptococcus thermophillus DSM24731, Lactobacillus acidophillus DSM24735, Lactobacillus delbrueckii ssp bulgaricus DSM24734, Lactobacillus paracasei DSM24733, Lactobacillus plantarum DSM24730, Bifidobacterium longum DSM24736, Bifidobacterium infantis DSM24737, Bifidobacterium breve DSM24732","PRIMARY_FNCLTY":"(국문) 유익한 유산균 증식, 유해균 억제, 배변활동 원활, 장 면역을 조절하여 장 건강에 도움을 줄 수 있음","IFTKN_ATNT_MATR_CN":""}]

## db_057_TpqG2KZ0aRk / c14 / OVERCLAIM

영상 그룹: overclaim_1
제품: 드시모네 키즈 프리미엄 / 코스맥스엔비티(주) / DB ID 12107

드시모네 키즈 프리미엄 제품은 3일 만에 장내 유익균 수를 열 배로 늘리는 효과가 확실하다.

**판정 근거**

제품 및 원료의 인정 기능성에는 이 기간·수치·구체적 결과를 보장하는 문장이 없음. 질병 치료나 의약품 대체가 아니라, 인정 범위를 넘는 과장된 효과로 구성함. NLI 점수를 정답으로 사용하지 않으며 실제 NLI의 OVERCLAIM 출력은 별도 평가 대상임.

**DB 원문: products:12107.main_functionality**

> [프로바이오틱스] 
> ① 유익한 유산균 증식, 유해균 억제, 배변활동 원활
> ② 장면역을 조절하여 장 건강에 도움을 줄 수 있음
> 
> 
> [아연]
> ① 정상적인 면역기능에 필요
> ② 정상적인 세포분열에 필요

**DB 원문: products:12107.RAWMTRL_STD_INFO**

> [{"RCOGN_NO":"2009-28","RAWMTRL_NM":"프로바이오틱스(드시모네)(기능성원료인정제2009-28호)","DAY_INTK_LOWLIMIT":"100000000","DAY_INTK_HIGHLIMIT":"3000000000000","INTK_UNIT":"","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"Streptococcus thermophillus DSM24731, Lactobacillus acidophillus DSM24735, Lactobacillus delbrueckii ssp bulgaricus DSM24734, Lactobacillus paracasei DSM24733, Lactobacillus plantarum DSM24730, Bifidobacterium longum DSM24736, Bifidobacterium infantis DSM24737, Bifidobacterium breve DSM24732","PRIMARY_FNCLTY":"(국문) 유익한 유산균 증식, 유해균 억제, 배변활동 원활, 장 면역을 조절하여 장 건강에 도움을 줄 수 있음","IFTKN_ATNT_MATR_CN":""},{"RCOGN_NO":"","RAWMTRL_NM":"아연","DAY_INTK_LOWLIMIT":"2.55","DAY_INTK_HIGHLIMIT":"12","INTK_UNIT":"mg","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 정상적인 면역기능에 필요\n(2) 정상적인 세포분열에 필요","IFTKN_ATNT_MATR_CN":""}]

## db_059_NaLc-_bwGw8 / c14 / VIOLATION

영상 그룹: violation_1_overclaim_1
제품: 락토핏 솔루션2 / (주)서흥헬스케어 / DB ID 13104

락토핏 솔루션2의 등록된 하루 섭취량은 3캡슐이다.

**판정 근거**

같은 하루 기준에서 DB는 1캡슐이나 Claim은 3캡슐으로 변경함.

**DB 원문: products:13104.intake_method**

> 1일 1회, 1회 1캡슐을 충분한 물과 함께 섭취하십시오.

## db_059_NaLc-_bwGw8 / c15 / OVERCLAIM

영상 그룹: violation_1_overclaim_1
제품: 락토핏 솔루션1 / (주)서흥헬스케어 / DB ID 13102

락토핏 솔루션1 제품은 하루 만에 장내 유해균을 99% 깨끗이 제거한다.

**판정 근거**

제품 및 원료의 인정 기능성에는 이 기간·수치·구체적 결과를 보장하는 문장이 없음. 질병 치료나 의약품 대체가 아니라, 인정 범위를 넘는 과장된 효과로 구성함. NLI 점수를 정답으로 사용하지 않으며 실제 NLI의 OVERCLAIM 출력은 별도 평가 대상임.

**DB 원문: products:13102.main_functionality**

> 프로바이오틱스 : (1) 유산균 증식 및 유해균 억제에 도움을 줄 수 있음 (2) 배변활동 원활에 도움을 줄 수 있음 (3) 장 건강에 도움을 줄 수 있음

**DB 원문: products:13102.RAWMTRL_STD_INFO**

> [{"RCOGN_NO":"","RAWMTRL_NM":"프로바이오틱스","DAY_INTK_LOWLIMIT":"100000000","DAY_INTK_HIGHLIMIT":"10000000000","INTK_UNIT":"CFU","INTK_MEMO":"21.7.11: 기능성 내용 변경","SKLL_IX_IRDNT_RAWMTRL":"생균","PRIMARY_FNCLTY":"유산균 증식 및 유해균 억제･배변활동 원활･장 건강에 도움을 줄 수 있음","IFTKN_ATNT_MATR_CN":"(가) 질환이 있거나 의약품 복용 시 전문가와 상담할 것\n(나) 알레르기 체질 등은 개인에 따라 과민반응을 나타낼 수 있음\n(다) 어린이가 함부로 섭취하지 않도록 일일섭취량 방법을 지도할 것\n(라) 이상사례 발생 시 섭취를 중단하고 전문가와 상담할 것"}]

## db_060_wKE98OOcdPU / c26 / VIOLATION

영상 그룹: violation_2
제품: 락토핏 코어맥스 / 종근당건강(주) / DB ID 13119

락토핏 코어맥스 제품은 장염을 치료한다.

**판정 근거**

건강 보조 기능을 질병 예방·치료 또는 의약품 대체 주장으로 바꿈. 주간 발표의 질병·의약품 주장 기준에 따른 정답임.

**DB 원문: products:13119.main_functionality**

> 유산균 증식 및 유해균 억제･배변활동 원활･장 건강에 도움을 줄 수 있음
> 
> (1) 정상적인 면역기능에 필요
> (2) 정상적인 세포분열에 필요

## db_060_wKE98OOcdPU / c27 / VIOLATION

영상 그룹: violation_2
제품: 락토핏 코어맥스 / 종근당건강(주) / DB ID 13119

락토핏 코어맥스의 등록된 하루 섭취량은 3포이다.

**판정 근거**

같은 하루 기준에서 DB는 1포이나 Claim은 3포으로 변경함.

**DB 원문: products:13119.intake_method**

> 1일 1회, 1회 1포를 식전·식후 어느때나 물 없이 섭취하십시오.

## db_065_d1vRPXhgJAY / c17 / OVERCLAIM

영상 그룹: overclaim_1
제품: 루테인지아잔틴 164 / 주식회사 노바렉스2공장 / DB ID 14188

루테인지아잔틴 164 제품은 단 하루 만에 눈의 피로를 90%까지 확실히 줄인다.

**판정 근거**

제품 및 원료의 인정 기능성에는 이 기간·수치·구체적 결과를 보장하는 문장이 없음. 질병 치료나 의약품 대체가 아니라, 인정 범위를 넘는 과장된 효과로 구성함. NLI 점수를 정답으로 사용하지 않으며 실제 NLI의 OVERCLAIM 출력은 별도 평가 대상임.

**DB 원문: products:14188.main_functionality**

> ①노화로 인해 감소될 수 있는 황반색소 밀도를 유지하여 눈 건강에 도움을 줄 수 있음.
> ①항산화 작용을 하여 유해산소로부터 세포를 보호하는데 필요
> ①유해산소로부터 세포를 보호하는데 필요
> ①정상적인 면역기능에 필요②정상적인 세포분열에 필요
> ①어두운 곳에서 시각 적응을 위해 필요②피부와 점막을 형성하고 기능을 유지하는데 필요③상피세포의 성장과 발달에 필요
> ①탄수화물과 에너지 대사에 필요
> ①체내 에너지 생성에 필요

**DB 원문: products:14188.RAWMTRL_STD_INFO**

> [{"RCOGN_NO":"","RAWMTRL_NM":"비타민 E","DAY_INTK_LOWLIMIT":"3.3","DAY_INTK_HIGHLIMIT":"400","INTK_UNIT":"mg α-TE","INTK_MEMO":"2021.7.11: 기능성 내용 변경","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"항산화 작용을 하여 유해산소로부터 세포를 보호하는데 필요","IFTKN_ATNT_MATR_CN":""},{"RCOGN_NO":"","RAWMTRL_NM":"셀레늄(또는 셀렌)","DAY_INTK_LOWLIMIT":"0.0165","DAY_INTK_HIGHLIMIT":"0.135","INTK_UNIT":"mg","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 유해산소로부터 세포를 보호하는데 필요","IFTKN_ATNT_MATR_CN":""},{"RCOGN_NO":"","RAWMTRL_NM":"아연","DAY_INTK_LOWLIMIT":"2.55","DAY_INTK_HIGHLIMIT":"12","INTK_UNIT":"mg","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 정상적인 면역기능에 필요\n(2) 정상적인 세포분열에 필요","IFTKN_ATNT_MATR_CN":""},{"RCOGN_NO":"","RAWMTRL_NM":"비타민 B2","DAY_INTK_LOWLIMIT":"0.42","DAY_INTK_HIGHLIMIT":"40","INTK_UNIT":"mg","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 체내 에너지 생성에 필요","IFTKN_ATNT_MATR_CN":"(1) 이상사례 발생 시 섭취를 중단하고 전문가와 상담할 것"},{"RCOGN_NO":"","RAWMTRL_NM":"비타민 B1","DAY_INTK_LOWLIMIT":"0.36","DAY_INTK_HIGHLIMIT":"100","INTK_UNIT":"mg","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 탄수화물과 에너지 대사에 필요","IFTKN_ATNT_MATR_CN":"(1) 이상사례 발생 시 섭취를 중단하고 전문가와 상담할 것"},{"RCOGN_NO":"","RAWMTRL_NM":"비타민 A","DAY_INTK_LOWLIMIT":"210","DAY_INTK_HIGHLIMIT":"1000","INTK_UNIT":"μg RAE","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 어두운 곳에서 시각 적응을 위해 필요\n(2) 피부와 점막을 형성하고 기능을 유지하는데 필요\n(3) 상피세포의 성장과 발달에 필요","IFTKN_ATNT_MATR_CN":""},{"RCOGN_NO":"2013-23","RAWMTRL_NM":"루테인지아잔틴복합추출물20%(기능성원료인정제2013-23호)","DAY_INTK_LOWLIMIT":"10","DAY_INTK_HIGHLIMIT":"20","INTK_UNIT":"mg/일","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"루테인(Lutein), 지아잔틴(Zeaxanthin)","PRIMARY_FNCLTY":"(국문) 노화로 인해 감소될 수 있는 황반색소밀도를 유지하여 눈건강에 도움을 줄 수 있음 (영문) May help the eye health by maintaining the density of macular pigments which can be decreased by aging","IFTKN_ATNT_MATR_CN":"(1) 영유아, 어린이, 임산부 및 수유부는 섭취를 피할 것\n(2) 흡연자는 섭취 시 전문가와 상담할 것\n(3) 과다 섭취 시 일시적으로 피부가 황색으로 변할 수 있음\n(4) 이상사례 발생 시 섭취를 중단하고 전문가와 상담할 것"}]

## db_080_yPMKj9wxiKc / c13 / VIOLATION

영상 그룹: violation_1_overclaim_1
제품: 마이니 부스터 비타민 / 주식회사 네추럴웨이 포천 제2공장 / DB ID 15513

마이니 부스터 비타민의 등록된 하루 섭취량은 3병이다.

**판정 근거**

같은 하루 기준에서 DB는 1병이나 Claim은 3병으로 변경함.

**DB 원문: products:15513.intake_method**

> 뚜껑을 개봉하여, 정제2정(800mg, 650mg)을 액상(20ml)과 함께 섭취 or 물과 함께 섭취(1일 1회, 1회 1병)

## db_080_yPMKj9wxiKc / c14 / OVERCLAIM

영상 그룹: violation_1_overclaim_1
제품: 마이니 딥슬립 이뮨 / 주식회사 네추럴웨이 포천 제2공장 / DB ID 15498

마이니 딥슬립 이뮨 제품은 먹은 날부터 깊은 수면 시간이 두 배로 늘어나는 효과가 확실하다.

**판정 근거**

제품 및 원료의 인정 기능성에는 이 기간·수치·구체적 결과를 보장하는 문장이 없음. 질병 치료나 의약품 대체가 아니라, 인정 범위를 넘는 과장된 효과로 구성함. NLI 점수를 정답으로 사용하지 않으며 실제 NLI의 OVERCLAIM 출력은 별도 평가 대상임.

**DB 원문: products:15498.main_functionality**

> ①에너지 이용에 필요
> ②신경과 근육 기능 유지에 필요
> 
> ① 스트레스로 인한 긴장완화에 도움을 줄 수 있음
> 
> (국문) 수면의 질 개선에 도움을 줄 수 있음
> (영문) May help to improve sleep
> 
> ① 지방, 탄수화물, 단백질 대사와 에너지 생성에 필요
> 
> ① 정상적인 면역기능에 필요
> ② 정상적인 세포분열에 필요
> 
> ① 단백질 및 아미노산 이용에 필요
> ② 혈액의 호모시스테인 수준을 정상으로 유지하는데 필요

**DB 원문: products:15498.RAWMTRL_STD_INFO**

> [{"RCOGN_NO":"","RAWMTRL_NM":"마그네슘","DAY_INTK_LOWLIMIT":"94.5","DAY_INTK_HIGHLIMIT":"250","INTK_UNIT":"mg","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 에너지 이용에 필요\n(2) 신경과 근육 기능 유지에 필요","IFTKN_ATNT_MATR_CN":""},{"RCOGN_NO":"","RAWMTRL_NM":"테아닌","DAY_INTK_LOWLIMIT":"200","DAY_INTK_HIGHLIMIT":"250","INTK_UNIT":"mg","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"L-테아닌","PRIMARY_FNCLTY":"(1) 스트레스로 인한 긴장완화에 도움을 줄 수 있음","IFTKN_ATNT_MATR_CN":"(1) 임산부 및 수유부는 섭취를 피할 것\n(2) 카페인 함유음료(커피, 홍차, 녹차 등)와의 병용 섭취에 주의할 것\n(3) 수술전후 환자는 전문가와 상담할 것\n(4) 이상사례 발생 시 섭취를 중단하고 전문가와 상담할 것"},{"RCOGN_NO":"2020-2","RAWMTRL_NM":"유단백가수분해물(락티움)(기능성원료인정제2020-2호)","DAY_INTK_LOWLIMIT":"300","DAY_INTK_HIGHLIMIT":"300","INTK_UNIT":"mg/일","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"알파에스1카제인(αS1-casein)(f91-100)","PRIMARY_FNCLTY":"(국문) 수면의 질 개선에 도움을 줄 수 있음 (영문) May help to improve sleep","IFTKN_ATNT_MATR_CN":"(1) 임산부, 수유여성 및 어린이는 섭취에 주의 (2) 우유 및 유제품에 대하여 알레르기를 나타내는 사람은 섭취에 주의"},{"RCOGN_NO":"","RAWMTRL_NM":"판토텐산","DAY_INTK_LOWLIMIT":"1.5","DAY_INTK_HIGHLIMIT":"200","INTK_UNIT":"mg","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 지방, 탄수화물, 단백질 대사와 에너지 생성에 필요","IFTKN_ATNT_MATR_CN":"(1) 이상사례 발생 시 섭취를 중단하고 전문가와 상담할 것"},{"RCOGN_NO":"","RAWMTRL_NM":"아연","DAY_INTK_LOWLIMIT":"2.55","DAY_INTK_HIGHLIMIT":"12","INTK_UNIT":"mg","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 정상적인 면역기능에 필요\n(2) 정상적인 세포분열에 필요","IFTKN_ATNT_MATR_CN":""},{"RCOGN_NO":"","RAWMTRL_NM":"비타민 B6","DAY_INTK_LOWLIMIT":"0.45","DAY_INTK_HIGHLIMIT":"67","INTK_UNIT":"mg","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 단백질 및 아미노산 이용에 필요\n(2) 혈액의 호모시스테인 수준을 정상으로 유지하는데 필요","IFTKN_ATNT_MATR_CN":"(1) 손발 따끔거림, 작열감 또는 저림 등의 이상사례 발생 시 섭취를 중단하고 전문가와 상담할 것"}]

## db_082_AnT61olLCjY / c16 / OVERCLAIM

영상 그룹: overclaim_1
제품: 머슬파워 / 코스맥스바이오(주) / DB ID 16234

머슬파워 제품은 2주 만에 근육량 3kg 증가가 확실하다.

**판정 근거**

제품 및 원료의 인정 기능성에는 이 기간·수치·구체적 결과를 보장하는 문장이 없음. 질병 치료나 의약품 대체가 아니라, 인정 범위를 넘는 과장된 효과로 구성함. NLI 점수를 정답으로 사용하지 않으며 실제 NLI의 OVERCLAIM 출력은 별도 평가 대상임.

**DB 원문: products:16234.main_functionality**

> 1) 오미자추출물 : 근력 개선에 도움을 줄 수 있음
> 2) 비타민B2 : 체내 에너지 생성에 필요.
> 3) 비타민B6 : 단백질 및 아미노산 이용에 필요, 혈액의 호모시스테인 수준을 정상으로 유지하는데 필요.
> 4) 아연 : 정상적인 면역기능에 필요, 정상적인 세포분열에 필요.

**DB 원문: products:16234.RAWMTRL_STD_INFO**

> [{"RCOGN_NO":"","RAWMTRL_NM":"비타민 B2","DAY_INTK_LOWLIMIT":"0.42","DAY_INTK_HIGHLIMIT":"40","INTK_UNIT":"mg","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 체내 에너지 생성에 필요","IFTKN_ATNT_MATR_CN":"(1) 이상사례 발생 시 섭취를 중단하고 전문가와 상담할 것"},{"RCOGN_NO":"","RAWMTRL_NM":"비타민 B6","DAY_INTK_LOWLIMIT":"0.45","DAY_INTK_HIGHLIMIT":"67","INTK_UNIT":"mg","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 단백질 및 아미노산 이용에 필요\n(2) 혈액의 호모시스테인 수준을 정상으로 유지하는데 필요","IFTKN_ATNT_MATR_CN":"(1) 손발 따끔거림, 작열감 또는 저림 등의 이상사례 발생 시 섭취를 중단하고 전문가와 상담할 것"},{"RCOGN_NO":"","RAWMTRL_NM":"아연","DAY_INTK_LOWLIMIT":"2.55","DAY_INTK_HIGHLIMIT":"12","INTK_UNIT":"mg","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 정상적인 면역기능에 필요\n(2) 정상적인 세포분열에 필요","IFTKN_ATNT_MATR_CN":""},{"RCOGN_NO":"2018-9","RAWMTRL_NM":"오미자추출물(기능성원료인정제2018-9호)","DAY_INTK_LOWLIMIT":"1582","DAY_INTK_HIGHLIMIT":"1582","INTK_UNIT":"mg","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"쉬잔드린(Schizandrin)","PRIMARY_FNCLTY":"(국문) 근력 개선에 도움을 줄 수 있음 (영문) Help to improve muscle strength","IFTKN_ATNT_MATR_CN":"(1) 영·유아, 어린이, 임산부 및 수유부는 섭취에 주의 (2) 수술 전․후 섭취에 주의 (3) 식사조절, 운동을 병행하는 것이 바람직함"}]

## db_088_ZiHnof9A28Y / c13 / OVERCLAIM

영상 그룹: overclaim_2
제품: 메노락토 프로바이오틱스 / (주)알피바이오 / DB ID 16928

메노락토 프로바이오틱스 제품은 단 3일 만에 갱년기 불편감을 90% 줄이는 효과가 확실하다.

**판정 근거**

제품 및 원료의 인정 기능성에는 이 기간·수치·구체적 결과를 보장하는 문장이 없음. 질병 치료나 의약품 대체가 아니라, 인정 범위를 넘는 과장된 효과로 구성함. NLI 점수를 정답으로 사용하지 않으며 실제 NLI의 OVERCLAIM 출력은 별도 평가 대상임.

**DB 원문: products:16928.main_functionality**

> (국문) 갱년기 여성 건강에 도움을 줄 수 있음 (영문) May help to menopausal womens health
> 유산균증식및유해균 억제에 도움을 줄수 있음
> 배변활동 원활에 도움을 줄 수 있음
> 장 건강에 도움을 줄수 있음

**DB 원문: products:16928.RAWMTRL_STD_INFO**

> [{"RCOGN_NO":"2019-22","RAWMTRL_NM":"Lactobacillus acidophilus YT1(기능성원료인정제2019-22호)","DAY_INTK_LOWLIMIT":"100000000","DAY_INTK_HIGHLIMIT":"100000000","INTK_UNIT":"CFU","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"프로바이오틱스 수","PRIMARY_FNCLTY":"(국문) 갱년기 여성 건강에 도움을 줄 수 있음 (영문) May help to improve menopausal women’s health","IFTKN_ATNT_MATR_CN":"(1) 질환이 있거나 의약품(면역억제제 등) 복용 시 전문가와 상담할 것 (2) 알레르기 체질 등은 개인에 따라 과민반응을 나타낼 수 있음 (3) 어린이가 함부로 섭취하지 않도록 일일섭취량 방법을 지도할 것 (4) 이상사례 발생 시 섭취를 중단하고 전문가와 상담할 것"}]

## db_088_ZiHnof9A28Y / c14 / OVERCLAIM

영상 그룹: overclaim_2
제품: 메노락토 프로바이오틱스 / (주)알피바이오 / DB ID 16928

메노락토 프로바이오틱스 제품은 한 번만 먹어도 갱년기로 떨어진 체력이 즉시 두 배로 좋아진다.

**판정 근거**

제품 및 원료의 인정 기능성에는 이 기간·수치·구체적 결과를 보장하는 문장이 없음. 질병 치료나 의약품 대체가 아니라, 인정 범위를 넘는 과장된 효과로 구성함. NLI 점수를 정답으로 사용하지 않으며 실제 NLI의 OVERCLAIM 출력은 별도 평가 대상임.

**DB 원문: products:16928.main_functionality**

> (국문) 갱년기 여성 건강에 도움을 줄 수 있음 (영문) May help to menopausal womens health
> 유산균증식및유해균 억제에 도움을 줄수 있음
> 배변활동 원활에 도움을 줄 수 있음
> 장 건강에 도움을 줄수 있음

**DB 원문: products:16928.RAWMTRL_STD_INFO**

> [{"RCOGN_NO":"2019-22","RAWMTRL_NM":"Lactobacillus acidophilus YT1(기능성원료인정제2019-22호)","DAY_INTK_LOWLIMIT":"100000000","DAY_INTK_HIGHLIMIT":"100000000","INTK_UNIT":"CFU","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"프로바이오틱스 수","PRIMARY_FNCLTY":"(국문) 갱년기 여성 건강에 도움을 줄 수 있음 (영문) May help to improve menopausal women’s health","IFTKN_ATNT_MATR_CN":"(1) 질환이 있거나 의약품(면역억제제 등) 복용 시 전문가와 상담할 것 (2) 알레르기 체질 등은 개인에 따라 과민반응을 나타낼 수 있음 (3) 어린이가 함부로 섭취하지 않도록 일일섭취량 방법을 지도할 것 (4) 이상사례 발생 시 섭취를 중단하고 전문가와 상담할 것"}]

## db_091_RmbfFdrWBdo / c14 / VIOLATION

영상 그룹: violation_1
제품: 메타그린 슬림업 / (주)아모레퍼시픽 / DB ID 17121

메타그린 슬림업 제품은 수유부도 먹을 수 있다.

**판정 근거**

광고와 DB가 모두 수유부 섭취를 말하며, 섭취 회피 조건에 직접 반하는 주장임.

**DB 원문: products:17121.intake_precautions**

> (1) 어린이, 임산부 및 수유부는 섭취를 피할 것
> (2) 간질환이 있거나 의약품 복용 시 전문가와 상담할 것
> (3) 카페인이 함유되어 있어 초조감, 불면 등을 나타낼 수 있음
> (4) 식사 후 섭취할 것
> (5) 카페인을 함유한 식품의 섭취에 주의할 것
> (6) 이상사례 발생 시 섭취를 중단하고 전문가와 상담할 것

## db_093_qHU1meSxfco / c11 / OVERCLAIM

영상 그룹: overclaim_1
제품: 메타그린부스터샷7일 / (주)아모레퍼시픽 / DB ID 17127

메타그린부스터샷7일 제품은 2주 만에 체지방 5kg을 확실히 줄인다.

**판정 근거**

제품 및 원료의 인정 기능성에는 이 기간·수치·구체적 결과를 보장하는 문장이 없음. 질병 치료나 의약품 대체가 아니라, 인정 범위를 넘는 과장된 효과로 구성함. NLI 점수를 정답으로 사용하지 않으며 실제 NLI의 OVERCLAIM 출력은 별도 평가 대상임.

**DB 원문: products:17127.main_functionality**

> [녹차추출물]
> 항산화･체지방 감소･혈중 콜레스테롤 개선에 도움을 줄 수 있음
> [비타민B1]
> 탄수화물과 에너지 대사에 필요
> [판토텐산]
> 지방, 탄수화물, 단백질 대사와 에너지 생성에 필요
> [APIC 대두배아열수추출물 등 복합물(제2008-6호)
> (국문) 체지방의 감소에 도움을 줄 수 있음 (영문) May help to reduce body fat

**DB 원문: products:17127.RAWMTRL_STD_INFO**

> [{"RCOGN_NO":"2008-6","RAWMTRL_NM":"APIC 대두배아열수추출물 등 복합물(기능성원료인정제2008-6호)","DAY_INTK_LOWLIMIT":"700","DAY_INTK_HIGHLIMIT":"700","INTK_UNIT":"mg","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"Daidzin, Glycitin, Genistin 함량의 총 합, L-carnitine","PRIMARY_FNCLTY":"(국문) 체지방의 감소에 도움을 줄 수 있음 (영문) May help to reduce body fat","IFTKN_ATNT_MATR_CN":"(1) 어린이, 임산부 및 수유부는 섭취를 피할 것 (2) 알레르기성 비염, 천식, 우유, 대두알레르기반응을 나타내는 사람은 섭취에 주의 (3) 에스트로겐 호르몬에 민감한 사람은 섭취에 주의 (4) 이상사례 발생 시 섭취를 중단하고 전문가와 상담할 것"},{"RCOGN_NO":"","RAWMTRL_NM":"판토텐산","DAY_INTK_LOWLIMIT":"1.5","DAY_INTK_HIGHLIMIT":"200","INTK_UNIT":"mg","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 지방, 탄수화물, 단백질 대사와 에너지 생성에 필요","IFTKN_ATNT_MATR_CN":"(1) 이상사례 발생 시 섭취를 중단하고 전문가와 상담할 것"},{"RCOGN_NO":"","RAWMTRL_NM":"비타민 B1","DAY_INTK_LOWLIMIT":"0.36","DAY_INTK_HIGHLIMIT":"100","INTK_UNIT":"mg","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 탄수화물과 에너지 대사에 필요","IFTKN_ATNT_MATR_CN":"(1) 이상사례 발생 시 섭취를 중단하고 전문가와 상담할 것"},{"RCOGN_NO":"","RAWMTRL_NM":"녹차추출물","DAY_INTK_LOWLIMIT":"0.3","DAY_INTK_HIGHLIMIT":"1","INTK_UNIT":"g","INTK_MEMO":"(24.12.20.) 섭취시주의사항, 주된기능성 현행화 / '24 신뢰성 확보","SKLL_IX_IRDNT_RAWMTRL":"카테킨","PRIMARY_FNCLTY":"(1) 기능성 내용 : 항산화･체지방 감소･혈중 콜레스테롤 개선에 도움을 줄 수 있음","IFTKN_ATNT_MATR_CN":"(가) 어린이, 임산부 및 수유부는 섭취를 피할 것\n(나) 간질환이 있거나 의약품 복용 시 전문가와 상담할 것\n(다) 카페인이 함유되어 있어 초조감, 불면 등을 나타낼 수 있음\n(라) 식사 후 섭취할 것\n(마) 카페인을 함유한 식품의 섭취에 주의할 것\n(바) 이상사례 발생 시 섭취를 중단하고 전문가와 상담할 것"}]

## db_095_e2JpCbQWuvo / c27 / VIOLATION

영상 그룹: violation_1
제품: 면역엔 알로에뮨 / (주)천호엔케어 / DB ID 17422

면역엔 알로에뮨 제품은 독감을 예방한다.

**판정 근거**

건강 보조 기능을 질병 예방·치료 또는 의약품 대체 주장으로 바꿈. 주간 발표의 질병·의약품 주장 기준에 따른 정답임.

**DB 원문: products:17422.main_functionality**

> -피부건강·장 건강·면역력 증진에 도움을 줄 수 있음

## db_096_LGDnFYgymEQ / c17 / OVERCLAIM

영상 그룹: overclaim_1
제품: 면역탄탄 칼슘&아연&비타민D 젤리스틱 / 농업회사법인(주)힐링팜 / DB ID 17489

면역탄탄 칼슘&아연&비타민D 젤리스틱 제품은 일주일 만에 뼈의 강도를 두 배로 높여 준다.

**판정 근거**

제품 및 원료의 인정 기능성에는 이 기간·수치·구체적 결과를 보장하는 문장이 없음. 질병 치료나 의약품 대체가 아니라, 인정 범위를 넘는 과장된 효과로 구성함. NLI 점수를 정답으로 사용하지 않으며 실제 NLI의 OVERCLAIM 출력은 별도 평가 대상임.

**DB 원문: products:17489.main_functionality**

> [칼슘] 뼈와 치아 형성에 필요, 신경과 근육 기능 유지에 필요, 정상적인 혈액응고에 필요, 골다공증발생 위험 감소에 도움을 줌
> [아연] 정상적인 면역기능에 필요, 정상적인 세포분열에 필요
> [비타민D] 칼슘과 인이 흡수되고 이용되는데 필요, 뼈의 형성과 유지에 필요, 골다공증발생 위험 감소에 도움을 줌

**DB 원문: products:17489.RAWMTRL_STD_INFO**

> [{"RCOGN_NO":"","RAWMTRL_NM":"칼슘","DAY_INTK_LOWLIMIT":"210","DAY_INTK_HIGHLIMIT":"800","INTK_UNIT":"mg","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 뼈와 치아 형성에 필요\n(2) 신경과 근육 기능 유지에 필요\n(3) 정상적인 혈액응고에 필요\n(4) 골다공증발생 위험 감소에 도움을 줌","IFTKN_ATNT_MATR_CN":""},{"RCOGN_NO":"","RAWMTRL_NM":"아연","DAY_INTK_LOWLIMIT":"2.55","DAY_INTK_HIGHLIMIT":"12","INTK_UNIT":"mg","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 정상적인 면역기능에 필요\n(2) 정상적인 세포분열에 필요","IFTKN_ATNT_MATR_CN":""},{"RCOGN_NO":"","RAWMTRL_NM":"비타민 D","DAY_INTK_LOWLIMIT":"0.003","DAY_INTK_HIGHLIMIT":"0.01","INTK_UNIT":"mg","INTK_MEMO":"일일섭취량 : 3~10 μg(120∼400 IU)","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 칼슘과 인이 흡수되고 이용되는데 필요\n(2) 뼈의 형성과 유지에 필요\n(3) 골다공증발생 위험 감소에 도움을 줌","IFTKN_ATNT_MATR_CN":"(가) 고칼슘혈증이 있거나 의약품 복용 시 전문가와 상담할 것\n(나) 이상사례 발생 시 섭취를 중단하고 전문가와 상담할 것"}]

## db_097_un653gDaVwY / c09 / OVERCLAIM

영상 그룹: overclaim_1
제품: 밀크씨슬 멀티미네랄 비타민 / 광동헬스바이오(주) 2공장 / DB ID 18130

밀크씨슬 멀티미네랄 비타민 제품은 일주일 만에 간 해독 능력을 두 배로 높이는 효과가 확실하다.

**판정 근거**

제품 및 원료의 인정 기능성에는 이 기간·수치·구체적 결과를 보장하는 문장이 없음. 질병 치료나 의약품 대체가 아니라, 인정 범위를 넘는 과장된 효과로 구성함. NLI 점수를 정답으로 사용하지 않으며 실제 NLI의 OVERCLAIM 출력은 별도 평가 대상임.

**DB 원문: products:18130.main_functionality**

> [밀크씨슬 추출물] 간 건강에 도움을 줄 수 있음
> [나이아신] 체내 에너지 생성에 필요
> [아연] ①정상적인 면역기능에 필요 ②정상적인 세포분열에 필요
> [망간] ①뼈 형성에 필요 ②에너지 이용에 필요 ③유해산소로부터 세포를 보호하는데 필요
> [구리] ①철의 운반과 이용에 필요 ②유해산소로부터 세포를 보호하는데 필요
> [셀렌] 유해산소로부터 세포를 보호하는데 필요
> [판토텐산] 지방, 탄수화물, 단백질 대사와 에너지 생성에 필요
> [비오틴] 지방, 탄수화물, 단백질 대사와 에너지 생성에 필요
> [비타민B12] 정상적인 엽산 대사에 필요
> [비타민B6] ①단백질 및 아미노산 이용에 필요 ②혈액의 호모시스테인 수준을 정상으로 유지하는데 필요
> [비타민B1] 탄수화물과 에너지 대사에 필요
> [비타민B2] 체내 에너지 생성에 필요
> [엽산] ①세포와 혈액생성에 필요 ②태아 신경관의 정상 발달에 필요 ③혈액의 호모시스테인 수준을 정상으로 유지하는데 필요

**DB 원문: products:18130.RAWMTRL_STD_INFO**

> [{"RCOGN_NO":"","RAWMTRL_NM":"엽산","DAY_INTK_LOWLIMIT":"120","DAY_INTK_HIGHLIMIT":"400","INTK_UNIT":"μg","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 세포와 혈액생성에 필요\n(2) 태아 신경관의 정상 발달에 필요\n(3) 혈액의 호모시스테인 수준을 정상으로 유지하는데 필요","IFTKN_ATNT_MATR_CN":""},{"RCOGN_NO":"","RAWMTRL_NM":"비타민 B2","DAY_INTK_LOWLIMIT":"0.42","DAY_INTK_HIGHLIMIT":"40","INTK_UNIT":"mg","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 체내 에너지 생성에 필요","IFTKN_ATNT_MATR_CN":"(1) 이상사례 발생 시 섭취를 중단하고 전문가와 상담할 것"},{"RCOGN_NO":"","RAWMTRL_NM":"비타민 B1","DAY_INTK_LOWLIMIT":"0.36","DAY_INTK_HIGHLIMIT":"100","INTK_UNIT":"mg","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 탄수화물과 에너지 대사에 필요","IFTKN_ATNT_MATR_CN":"(1) 이상사례 발생 시 섭취를 중단하고 전문가와 상담할 것"},{"RCOGN_NO":"","RAWMTRL_NM":"비타민 B6","DAY_INTK_LOWLIMIT":"0.45","DAY_INTK_HIGHLIMIT":"67","INTK_UNIT":"mg","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 단백질 및 아미노산 이용에 필요\n(2) 혈액의 호모시스테인 수준을 정상으로 유지하는데 필요","IFTKN_ATNT_MATR_CN":"(1) 손발 따끔거림, 작열감 또는 저림 등의 이상사례 발생 시 섭취를 중단하고 전문가와 상담할 것"},{"RCOGN_NO":"","RAWMTRL_NM":"비타민 B12","DAY_INTK_LOWLIMIT":"0.00072","DAY_INTK_HIGHLIMIT":"2","INTK_UNIT":"mg","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 정상적인 엽산 대사에 필요","IFTKN_ATNT_MATR_CN":"(1) 이상사례 발생 시 섭취를 중단하고 전문가와 상담할 것"},{"RCOGN_NO":"","RAWMTRL_NM":"비오틴","DAY_INTK_LOWLIMIT":"0.009","DAY_INTK_HIGHLIMIT":"0.9","INTK_UNIT":"mg","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 지방, 탄수화물, 단백질 대사와 에너지 생성에 필요","IFTKN_ATNT_MATR_CN":"(1) 이상사례 발생 시 섭취를 중단하고 전문가와 상담할 것"},{"RCOGN_NO":"","RAWMTRL_NM":"판토텐산","DAY_INTK_LOWLIMIT":"1.5","DAY_INTK_HIGHLIMIT":"200","INTK_UNIT":"mg","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 지방, 탄수화물, 단백질 대사와 에너지 생성에 필요","IFTKN_ATNT_MATR_CN":"(1) 이상사례 발생 시 섭취를 중단하고 전문가와 상담할 것"},{"RCOGN_NO":"","RAWMTRL_NM":"셀레늄(또는 셀렌)","DAY_INTK_LOWLIMIT":"0.0165","DAY_INTK_HIGHLIMIT":"0.135","INTK_UNIT":"mg","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 유해산소로부터 세포를 보호하는데 필요","IFTKN_ATNT_MATR_CN":""},{"RCOGN_NO":"","RAWMTRL_NM":"구리","DAY_INTK_LOWLIMIT":"0.24","DAY_INTK_HIGHLIMIT":"7","INTK_UNIT":"mg","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 철의 운반과 이용에 필요\n(2) 유해산소로부터 세포를 보호하는데 필요","IFTKN_ATNT_MATR_CN":""},{"RCOGN_NO":"","RAWMTRL_NM":"밀크씨슬(카르두스 마리아누스) 추출물","DAY_INTK_LOWLIMIT":"130","DAY_INTK_HIGHLIMIT":"130","INTK_UNIT":"mg","INTK_MEMO":"(24.12.20.) 일일섭취량, 섭취시주의사항 현행화 / '24 신뢰성 확보","SKLL_IX_IRDNT_RAWMTRL":"실리마린","PRIMARY_FNCLTY":"① 간 건강에 도움을 줄 수 있음","IFTKN_ATNT_MATR_CN":"(가) 어린이, 임산부 및 수유부는 섭취를 피할 것\n(나) 알레르기 반응이 나타나는 경우에는 섭취 중단\n(다) 설사, 위통, 복부팽만 등의 위장관계 장애가 나타나는 경우에는 섭취에 주의\n(라) 이상사례 발생 시 섭취를 중단하고 전문가와 상담할 것"},{"RCOGN_NO":"","RAWMTRL_NM":"나이아신","DAY_INTK_LOWLIMIT":"4.5","DAY_INTK_HIGHLIMIT":"670","INTK_UNIT":"mg","INTK_MEMO":"니코틴산 4.5～23 mg, 니코틴산아미드 4.5～670 mg","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 체내 에너지 생성에 필요","IFTKN_ATNT_MATR_CN":""},{"RCOGN_NO":"","RAWMTRL_NM":"아연","DAY_INTK_LOWLIMIT":"2.55","DAY_INTK_HIGHLIMIT":"12","INTK_UNIT":"mg","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 정상적인 면역기능에 필요\n(2) 정상적인 세포분열에 필요","IFTKN_ATNT_MATR_CN":""},{"RCOGN_NO":"","RAWMTRL_NM":"망간","DAY_INTK_LOWLIMIT":"0.9","DAY_INTK_HIGHLIMIT":"3.5","INTK_UNIT":"mg","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 뼈 형성에 필요\n(2) 에너지 이용에 필요\n(3) 유해산소로부터 세포를 보호하는데 필요","IFTKN_ATNT_MATR_CN":""}]

## db_098_6-u-FnfXyZs / c09 / VIOLATION

영상 그룹: violation_1
제품: 발리 유산균 프리미엄 / (주)케비젠 / DB ID 18775

발리 유산균 프리미엄의 등록된 하루 섭취량은 3캡슐이다.

**판정 근거**

같은 하루 기준에서 DB는 1캡슐이나 Claim은 3캡슐으로 변경함.

**DB 원문: products:18775.intake_method**

> 1일 1회, 1회 1캡슐(450mg)을 충분한 물과 함께 섭취하십시오.

## db_099_dSjddyyEbrQ / c06 / VIOLATION

영상 그룹: violation_1
제품: 변할지도 / 경성제약주식회사 / DB ID 19499

변할지도 제품은 고지혈증 치료제를 대신할 수 있다.

**판정 근거**

건강 보조 기능을 질병 예방·치료 또는 의약품 대체 주장으로 바꿈. 주간 발표의 질병·의약품 주장 기준에 따른 정답임.

**DB 원문: products:19499.main_functionality**

> ①혈중 콜레스테롤 개선·배변활동 원활에 도움을 줄 수 있음

## db_100_X6OK887LWyA / c22 / VIOLATION

영상 그룹: violation_1
제품: 보스웰리아 BCC / (주)서흥 / DB ID 19634

보스웰리아 BCC 제품은 퇴행성 관절염을 치료한다.

**판정 근거**

건강 보조 기능을 질병 예방·치료 또는 의약품 대체 주장으로 바꿈. 주간 발표의 질병·의약품 주장 기준에 따른 정답임.

**DB 원문: products:19634.main_functionality**

> 보스웰리아추출물등복합물(Flexir) : (국문) 관절 및 연골 건강에 도움을 줄 수 있음 (영문) May help to maintain healthy joint and cartilage
> 셀렌 : 유해산소로부터 세포를 보호하는데 필요
> 아연 : (1) 정상적인 면역기능에 필요 (2) 정상적인 세포분열에 필요
> 망간 : (1) 뼈 형성에 필요 (2) 에너지 이용에 필요 (3) 유해산소로부터 세포를 보호하는데 필요
> 비타민D : (1) 칼슘과 인이 흡수되고 이용되는데 필요 (2) 뼈의 형성과 유지에 필요 (3) 골다공증발생 위험 감소에 도움을 줌
> 비오틴 : 지방, 탄수화물, 단백질 대사와 에너지 생성에 필요
> 비타민K : (1) 정상적인 혈액응고에 필요 (2) 뼈의 구성에 필요

## db_101_k9HPaTy2jAc / c08 / OVERCLAIM

영상 그룹: overclaim_1
제품: 비나이다 혈당케어 바나바잎 / 우리바이오(주) / DB ID 20305

비나이다 혈당케어 바나바잎 제품은 탄수화물을 두 배로 먹어도 식후 혈당 상승을 완전히 막는다.

**판정 근거**

제품 및 원료의 인정 기능성에는 이 기간·수치·구체적 결과를 보장하는 문장이 없음. 질병 치료나 의약품 대체가 아니라, 인정 범위를 넘는 과장된 효과로 구성함. NLI 점수를 정답으로 사용하지 않으며 실제 NLI의 OVERCLAIM 출력은 별도 평가 대상임.

**DB 원문: products:20305.main_functionality**

> ① 식후 혈당상승 억제에 도움을 줄 수 있음
> 
> (1) 체내 탄수화물, 지방, 단백질 대사에 관여
> 
> (1) 유해산소로부터 세포를 보호하는데 필요
> 
> (1) 정상적인 면역기능에 필요
> (2) 정상적인 세포분열에 필요
> 
> (1) 세포와 혈액생성에 필요
> (2) 태아 신경관의 정상 발달에 필요
> (3) 혈액의 호모시스테인 수준을 정상으로 유지하는데 필요

**DB 원문: products:20305.RAWMTRL_STD_INFO**

> [{"RCOGN_NO":"","RAWMTRL_NM":"바나바잎 추출물","DAY_INTK_LOWLIMIT":"0.45","DAY_INTK_HIGHLIMIT":"1.3","INTK_UNIT":"mg","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"코로솔산(Corosolic acid)","PRIMARY_FNCLTY":"(1) 식후 혈당상승 억제에 도움을 줄 수 있음","IFTKN_ATNT_MATR_CN":"(1) 어린이, 임산부 및 수유부는 섭취를 피할 것\n(2) 이상사례 발생 시 섭취를 중단하고 전문가와 상담할 것"},{"RCOGN_NO":"","RAWMTRL_NM":"크롬","DAY_INTK_LOWLIMIT":"0.009","DAY_INTK_HIGHLIMIT":"9","INTK_UNIT":"mg","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 체내 탄수화물, 지방, 단백질 대사에 관여","IFTKN_ATNT_MATR_CN":"(1) 당뇨병이 있는 경우 섭취 전 전문가와 상담할 것\n(2) 이상사례 발생 시 섭취를 중단하고 전문가와 상담할 것"},{"RCOGN_NO":"","RAWMTRL_NM":"셀레늄(또는 셀렌)","DAY_INTK_LOWLIMIT":"0.0165","DAY_INTK_HIGHLIMIT":"0.135","INTK_UNIT":"mg","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 유해산소로부터 세포를 보호하는데 필요","IFTKN_ATNT_MATR_CN":""},{"RCOGN_NO":"","RAWMTRL_NM":"아연","DAY_INTK_LOWLIMIT":"2.55","DAY_INTK_HIGHLIMIT":"12","INTK_UNIT":"mg","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 정상적인 면역기능에 필요\n(2) 정상적인 세포분열에 필요","IFTKN_ATNT_MATR_CN":""},{"RCOGN_NO":"","RAWMTRL_NM":"엽산","DAY_INTK_LOWLIMIT":"120","DAY_INTK_HIGHLIMIT":"400","INTK_UNIT":"μg","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 세포와 혈액생성에 필요\n(2) 태아 신경관의 정상 발달에 필요\n(3) 혈액의 호모시스테인 수준을 정상으로 유지하는데 필요","IFTKN_ATNT_MATR_CN":""}]

## db_102_j2gn9xONdJE / c13 / OVERCLAIM

영상 그룹: overclaim_1
제품: 비에날 퀸 / (주)서흥 / DB ID 20442

비에날 퀸 제품은 2주 만에 체지방 5kg을 확실히 줄인다.

**판정 근거**

제품 및 원료의 인정 기능성에는 이 기간·수치·구체적 결과를 보장하는 문장이 없음. 질병 치료나 의약품 대체가 아니라, 인정 범위를 넘는 과장된 효과로 구성함. NLI 점수를 정답으로 사용하지 않으며 실제 NLI의 OVERCLAIM 출력은 별도 평가 대상임.

**DB 원문: products:20442.main_functionality**

> Lactobacillus gasseri BNR17 : (국문) 체지방 감소에 도움을 줄 수 있음(생리활성기능), 유산균 증식 및 유해균 억제에 도움을 줄 수 있음, 배변활동 원활에 도움을 줄 수 있음, 장 건강에 도움을 줄 수 있음
>                                           (영문) May help to reduce body fat. 
> 회화나무열매추출물: 갱년기 여성의 건강에 도움을 줄 수 있음  
> 셀렌: 유해산소로부터 세포를 보호하는데 필요  
> 비타민D: ①칼슘과 인이 흡수되고 이용되는데 필요②뼈의 형성과 유지에 필요③골다공증발생 위험 감소에 도움을 줌
> 아연: ①정상적인 면역기능에 필요②정상적인 세포분열에 필요
> 비타민A: ①어두운 곳에서 시각 적응을 위해 필요②피부와 점막을 형성하고 기능을 유지하는데 필요③상피세포의 성장과 발달에 필요.

**DB 원문: products:20442.RAWMTRL_STD_INFO**

> [{"RCOGN_NO":"","RAWMTRL_NM":"회화나무열매추출물","DAY_INTK_LOWLIMIT":"350","DAY_INTK_HIGHLIMIT":"350","INTK_UNIT":"mg","INTK_MEMO":"(24.12.23.) 일일섭취량 현행화 / '24 신뢰성 확보","SKLL_IX_IRDNT_RAWMTRL":"소포리코사이드(Sophoricoside)","PRIMARY_FNCLTY":"(1) 갱년기 여성의 건강에 도움을 줄 수 있음","IFTKN_ATNT_MATR_CN":"(가) 어린이, 임산부, 수유부는 섭취에 주의\n(나) 에스트로겐 호르몬에 민감한 사람은 섭취에 주의"},{"RCOGN_NO":"","RAWMTRL_NM":"셀레늄(또는 셀렌)","DAY_INTK_LOWLIMIT":"0.0165","DAY_INTK_HIGHLIMIT":"0.135","INTK_UNIT":"mg","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 유해산소로부터 세포를 보호하는데 필요","IFTKN_ATNT_MATR_CN":""},{"RCOGN_NO":"","RAWMTRL_NM":"비타민 D","DAY_INTK_LOWLIMIT":"0.003","DAY_INTK_HIGHLIMIT":"0.01","INTK_UNIT":"mg","INTK_MEMO":"일일섭취량 : 3~10 μg(120∼400 IU)","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 칼슘과 인이 흡수되고 이용되는데 필요\n(2) 뼈의 형성과 유지에 필요\n(3) 골다공증발생 위험 감소에 도움을 줌","IFTKN_ATNT_MATR_CN":"(가) 고칼슘혈증이 있거나 의약품 복용 시 전문가와 상담할 것\n(나) 이상사례 발생 시 섭취를 중단하고 전문가와 상담할 것"},{"RCOGN_NO":"","RAWMTRL_NM":"아연","DAY_INTK_LOWLIMIT":"2.55","DAY_INTK_HIGHLIMIT":"12","INTK_UNIT":"mg","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 정상적인 면역기능에 필요\n(2) 정상적인 세포분열에 필요","IFTKN_ATNT_MATR_CN":""},{"RCOGN_NO":"","RAWMTRL_NM":"비타민 A","DAY_INTK_LOWLIMIT":"210","DAY_INTK_HIGHLIMIT":"1000","INTK_UNIT":"μg RAE","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 어두운 곳에서 시각 적응을 위해 필요\n(2) 피부와 점막을 형성하고 기능을 유지하는데 필요\n(3) 상피세포의 성장과 발달에 필요","IFTKN_ATNT_MATR_CN":""},{"RCOGN_NO":"2017-6","RAWMTRL_NM":"Lactobacillus gasseri BNR17(기능성원료인정제2017-6호)","DAY_INTK_LOWLIMIT":"10000000000","DAY_INTK_HIGHLIMIT":"10000000000","INTK_UNIT":"CFU","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"Lactobacillus gasseri BNR17","PRIMARY_FNCLTY":"(국문) 체지방 감소에 도움을 줄 수 있음(생리활성기능) (영문) May help to reduce body fat","IFTKN_ATNT_MATR_CN":"(1) 산성도가 낮은 음료나 뜨거운 물과 함께 복용하는 것을 피하는 것이 좋음"}]

## db_104_2DMM40MV6do / c19 / OVERCLAIM

영상 그룹: overclaim_2
제품: 선택하라 프리바이오틱스 장건강 솔루션 플러스 / 주식회사한미양행 / DB ID 22710

선택하라 프리바이오틱스 장건강 솔루션 플러스 제품은 하루 만에 장내 유해균을 99% 깨끗이 제거한다.

**판정 근거**

제품 및 원료의 인정 기능성에는 이 기간·수치·구체적 결과를 보장하는 문장이 없음. 질병 치료나 의약품 대체가 아니라, 인정 범위를 넘는 과장된 효과로 구성함. NLI 점수를 정답으로 사용하지 않으며 실제 NLI의 OVERCLAIM 출력은 별도 평가 대상임.

**DB 원문: products:22710.main_functionality**

> ① 유익균 증식 및 유해균 억제·칼슘 흡수·배변활동 원활에 도움을 줄 수 있음
> 
> ①정상적인 면역기능에 필요②정상적인 세포분열에 필요

**DB 원문: products:22710.RAWMTRL_STD_INFO**

> [{"RCOGN_NO":"","RAWMTRL_NM":"프락토올리고당","DAY_INTK_LOWLIMIT":"3","DAY_INTK_HIGHLIMIT":"8","INTK_UNIT":"g","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"프락토올리고당","PRIMARY_FNCLTY":"(1) 장내 유익균 증식 및 배변활동 원활에 도움을 줄 수 있음","IFTKN_ATNT_MATR_CN":"(가) 섭취 시 가스참, 트림, 복통, 복부팽만감 등이 발생할 수 있음\n(나) 이상사례 발생 시 섭취를 중단하고 전문가와 상담할 것"},{"RCOGN_NO":"","RAWMTRL_NM":"아연","DAY_INTK_LOWLIMIT":"2.55","DAY_INTK_HIGHLIMIT":"12","INTK_UNIT":"mg","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 정상적인 면역기능에 필요\n(2) 정상적인 세포분열에 필요","IFTKN_ATNT_MATR_CN":""}]

## db_104_2DMM40MV6do / c20 / OVERCLAIM

영상 그룹: overclaim_2
제품: 선택하라 프리바이오틱스 장건강 솔루션 플러스 / 주식회사한미양행 / DB ID 22710

선택하라 프리바이오틱스 장건강 솔루션 플러스 제품은 3일 만에 장내 유익균 수를 열 배로 늘리는 효과가 확실하다.

**판정 근거**

제품 및 원료의 인정 기능성에는 이 기간·수치·구체적 결과를 보장하는 문장이 없음. 질병 치료나 의약품 대체가 아니라, 인정 범위를 넘는 과장된 효과로 구성함. NLI 점수를 정답으로 사용하지 않으며 실제 NLI의 OVERCLAIM 출력은 별도 평가 대상임.

**DB 원문: products:22710.main_functionality**

> ① 유익균 증식 및 유해균 억제·칼슘 흡수·배변활동 원활에 도움을 줄 수 있음
> 
> ①정상적인 면역기능에 필요②정상적인 세포분열에 필요

**DB 원문: products:22710.RAWMTRL_STD_INFO**

> [{"RCOGN_NO":"","RAWMTRL_NM":"프락토올리고당","DAY_INTK_LOWLIMIT":"3","DAY_INTK_HIGHLIMIT":"8","INTK_UNIT":"g","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"프락토올리고당","PRIMARY_FNCLTY":"(1) 장내 유익균 증식 및 배변활동 원활에 도움을 줄 수 있음","IFTKN_ATNT_MATR_CN":"(가) 섭취 시 가스참, 트림, 복통, 복부팽만감 등이 발생할 수 있음\n(나) 이상사례 발생 시 섭취를 중단하고 전문가와 상담할 것"},{"RCOGN_NO":"","RAWMTRL_NM":"아연","DAY_INTK_LOWLIMIT":"2.55","DAY_INTK_HIGHLIMIT":"12","INTK_UNIT":"mg","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 정상적인 면역기능에 필요\n(2) 정상적인 세포분열에 필요","IFTKN_ATNT_MATR_CN":""}]

## db_114_g7TzMEZKjaU / c14 / VIOLATION

영상 그룹: violation_1
제품: 센트룸 에너지 구미 / (주)서흥 오송2공장 / DB ID 22963

센트룸 에너지 구미 제품은 만성피로증후군을 치료한다.

**판정 근거**

건강 보조 기능을 질병 예방·치료 또는 의약품 대체 주장으로 바꿈. 주간 발표의 질병·의약품 주장 기준에 따른 정답임.

**DB 원문: products:22963.main_functionality**

> 나이아신 : 체내 에너지 생성에 필요
> 비타민B6 : (1) 단백질 및 아미노산 이용에 필요 (2) 혈액의 호모시스테인 수준을 정상으로 유지하는데 필요
> 비타민B1 : 탄수화물과 에너지 대사에 필요
> 비타민B2 : 체내 에너지 생성에 필요

## db_120_QUwiyY9Qh_k / c12 / VIOLATION

영상 그룹: violation_1
제품: 셀로맥스 가네요 / 주식회사 네추럴웨이 포천 제2공장 / DB ID 23070

셀로맥스 가네요 제품은 췌장염을 치료한다.

**판정 근거**

건강 보조 기능을 질병 예방·치료 또는 의약품 대체 주장으로 바꿈. 주간 발표의 질병·의약품 주장 기준에 따른 정답임.

**DB 원문: products:23070.main_functionality**

> - 담즙분비를 촉진하여 지방 소화에 도움을 줄 수 있음
> - May help fat digestion by facilitating the secretion of bile acid

## db_121_p3YufTgQRHA / c12 / VIOLATION

영상 그룹: violation_1
제품: 셀로맥스 명품 알티지 오메가3 / 주식회사 노바렉스2공장 / DB ID 23099

셀로맥스 명품 알티지 오메가3 제품은 혈전증을 치료한다.

**판정 근거**

건강 보조 기능을 질병 예방·치료 또는 의약품 대체 주장으로 바꿈. 주간 발표의 질병·의약품 주장 기준에 따른 정답임.

**DB 원문: products:23099.main_functionality**

> 혈중 중성지질 개선·혈행 개선·건조한 눈을 개선하여 눈 건강에 도움을 줄 수 있음

## db_123_seN7xZFP5eE / c11 / OVERCLAIM

영상 그룹: overclaim_2
제품: 셀로맥스 비타민D 5000IU / 주식회사 노바렉스2공장 / DB ID 23116

셀로맥스 비타민D 5000IU 제품은 한 달 만에 골밀도를 30% 높이는 효과가 확실하다.

**판정 근거**

제품 및 원료의 인정 기능성에는 이 기간·수치·구체적 결과를 보장하는 문장이 없음. 질병 치료나 의약품 대체가 아니라, 인정 범위를 넘는 과장된 효과로 구성함. NLI 점수를 정답으로 사용하지 않으며 실제 NLI의 OVERCLAIM 출력은 별도 평가 대상임.

**DB 원문: products:23116.main_functionality**

> ①칼슘과 인이 흡수되고 이용되는데 필요②뼈의 형성과 유지에 필요③골다공증발생 위험 감소에 도움을 줌

**DB 원문: products:23116.RAWMTRL_STD_INFO**

> [{"RCOGN_NO":"","RAWMTRL_NM":"비타민 D","DAY_INTK_LOWLIMIT":"0.003","DAY_INTK_HIGHLIMIT":"0.01","INTK_UNIT":"mg","INTK_MEMO":"일일섭취량 : 3~10 μg(120∼400 IU)","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 칼슘과 인이 흡수되고 이용되는데 필요\n(2) 뼈의 형성과 유지에 필요\n(3) 골다공증발생 위험 감소에 도움을 줌","IFTKN_ATNT_MATR_CN":"(가) 고칼슘혈증이 있거나 의약품 복용 시 전문가와 상담할 것\n(나) 이상사례 발생 시 섭취를 중단하고 전문가와 상담할 것"}]

## db_123_seN7xZFP5eE / c12 / OVERCLAIM

영상 그룹: overclaim_2
제품: 셀로맥스 비타민D 5000IU / 주식회사 노바렉스2공장 / DB ID 23116

셀로맥스 비타민D 5000IU 제품은 일주일 만에 뼈의 강도를 두 배로 높여 준다.

**판정 근거**

제품 및 원료의 인정 기능성에는 이 기간·수치·구체적 결과를 보장하는 문장이 없음. 질병 치료나 의약품 대체가 아니라, 인정 범위를 넘는 과장된 효과로 구성함. NLI 점수를 정답으로 사용하지 않으며 실제 NLI의 OVERCLAIM 출력은 별도 평가 대상임.

**DB 원문: products:23116.main_functionality**

> ①칼슘과 인이 흡수되고 이용되는데 필요②뼈의 형성과 유지에 필요③골다공증발생 위험 감소에 도움을 줌

**DB 원문: products:23116.RAWMTRL_STD_INFO**

> [{"RCOGN_NO":"","RAWMTRL_NM":"비타민 D","DAY_INTK_LOWLIMIT":"0.003","DAY_INTK_HIGHLIMIT":"0.01","INTK_UNIT":"mg","INTK_MEMO":"일일섭취량 : 3~10 μg(120∼400 IU)","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 칼슘과 인이 흡수되고 이용되는데 필요\n(2) 뼈의 형성과 유지에 필요\n(3) 골다공증발생 위험 감소에 도움을 줌","IFTKN_ATNT_MATR_CN":"(가) 고칼슘혈증이 있거나 의약품 복용 시 전문가와 상담할 것\n(나) 이상사례 발생 시 섭취를 중단하고 전문가와 상담할 것"}]

## db_126_1c3ZmUXrc8A / c18 / OVERCLAIM

영상 그룹: overclaim_2
제품: 수퍼바이오틱스 콜레스테롤 / (주)서흥 / DB ID 23601

수퍼바이오틱스 콜레스테롤 제품은 일주일 만에 혈중 콜레스테롤을 50% 줄이는 효과가 확실하다.

**판정 근거**

제품 및 원료의 인정 기능성에는 이 기간·수치·구체적 결과를 보장하는 문장이 없음. 질병 치료나 의약품 대체가 아니라, 인정 범위를 넘는 과장된 효과로 구성함. NLI 점수를 정답으로 사용하지 않으며 실제 NLI의 OVERCLAIM 출력은 별도 평가 대상임.

**DB 원문: products:23601.main_functionality**

> 유산균복합물(AB-LIFE) : (국문) 혈중 콜레스테롤 개선에 도움을 줄 수 있음, (영문) May help to reduce blood cholesterol levels,  유산균 증식 및 유해균 억제에 도움을 줄 수 있음, 배변활동 원활에 도움을 줄 수 있음, 장 건강에 도움을 줄 수 있음

**DB 원문: products:23601.RAWMTRL_STD_INFO**

> [{"RCOGN_NO":"2022-15","RAWMTRL_NM":"유산균복합물(AB-LIFE®)(기능성원료인정제2022-15호)","DAY_INTK_LOWLIMIT":"1200000000","DAY_INTK_HIGHLIMIT":"1200000000","INTK_UNIT":"CFU","INTK_MEMO":"제2022-15호","SKLL_IX_IRDNT_RAWMTRL":"프로바이오틱스 수","PRIMARY_FNCLTY":"(국문) 혈중 콜레스테롤 개선에 도움을 줄 수 있음 (영문) May help to reduce blood cholesterol levels","IFTKN_ATNT_MATR_CN":"(1) 질환이 있거나 의약품 복용 시 전문가와 상담할 것 (2) 특정질환(알레르기 체질, 단장증후군 등)이 있는 분은 섭취에 주의할 것 (3) 영·유아, 어린이, 임산부 및 수유부는 섭취에 주의할 것 (4) 어린이가 함부로 섭취하지 않도록 일일섭취량 방법을 지도할 것 (5) 이상사례 발생 시 섭취를 중단하고 전문가와 상담할 것 (6) 과다섭취에 주의할 것"}]

## db_126_1c3ZmUXrc8A / c19 / OVERCLAIM

영상 그룹: overclaim_2
제품: 수퍼바이오틱스 콜레스테롤 / (주)서흥 / DB ID 23601

수퍼바이오틱스 콜레스테롤 제품은 한 번만 먹어도 콜레스테롤 수치가 절반으로 떨어진다.

**판정 근거**

제품 및 원료의 인정 기능성에는 이 기간·수치·구체적 결과를 보장하는 문장이 없음. 질병 치료나 의약품 대체가 아니라, 인정 범위를 넘는 과장된 효과로 구성함. NLI 점수를 정답으로 사용하지 않으며 실제 NLI의 OVERCLAIM 출력은 별도 평가 대상임.

**DB 원문: products:23601.main_functionality**

> 유산균복합물(AB-LIFE) : (국문) 혈중 콜레스테롤 개선에 도움을 줄 수 있음, (영문) May help to reduce blood cholesterol levels,  유산균 증식 및 유해균 억제에 도움을 줄 수 있음, 배변활동 원활에 도움을 줄 수 있음, 장 건강에 도움을 줄 수 있음

**DB 원문: products:23601.RAWMTRL_STD_INFO**

> [{"RCOGN_NO":"2022-15","RAWMTRL_NM":"유산균복합물(AB-LIFE®)(기능성원료인정제2022-15호)","DAY_INTK_LOWLIMIT":"1200000000","DAY_INTK_HIGHLIMIT":"1200000000","INTK_UNIT":"CFU","INTK_MEMO":"제2022-15호","SKLL_IX_IRDNT_RAWMTRL":"프로바이오틱스 수","PRIMARY_FNCLTY":"(국문) 혈중 콜레스테롤 개선에 도움을 줄 수 있음 (영문) May help to reduce blood cholesterol levels","IFTKN_ATNT_MATR_CN":"(1) 질환이 있거나 의약품 복용 시 전문가와 상담할 것 (2) 특정질환(알레르기 체질, 단장증후군 등)이 있는 분은 섭취에 주의할 것 (3) 영·유아, 어린이, 임산부 및 수유부는 섭취에 주의할 것 (4) 어린이가 함부로 섭취하지 않도록 일일섭취량 방법을 지도할 것 (5) 이상사례 발생 시 섭취를 중단하고 전문가와 상담할 것 (6) 과다섭취에 주의할 것"}]

## db_127_kNWjguHhRs4 / c20 / VIOLATION

영상 그룹: violation_1
제품: 시그니처 파이토 이뮨 / 주식회사 네추럴웨이 포천 제2공장 / DB ID 24705

시그니처 파이토 이뮨의 등록된 하루 섭취량은 3병이다.

**판정 근거**

같은 하루 기준에서 DB는 1병이나 Claim은 3병으로 변경함.

**DB 원문: products:24705.intake_method**

> 뚜껑을 개봉하여 정제+연질캡슐을 액상과 함께 섭취 or 물과 함께 섭취(1일 1회, 1회 1병)

## db_132__MNYBmy24nk / c14 / OVERCLAIM

영상 그룹: overclaim_1
제품: 아이메가 rTG 오메가3 미니 / 코스맥스엔비티(주) / DB ID 25915

아이메가 rTG 오메가3 미니 제품은 일주일 만에 혈관 탄력성을 50% 높이는 효과가 확실하다.

**판정 근거**

제품 및 원료의 인정 기능성에는 이 기간·수치·구체적 결과를 보장하는 문장이 없음. 질병 치료나 의약품 대체가 아니라, 인정 범위를 넘는 과장된 효과로 구성함. NLI 점수를 정답으로 사용하지 않으며 실제 NLI의 OVERCLAIM 출력은 별도 평가 대상임.

**DB 원문: products:25915.main_functionality**

> [EPA 및 DHA 함유 유지] 혈중 중성지질 개선･혈행 개선에 도움을 줄 수 있음

**DB 원문: products:25915.RAWMTRL_STD_INFO**

> [{"RCOGN_NO":"","RAWMTRL_NM":"EPA 및 DHA 함유 유지","DAY_INTK_LOWLIMIT":"0.5","DAY_INTK_HIGHLIMIT":"2.24","INTK_UNIT":"g","INTK_MEMO":"건강기능식품의 기준 및 규격 2-16","SKLL_IX_IRDNT_RAWMTRL":"EPA와 DHA","PRIMARY_FNCLTY":"(1) 기능성 내용 : 혈중 중성지질 개선･혈행 개선･기억력 개선･건조한 눈을 개선하여 눈 건강에 도움을 줄 수 있음","IFTKN_ATNT_MATR_CN":"(가) 의약품(항응고제, 항혈소판제, 혈압강하제 등) 복용 시 전문가와 상담할 것\n(나) 개인에 따라 피부 관련 이상반응이 발생할 수 있음\n(다) 이상사례 발생 시 섭취를 중단하고 전문가와 상담할 것"}]

## db_135_0EkaCDWmB04 / c10 / OVERCLAIM

영상 그룹: overclaim_2
제품: 아이시안 루테인 지아잔틴 플러스 케어 / (주)서흥 / DB ID 25970

아이시안 루테인 지아잔틴 플러스 케어 제품은 일주일 만에 시력을 0.3 높여 주는 효과가 확실하다.

**판정 근거**

제품 및 원료의 인정 기능성에는 이 기간·수치·구체적 결과를 보장하는 문장이 없음. 질병 치료나 의약품 대체가 아니라, 인정 범위를 넘는 과장된 효과로 구성함. NLI 점수를 정답으로 사용하지 않으며 실제 NLI의 OVERCLAIM 출력은 별도 평가 대상임.

**DB 원문: products:25970.main_functionality**

> 루테인지아잔틴복합추출물(제2018-4호) : (국문) (1) 노화로 인해 감소될 수 있는 황반색소밀도를 유지하여 눈 건강에 도움을 줄 수 있음 (2) 건조한 눈을 개선하여 눈 건강에 도움을 줄 수 있음, (영문) (1) May help the eye health by maintaining the density of macular pigments which can be decreased by aging (2) May help to maintain eyes healthy by relieving dryness
> 아연 : (1) 정상적인 면역기능에 필요 (2) 정상적인 세포분열에 필요
> 비타민E : 항산화 작용을 하여 유해산소로부터 세포를 보호하는데 필요
> 비타민B6 : (1) 단백질 및 아미노산 이용에 필요 (2) 혈액의 호모시스테인 수준을 정상으로 유지하는데 필요
> 비타민B1 : 탄수화물과 에너지 대사에 필요
> 비타민B2 : 체내 에너지 생성에 필요
> 비타민A : (1) 어두운 곳에서 시각 적응을 위해 필요 (2) 피부와 점막을 형성하고 기능을 유지하는데 필요 (3) 상피세포의 성장과 발달에 필요

**DB 원문: products:25970.RAWMTRL_STD_INFO**

> [{"RCOGN_NO":"","RAWMTRL_NM":"비타민 A","DAY_INTK_LOWLIMIT":"210","DAY_INTK_HIGHLIMIT":"1000","INTK_UNIT":"μg RAE","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 어두운 곳에서 시각 적응을 위해 필요\n(2) 피부와 점막을 형성하고 기능을 유지하는데 필요\n(3) 상피세포의 성장과 발달에 필요","IFTKN_ATNT_MATR_CN":""},{"RCOGN_NO":"","RAWMTRL_NM":"비타민 B2","DAY_INTK_LOWLIMIT":"0.42","DAY_INTK_HIGHLIMIT":"40","INTK_UNIT":"mg","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 체내 에너지 생성에 필요","IFTKN_ATNT_MATR_CN":"(1) 이상사례 발생 시 섭취를 중단하고 전문가와 상담할 것"},{"RCOGN_NO":"","RAWMTRL_NM":"비타민 B1","DAY_INTK_LOWLIMIT":"0.36","DAY_INTK_HIGHLIMIT":"100","INTK_UNIT":"mg","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 탄수화물과 에너지 대사에 필요","IFTKN_ATNT_MATR_CN":"(1) 이상사례 발생 시 섭취를 중단하고 전문가와 상담할 것"},{"RCOGN_NO":"","RAWMTRL_NM":"비타민 B6","DAY_INTK_LOWLIMIT":"0.45","DAY_INTK_HIGHLIMIT":"67","INTK_UNIT":"mg","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 단백질 및 아미노산 이용에 필요\n(2) 혈액의 호모시스테인 수준을 정상으로 유지하는데 필요","IFTKN_ATNT_MATR_CN":"(1) 손발 따끔거림, 작열감 또는 저림 등의 이상사례 발생 시 섭취를 중단하고 전문가와 상담할 것"},{"RCOGN_NO":"","RAWMTRL_NM":"비타민 E","DAY_INTK_LOWLIMIT":"3.3","DAY_INTK_HIGHLIMIT":"400","INTK_UNIT":"mg α-TE","INTK_MEMO":"2021.7.11: 기능성 내용 변경","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"항산화 작용을 하여 유해산소로부터 세포를 보호하는데 필요","IFTKN_ATNT_MATR_CN":""},{"RCOGN_NO":"","RAWMTRL_NM":"아연","DAY_INTK_LOWLIMIT":"2.55","DAY_INTK_HIGHLIMIT":"12","INTK_UNIT":"mg","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 정상적인 면역기능에 필요\n(2) 정상적인 세포분열에 필요","IFTKN_ATNT_MATR_CN":""},{"RCOGN_NO":"2018-4","RAWMTRL_NM":"루테인지아잔틴복합추출물(기능성원료인정제2018-4호)","DAY_INTK_LOWLIMIT":"10","DAY_INTK_HIGHLIMIT":"20","INTK_UNIT":"mg/일","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"루테인(Lutein), 총지아잔틴(Total Zeaxanthin)","PRIMARY_FNCLTY":"(국문) ① 노화로 인해 감소될 수 있는 황반색소밀도를 유지하여 눈 건강에 도움을 줄 수 있음\n② 건조한 눈을 개선하여 눈 건강에 도움을 줄 수 있음\n(영문) ① May help the eye health by maintaining the density of macular pigments which can be decreased by aging\n② May help to maintain eyes healthy by relieving dryness","IFTKN_ATNT_MATR_CN":"(1) 영유아, 어린이, 임산부 및 수유부는 섭취를 피할 것\n(2) 흡연자는 섭취 시 전문가와 상담할 것\n(3) 과다 섭취 시 일시적으로 피부가 황색으로 변할 수 있음\n(4) 이상사례 발생 시 섭취를 중단하고 전문가와 상담할 것"}]

## db_135_0EkaCDWmB04 / c11 / OVERCLAIM

영상 그룹: overclaim_2
제품: 아이시안 루테인 지아잔틴 플러스 케어 / (주)서흥 / DB ID 25970

아이시안 루테인 지아잔틴 플러스 케어 제품은 단 하루 만에 눈의 피로를 90%까지 확실히 줄인다.

**판정 근거**

제품 및 원료의 인정 기능성에는 이 기간·수치·구체적 결과를 보장하는 문장이 없음. 질병 치료나 의약품 대체가 아니라, 인정 범위를 넘는 과장된 효과로 구성함. NLI 점수를 정답으로 사용하지 않으며 실제 NLI의 OVERCLAIM 출력은 별도 평가 대상임.

**DB 원문: products:25970.main_functionality**

> 루테인지아잔틴복합추출물(제2018-4호) : (국문) (1) 노화로 인해 감소될 수 있는 황반색소밀도를 유지하여 눈 건강에 도움을 줄 수 있음 (2) 건조한 눈을 개선하여 눈 건강에 도움을 줄 수 있음, (영문) (1) May help the eye health by maintaining the density of macular pigments which can be decreased by aging (2) May help to maintain eyes healthy by relieving dryness
> 아연 : (1) 정상적인 면역기능에 필요 (2) 정상적인 세포분열에 필요
> 비타민E : 항산화 작용을 하여 유해산소로부터 세포를 보호하는데 필요
> 비타민B6 : (1) 단백질 및 아미노산 이용에 필요 (2) 혈액의 호모시스테인 수준을 정상으로 유지하는데 필요
> 비타민B1 : 탄수화물과 에너지 대사에 필요
> 비타민B2 : 체내 에너지 생성에 필요
> 비타민A : (1) 어두운 곳에서 시각 적응을 위해 필요 (2) 피부와 점막을 형성하고 기능을 유지하는데 필요 (3) 상피세포의 성장과 발달에 필요

**DB 원문: products:25970.RAWMTRL_STD_INFO**

> [{"RCOGN_NO":"","RAWMTRL_NM":"비타민 A","DAY_INTK_LOWLIMIT":"210","DAY_INTK_HIGHLIMIT":"1000","INTK_UNIT":"μg RAE","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 어두운 곳에서 시각 적응을 위해 필요\n(2) 피부와 점막을 형성하고 기능을 유지하는데 필요\n(3) 상피세포의 성장과 발달에 필요","IFTKN_ATNT_MATR_CN":""},{"RCOGN_NO":"","RAWMTRL_NM":"비타민 B2","DAY_INTK_LOWLIMIT":"0.42","DAY_INTK_HIGHLIMIT":"40","INTK_UNIT":"mg","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 체내 에너지 생성에 필요","IFTKN_ATNT_MATR_CN":"(1) 이상사례 발생 시 섭취를 중단하고 전문가와 상담할 것"},{"RCOGN_NO":"","RAWMTRL_NM":"비타민 B1","DAY_INTK_LOWLIMIT":"0.36","DAY_INTK_HIGHLIMIT":"100","INTK_UNIT":"mg","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 탄수화물과 에너지 대사에 필요","IFTKN_ATNT_MATR_CN":"(1) 이상사례 발생 시 섭취를 중단하고 전문가와 상담할 것"},{"RCOGN_NO":"","RAWMTRL_NM":"비타민 B6","DAY_INTK_LOWLIMIT":"0.45","DAY_INTK_HIGHLIMIT":"67","INTK_UNIT":"mg","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 단백질 및 아미노산 이용에 필요\n(2) 혈액의 호모시스테인 수준을 정상으로 유지하는데 필요","IFTKN_ATNT_MATR_CN":"(1) 손발 따끔거림, 작열감 또는 저림 등의 이상사례 발생 시 섭취를 중단하고 전문가와 상담할 것"},{"RCOGN_NO":"","RAWMTRL_NM":"비타민 E","DAY_INTK_LOWLIMIT":"3.3","DAY_INTK_HIGHLIMIT":"400","INTK_UNIT":"mg α-TE","INTK_MEMO":"2021.7.11: 기능성 내용 변경","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"항산화 작용을 하여 유해산소로부터 세포를 보호하는데 필요","IFTKN_ATNT_MATR_CN":""},{"RCOGN_NO":"","RAWMTRL_NM":"아연","DAY_INTK_LOWLIMIT":"2.55","DAY_INTK_HIGHLIMIT":"12","INTK_UNIT":"mg","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 정상적인 면역기능에 필요\n(2) 정상적인 세포분열에 필요","IFTKN_ATNT_MATR_CN":""},{"RCOGN_NO":"2018-4","RAWMTRL_NM":"루테인지아잔틴복합추출물(기능성원료인정제2018-4호)","DAY_INTK_LOWLIMIT":"10","DAY_INTK_HIGHLIMIT":"20","INTK_UNIT":"mg/일","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"루테인(Lutein), 총지아잔틴(Total Zeaxanthin)","PRIMARY_FNCLTY":"(국문) ① 노화로 인해 감소될 수 있는 황반색소밀도를 유지하여 눈 건강에 도움을 줄 수 있음\n② 건조한 눈을 개선하여 눈 건강에 도움을 줄 수 있음\n(영문) ① May help the eye health by maintaining the density of macular pigments which can be decreased by aging\n② May help to maintain eyes healthy by relieving dryness","IFTKN_ATNT_MATR_CN":"(1) 영유아, 어린이, 임산부 및 수유부는 섭취를 피할 것\n(2) 흡연자는 섭취 시 전문가와 상담할 것\n(3) 과다 섭취 시 일시적으로 피부가 황색으로 변할 수 있음\n(4) 이상사례 발생 시 섭취를 중단하고 전문가와 상담할 것"}]

## db_136_40OyEPJBj1E / c14 / VIOLATION

영상 그룹: violation_1
제품: 아이원 루테인지아잔틴 미니 / 코스맥스바이오(주) / DB ID 26056

아이원 루테인지아잔틴 미니 제품은 황반변성을 치료한다.

**판정 근거**

건강 보조 기능을 질병 예방·치료 또는 의약품 대체 주장으로 바꿈. 주간 발표의 질병·의약품 주장 기준에 따른 정답임.

**DB 원문: products:26056.main_functionality**

> 노화로 인해 감소될 수 있는 황반색소밀도를 유지하여 눈 건강에 도움을 줄 수 있음, 건조한 눈을 개선하여 눈 건강에 도움을 줄 수 있음.

## db_138_PTmYGvz-n84 / c10 / OVERCLAIM

영상 그룹: overclaim_1
제품: 아이커 / 종근당건강(주) / DB ID 26086

아이커 제품은 한 달 만에 아이 키가 5cm 더 크는 효과가 확실하다.

**판정 근거**

제품 및 원료의 인정 기능성에는 이 기간·수치·구체적 결과를 보장하는 문장이 없음. 질병 치료나 의약품 대체가 아니라, 인정 범위를 넘는 과장된 효과로 구성함. NLI 점수를 정답으로 사용하지 않으며 실제 NLI의 OVERCLAIM 출력은 별도 평가 대상임.

**DB 원문: products:26086.main_functionality**

> [황기추출물 등 복합물] (국문) 어린이 키성장에 도움을 줄 수 있음 (영문) May help to children grow taller
> [폴리감마글루탐산] ①체내 칼슘흡수 촉진에 도움을 줄 수 있음
> [비타민A] ①어두운 곳에서 시각 적응을 위해 필요②피부와 점막을 형성하고 기능을 유지하는데 필요③상피세포의 성장과 발달에 필요
> [비타민E] ①항산화 작용을 하여 유해산소로부터 세포를 보호하는데 필요
> [비타민D]①칼슘과 인이 흡수되고 이용되는데 필요②뼈의 형성과 유지에 필요③골다공증발생 위험 감소에 도움을 줌
> [비타민K] ①정상적인 혈액응고에 필요②뼈의 구성에 필요
> [비타민B1] ①탄수화물과 에너지 대사에 필요
> [비타민B2] ①체내 에너지 생성에 필요
> [비타민B12] ①정상적인 엽산 대사에 필요
> [칼슘] ①뼈와 치아 형성에 필요②신경과 근육 기능 유지에 필요③정상적인 혈액응고에 필요④골다공증발생 위험 감소에 도움을 줌
> [아연] ①정상적인 면역기능에 필요②정상적인 세포분열에 필요
> [나이아신] ①체내 에너지 생성에 필요
> [망간] ①뼈 형성에 필요②에너지 이용에 필요③유해산소로부터 세포를 보호하는데 필요
> [몰리브덴] ①산화·환원 효소의 활성에 필요

**DB 원문: products:26086.RAWMTRL_STD_INFO**

> [{"RCOGN_NO":"","RAWMTRL_NM":"비타민 D","DAY_INTK_LOWLIMIT":"0.003","DAY_INTK_HIGHLIMIT":"0.01","INTK_UNIT":"mg","INTK_MEMO":"일일섭취량 : 3~10 μg(120∼400 IU)","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 칼슘과 인이 흡수되고 이용되는데 필요\n(2) 뼈의 형성과 유지에 필요\n(3) 골다공증발생 위험 감소에 도움을 줌","IFTKN_ATNT_MATR_CN":"(가) 고칼슘혈증이 있거나 의약품 복용 시 전문가와 상담할 것\n(나) 이상사례 발생 시 섭취를 중단하고 전문가와 상담할 것"},{"RCOGN_NO":"","RAWMTRL_NM":"비타민 E","DAY_INTK_LOWLIMIT":"3.3","DAY_INTK_HIGHLIMIT":"400","INTK_UNIT":"mg α-TE","INTK_MEMO":"2021.7.11: 기능성 내용 변경","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"항산화 작용을 하여 유해산소로부터 세포를 보호하는데 필요","IFTKN_ATNT_MATR_CN":""},{"RCOGN_NO":"","RAWMTRL_NM":"비타민 A","DAY_INTK_LOWLIMIT":"210","DAY_INTK_HIGHLIMIT":"1000","INTK_UNIT":"μg RAE","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 어두운 곳에서 시각 적응을 위해 필요\n(2) 피부와 점막을 형성하고 기능을 유지하는데 필요\n(3) 상피세포의 성장과 발달에 필요","IFTKN_ATNT_MATR_CN":""},{"RCOGN_NO":"","RAWMTRL_NM":"폴리감마글루탐산","DAY_INTK_LOWLIMIT":"60","DAY_INTK_HIGHLIMIT":"70","INTK_UNIT":"mg","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"폴리감마글루탐산","PRIMARY_FNCLTY":"① 체내 칼슘흡수 촉진에 도움을 줄 수 있음","IFTKN_ATNT_MATR_CN":""},{"RCOGN_NO":"2014-40","RAWMTRL_NM":"황기추출물 등 복합물(HT042)(기능성원료인정제2014-40호)","DAY_INTK_LOWLIMIT":"1.5","DAY_INTK_HIGHLIMIT":"1.5","INTK_UNIT":"g/일","INTK_MEMO":"제2014-40호","SKLL_IX_IRDNT_RAWMTRL":"Formononetin, Shanzhiside methyl ester, Eleutheroside E","PRIMARY_FNCLTY":"(국문) 어린이 키성장에 도움을 줄 수 있음\n(영문) May help to children grow taller","IFTKN_ATNT_MATR_CN":"(1) 임산부 및 수유부는 섭취를 피할 것\n(2) 특정원료에 알레르기가 있거나 장기간 또는 의약품 복용시 전문가와 상담할 것\n(3) 이상사례 발생 시 섭취를 중단하고 전문가와 상담할 것\n(4) 키 성장에는 충분한 영양섭취, 적절한 수면, 건강한 생활습관ㆍ운동을 병행하여야 함"},{"RCOGN_NO":"","RAWMTRL_NM":"칼슘","DAY_INTK_LOWLIMIT":"210","DAY_INTK_HIGHLIMIT":"800","INTK_UNIT":"mg","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 뼈와 치아 형성에 필요\n(2) 신경과 근육 기능 유지에 필요\n(3) 정상적인 혈액응고에 필요\n(4) 골다공증발생 위험 감소에 도움을 줌","IFTKN_ATNT_MATR_CN":""},{"RCOGN_NO":"","RAWMTRL_NM":"비타민 B12","DAY_INTK_LOWLIMIT":"0.00072","DAY_INTK_HIGHLIMIT":"2","INTK_UNIT":"mg","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 정상적인 엽산 대사에 필요","IFTKN_ATNT_MATR_CN":"(1) 이상사례 발생 시 섭취를 중단하고 전문가와 상담할 것"},{"RCOGN_NO":"","RAWMTRL_NM":"비타민 B2","DAY_INTK_LOWLIMIT":"0.42","DAY_INTK_HIGHLIMIT":"40","INTK_UNIT":"mg","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 체내 에너지 생성에 필요","IFTKN_ATNT_MATR_CN":"(1) 이상사례 발생 시 섭취를 중단하고 전문가와 상담할 것"},{"RCOGN_NO":"","RAWMTRL_NM":"비타민 B1","DAY_INTK_LOWLIMIT":"0.36","DAY_INTK_HIGHLIMIT":"100","INTK_UNIT":"mg","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 탄수화물과 에너지 대사에 필요","IFTKN_ATNT_MATR_CN":"(1) 이상사례 발생 시 섭취를 중단하고 전문가와 상담할 것"},{"RCOGN_NO":"","RAWMTRL_NM":"비타민 K","DAY_INTK_LOWLIMIT":"0.021","DAY_INTK_HIGHLIMIT":"1","INTK_UNIT":"mg","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 정상적인 혈액응고에 필요\n(2) 뼈의 구성에 필요","IFTKN_ATNT_MATR_CN":"(1) 항응고제 등 복용 시 전문가와 상담할 것\n(2) 이상사례 발생 시 섭취를 중단하고 전문가와 상담할 것"},{"RCOGN_NO":"","RAWMTRL_NM":"몰리브덴","DAY_INTK_LOWLIMIT":"0.0075","DAY_INTK_HIGHLIMIT":"0.23","INTK_UNIT":"mg","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 산화·환원 효소의 활성에 필요","IFTKN_ATNT_MATR_CN":""},{"RCOGN_NO":"","RAWMTRL_NM":"망간","DAY_INTK_LOWLIMIT":"0.9","DAY_INTK_HIGHLIMIT":"3.5","INTK_UNIT":"mg","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 뼈 형성에 필요\n(2) 에너지 이용에 필요\n(3) 유해산소로부터 세포를 보호하는데 필요","IFTKN_ATNT_MATR_CN":""},{"RCOGN_NO":"","RAWMTRL_NM":"나이아신","DAY_INTK_LOWLIMIT":"4.5","DAY_INTK_HIGHLIMIT":"670","INTK_UNIT":"mg","INTK_MEMO":"니코틴산 4.5～23 mg, 니코틴산아미드 4.5～670 mg","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 체내 에너지 생성에 필요","IFTKN_ATNT_MATR_CN":""},{"RCOGN_NO":"","RAWMTRL_NM":"아연","DAY_INTK_LOWLIMIT":"2.55","DAY_INTK_HIGHLIMIT":"12","INTK_UNIT":"mg","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 정상적인 면역기능에 필요\n(2) 정상적인 세포분열에 필요","IFTKN_ATNT_MATR_CN":""}]

## db_142_nUgOnoNbEfU / c33 / OVERCLAIM

영상 그룹: overclaim_2
제품: 아이클리어 루테인지아잔틴 / 종근당건강(주) / DB ID 26126

아이클리어 루테인지아잔틴 제품은 일주일 만에 시력을 0.3 높여 주는 효과가 확실하다.

**판정 근거**

제품 및 원료의 인정 기능성에는 이 기간·수치·구체적 결과를 보장하는 문장이 없음. 질병 치료나 의약품 대체가 아니라, 인정 범위를 넘는 과장된 효과로 구성함. NLI 점수를 정답으로 사용하지 않으며 실제 NLI의 OVERCLAIM 출력은 별도 평가 대상임.

**DB 원문: products:26126.main_functionality**

> 루테인지아잔틴복합추출물 :(국문) 노화로 인해 감소될 수 있는 황반색소밀도를 유지하여 눈 건강에 도움을 줄 수 있음
> (영문) May help the eye health by maintaining the density of macular pigments which can be decreased by aging
> 
> 비타민E : ①항산화 작용을 하여 유해산소로부터 세포를 보호하는데 필요
> 
> 아연 : ①정상적인 면역기능에 필요②정상적인 세포분열에 필요
> 
> 비타민A : ①어두운 곳에서 시각 적응을 위해 필요②피부와 점막을 형성하고 기능을 유지하는데 필요③상피세포의 성장과 발달에 필요
> 
> 비타민B6 : ①단백질 및 아미노산 이용에 필요②혈액의 호모시스테인 수준을 정상으로 유지하는데 필요
> 
> 비타민B1 : ①탄수화물과 에너지 대사에 필요
> 
> 비타민B2 : ①체내 에너지 생성에 필요
> 
> 비타민D : ①칼슘과 인이 흡수되고 이용되는데 필요②뼈의 형성과 유지에 필요③골다공증발생 위험 감소에 도움을 줌

**DB 원문: products:26126.RAWMTRL_STD_INFO**

> [{"RCOGN_NO":"","RAWMTRL_NM":"아연","DAY_INTK_LOWLIMIT":"2.55","DAY_INTK_HIGHLIMIT":"12","INTK_UNIT":"mg","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 정상적인 면역기능에 필요\n(2) 정상적인 세포분열에 필요","IFTKN_ATNT_MATR_CN":""},{"RCOGN_NO":"","RAWMTRL_NM":"비타민 B6","DAY_INTK_LOWLIMIT":"0.45","DAY_INTK_HIGHLIMIT":"67","INTK_UNIT":"mg","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 단백질 및 아미노산 이용에 필요\n(2) 혈액의 호모시스테인 수준을 정상으로 유지하는데 필요","IFTKN_ATNT_MATR_CN":"(1) 손발 따끔거림, 작열감 또는 저림 등의 이상사례 발생 시 섭취를 중단하고 전문가와 상담할 것"},{"RCOGN_NO":"","RAWMTRL_NM":"비타민 B2","DAY_INTK_LOWLIMIT":"0.42","DAY_INTK_HIGHLIMIT":"40","INTK_UNIT":"mg","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 체내 에너지 생성에 필요","IFTKN_ATNT_MATR_CN":"(1) 이상사례 발생 시 섭취를 중단하고 전문가와 상담할 것"},{"RCOGN_NO":"","RAWMTRL_NM":"비타민 B1","DAY_INTK_LOWLIMIT":"0.36","DAY_INTK_HIGHLIMIT":"100","INTK_UNIT":"mg","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 탄수화물과 에너지 대사에 필요","IFTKN_ATNT_MATR_CN":"(1) 이상사례 발생 시 섭취를 중단하고 전문가와 상담할 것"},{"RCOGN_NO":"","RAWMTRL_NM":"비타민 D","DAY_INTK_LOWLIMIT":"0.003","DAY_INTK_HIGHLIMIT":"0.01","INTK_UNIT":"mg","INTK_MEMO":"일일섭취량 : 3~10 μg(120∼400 IU)","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 칼슘과 인이 흡수되고 이용되는데 필요\n(2) 뼈의 형성과 유지에 필요\n(3) 골다공증발생 위험 감소에 도움을 줌","IFTKN_ATNT_MATR_CN":"(가) 고칼슘혈증이 있거나 의약품 복용 시 전문가와 상담할 것\n(나) 이상사례 발생 시 섭취를 중단하고 전문가와 상담할 것"},{"RCOGN_NO":"","RAWMTRL_NM":"비타민 E","DAY_INTK_LOWLIMIT":"3.3","DAY_INTK_HIGHLIMIT":"400","INTK_UNIT":"mg α-TE","INTK_MEMO":"2021.7.11: 기능성 내용 변경","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"항산화 작용을 하여 유해산소로부터 세포를 보호하는데 필요","IFTKN_ATNT_MATR_CN":""},{"RCOGN_NO":"","RAWMTRL_NM":"비타민 A","DAY_INTK_LOWLIMIT":"210","DAY_INTK_HIGHLIMIT":"1000","INTK_UNIT":"μg RAE","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 어두운 곳에서 시각 적응을 위해 필요\n(2) 피부와 점막을 형성하고 기능을 유지하는데 필요\n(3) 상피세포의 성장과 발달에 필요","IFTKN_ATNT_MATR_CN":""},{"RCOGN_NO":"2018-4","RAWMTRL_NM":"루테인지아잔틴복합추출물(기능성원료인정제2018-4호)","DAY_INTK_LOWLIMIT":"10","DAY_INTK_HIGHLIMIT":"20","INTK_UNIT":"mg/일","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"루테인(Lutein), 총지아잔틴(Total Zeaxanthin)","PRIMARY_FNCLTY":"(국문) ① 노화로 인해 감소될 수 있는 황반색소밀도를 유지하여 눈 건강에 도움을 줄 수 있음\n② 건조한 눈을 개선하여 눈 건강에 도움을 줄 수 있음\n(영문) ① May help the eye health by maintaining the density of macular pigments which can be decreased by aging\n② May help to maintain eyes healthy by relieving dryness","IFTKN_ATNT_MATR_CN":"(1) 영유아, 어린이, 임산부 및 수유부는 섭취를 피할 것\n(2) 흡연자는 섭취 시 전문가와 상담할 것\n(3) 과다 섭취 시 일시적으로 피부가 황색으로 변할 수 있음\n(4) 이상사례 발생 시 섭취를 중단하고 전문가와 상담할 것"}]

## db_142_nUgOnoNbEfU / c34 / OVERCLAIM

영상 그룹: overclaim_2
제품: 아이클리어 빌베리 / (주)서흥 / DB ID 26132

아이클리어 빌베리 제품은 단 하루 만에 눈의 피로를 90%까지 확실히 줄인다.

**판정 근거**

제품 및 원료의 인정 기능성에는 이 기간·수치·구체적 결과를 보장하는 문장이 없음. 질병 치료나 의약품 대체가 아니라, 인정 범위를 넘는 과장된 효과로 구성함. NLI 점수를 정답으로 사용하지 않으며 실제 NLI의 OVERCLAIM 출력은 별도 평가 대상임.

**DB 원문: products:26132.main_functionality**

> 빌베리 추출물 : 눈의 피로 개선에 도움을 줄 수 있음
> 
> 마리골드꽃추출물 : 노화로 인해 감소될 수 있는 황반색소밀도를 유지하여 눈 건강에 도움을 줄 수 있음
> 
> 비타민A : ①어두운 곳에서 시각 적응을 위해 필요②피부와 점막을 형성하고 기능을 유지하는데 필요③상피세포의 성장과 발달에 필요

**DB 원문: products:26132.RAWMTRL_STD_INFO**

> [{"RCOGN_NO":"","RAWMTRL_NM":"빌베리 추출물","DAY_INTK_LOWLIMIT":"160","DAY_INTK_HIGHLIMIT":"240","INTK_UNIT":"mg","INTK_MEMO":"빌베리 추출물로서 160~240 mg(안토시아노사이드로서 50~108 mg)","SKLL_IX_IRDNT_RAWMTRL":"총 안토시아노사이드(Anthocyanosides)","PRIMARY_FNCLTY":"① 눈의 피로 개선에 도움을 줄 수 있음","IFTKN_ATNT_MATR_CN":""},{"RCOGN_NO":"","RAWMTRL_NM":"마리골드꽃추출물","DAY_INTK_LOWLIMIT":"10","DAY_INTK_HIGHLIMIT":"20","INTK_UNIT":"mg","INTK_MEMO":"(24.12.23.) 섭취시주의사항, 주된기능성 현행화 / '24 신뢰성 확보","SKLL_IX_IRDNT_RAWMTRL":"루테인(Lutein)","PRIMARY_FNCLTY":"(1) 노화로 인해 감소될 수 있는 황반색소밀도를 유지하여 눈 건강에 도움을 줄 수 있음","IFTKN_ATNT_MATR_CN":"(가) 영‧유아, 어린이, 임산부 및 수유부는 섭취를 피할 것\n(나) 흡연자는 섭취 시 전문가와 상담할 것\n(다) 과다 섭취 시 일시적으로 피부가 황색으로 변할 수 있음\n(라) 이상사례 발생 시 섭취를 중단하고 전문가와 상담할 것"},{"RCOGN_NO":"","RAWMTRL_NM":"비타민 A","DAY_INTK_LOWLIMIT":"210","DAY_INTK_HIGHLIMIT":"1000","INTK_UNIT":"μg RAE","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 어두운 곳에서 시각 적응을 위해 필요\n(2) 피부와 점막을 형성하고 기능을 유지하는데 필요\n(3) 상피세포의 성장과 발달에 필요","IFTKN_ATNT_MATR_CN":""}]

## db_144_5ykRFN8-k8s / c08 / OVERCLAIM

영상 그룹: overclaim_1
제품: 아이클리어 루테인지아잔틴 아스타잔틴 / 종근당건강(주) / DB ID 26128

아이클리어 루테인지아잔틴 아스타잔틴 제품은 단 하루 만에 눈의 피로를 90%까지 확실히 줄인다.

**판정 근거**

제품 및 원료의 인정 기능성에는 이 기간·수치·구체적 결과를 보장하는 문장이 없음. 질병 치료나 의약품 대체가 아니라, 인정 범위를 넘는 과장된 효과로 구성함. NLI 점수를 정답으로 사용하지 않으며 실제 NLI의 OVERCLAIM 출력은 별도 평가 대상임.

**DB 원문: products:26128.main_functionality**

> [루테인지아잔틴복합추출물(제2018-4호)]
> (국문) 노화로 인해 감소될 수 있는 황반색소밀도를 유지하여 눈 건강에 도움을 줄 수 있음
> (영문) May help the eye health by maintaining the density of macular pigments which can be decreased by aging
> 
> [헤마토코쿠스추출물]
> ① 눈의 피로도 개선에 도움을 줄 수 있음
> 
> [비타민C]
> ① 결합조직 형성과 기능유지에 필요
> ② 철의 흡수에 필요
> ③ 항산화 작용을 하여 유해산소로부터 세포를 보호하는데 필요
> 
> [비타민E]
> ① 항산화 작용을 하여 유해산소로부터 세포를 보호하는데 필요
> 
> [아연]
> ① 정상적인 면역기능에 필요
> ② 정상적인 세포분열에 필요
> 
> [비타민A]
> ① 어두운 곳에서 시각 적응을 위해 필요
> ② 피부와 점막을 형성하고 기능을 유지하는데 필요
> ③ 상피세포의 성장과 발달에 필요

**DB 원문: products:26128.RAWMTRL_STD_INFO**

> [{"RCOGN_NO":"","RAWMTRL_NM":"헤마토코쿠스 추출물","DAY_INTK_LOWLIMIT":"4","DAY_INTK_HIGHLIMIT":"12","INTK_UNIT":"mg","INTK_MEMO":"(24.12.23.) 섭취시주의사항, 주된기능성 현행화 / '24 신뢰성 확보","SKLL_IX_IRDNT_RAWMTRL":"아스타잔틴(Astaxanthin)","PRIMARY_FNCLTY":"(1) 기능성 내용 : 눈의 피로도 개선에 도움을 줄 수 있음","IFTKN_ATNT_MATR_CN":"(1) 과다 섭취 시 일시적으로 피부가 황색으로 변할 수 있음\n(2) β-카로틴의 흡수를 저해할 수 있음"},{"RCOGN_NO":"2018-4","RAWMTRL_NM":"루테인지아잔틴복합추출물(기능성원료인정제2018-4호)","DAY_INTK_LOWLIMIT":"10","DAY_INTK_HIGHLIMIT":"20","INTK_UNIT":"mg/일","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"루테인(Lutein), 총지아잔틴(Total Zeaxanthin)","PRIMARY_FNCLTY":"(국문) ① 노화로 인해 감소될 수 있는 황반색소밀도를 유지하여 눈 건강에 도움을 줄 수 있음\n② 건조한 눈을 개선하여 눈 건강에 도움을 줄 수 있음\n(영문) ① May help the eye health by maintaining the density of macular pigments which can be decreased by aging\n② May help to maintain eyes healthy by relieving dryness","IFTKN_ATNT_MATR_CN":"(1) 영유아, 어린이, 임산부 및 수유부는 섭취를 피할 것\n(2) 흡연자는 섭취 시 전문가와 상담할 것\n(3) 과다 섭취 시 일시적으로 피부가 황색으로 변할 수 있음\n(4) 이상사례 발생 시 섭취를 중단하고 전문가와 상담할 것"},{"RCOGN_NO":"","RAWMTRL_NM":"비타민 C","DAY_INTK_LOWLIMIT":"30","DAY_INTK_HIGHLIMIT":"1000","INTK_UNIT":"mg","INTK_MEMO":"21.7.11: 기능성 내용 변경 26.7.23 주의사항 변경","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 결합조직 형성과 기능유지에 필요\n(2) 철의 흡수에 필요\n(3) 항산화 작용을 하여 유해산소로부터 세포를 보호하는데 필요","IFTKN_ATNT_MATR_CN":"(1) 과량 섭취하지 않도록 주의할 것\n(2) 신장질환이 있는 경우 섭취 전 전문가와 상담할 것\n(3) 이상사례 발생 시 섭취를 중단하고 전문가와 상담할 것"},{"RCOGN_NO":"","RAWMTRL_NM":"아연","DAY_INTK_LOWLIMIT":"2.55","DAY_INTK_HIGHLIMIT":"12","INTK_UNIT":"mg","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 정상적인 면역기능에 필요\n(2) 정상적인 세포분열에 필요","IFTKN_ATNT_MATR_CN":""},{"RCOGN_NO":"","RAWMTRL_NM":"비타민 E","DAY_INTK_LOWLIMIT":"3.3","DAY_INTK_HIGHLIMIT":"400","INTK_UNIT":"mg α-TE","INTK_MEMO":"2021.7.11: 기능성 내용 변경","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"항산화 작용을 하여 유해산소로부터 세포를 보호하는데 필요","IFTKN_ATNT_MATR_CN":""},{"RCOGN_NO":"","RAWMTRL_NM":"비타민 A","DAY_INTK_LOWLIMIT":"210","DAY_INTK_HIGHLIMIT":"1000","INTK_UNIT":"μg RAE","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 어두운 곳에서 시각 적응을 위해 필요\n(2) 피부와 점막을 형성하고 기능을 유지하는데 필요\n(3) 상피세포의 성장과 발달에 필요","IFTKN_ATNT_MATR_CN":""}]

## db_145_7m0KUQskVVA / c23 / OVERCLAIM

영상 그룹: overclaim_1
제품: 아이클리어 올인원 / 종근당건강(주) / DB ID 26133

아이클리어 올인원 제품은 일주일 만에 시력을 0.3 높여 주는 효과가 확실하다.

**판정 근거**

제품 및 원료의 인정 기능성에는 이 기간·수치·구체적 결과를 보장하는 문장이 없음. 질병 치료나 의약품 대체가 아니라, 인정 범위를 넘는 과장된 효과로 구성함. NLI 점수를 정답으로 사용하지 않으며 실제 NLI의 OVERCLAIM 출력은 별도 평가 대상임.

**DB 원문: products:26133.main_functionality**

> [루테인지아잔틴복합추출물] 노화로 인해 감소될 수 있는 황반색소밀도를 유지하여 눈 건강에 도움을 줄 수 있음, 건조한 눈을 개선하여 눈 건강에 도움을 줄 수 있음
> [헤마토코쿠스추출물] 눈의 피로도 개선에 도움을 줄 수 있음
> [비타민C] 결합조직 형성과 기능유지에 필요, 철의 흡수에 필요, 항산화 작용을 하여 유해산소로부터 세포를 보호하는데 필요
> [비타민E] 항산화 작용을 하여 유해산소로부터 세포를 보호하는데 필요
> [아연] 정상적인 면역기능에 필요, 정상적인 세포분열에 필요

**DB 원문: products:26133.RAWMTRL_STD_INFO**

> [{"RCOGN_NO":"","RAWMTRL_NM":"비타민 E","DAY_INTK_LOWLIMIT":"3.3","DAY_INTK_HIGHLIMIT":"400","INTK_UNIT":"mg α-TE","INTK_MEMO":"2021.7.11: 기능성 내용 변경","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"항산화 작용을 하여 유해산소로부터 세포를 보호하는데 필요","IFTKN_ATNT_MATR_CN":""},{"RCOGN_NO":"","RAWMTRL_NM":"아연","DAY_INTK_LOWLIMIT":"2.55","DAY_INTK_HIGHLIMIT":"12","INTK_UNIT":"mg","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 정상적인 면역기능에 필요\n(2) 정상적인 세포분열에 필요","IFTKN_ATNT_MATR_CN":""},{"RCOGN_NO":"","RAWMTRL_NM":"비타민 C","DAY_INTK_LOWLIMIT":"30","DAY_INTK_HIGHLIMIT":"1000","INTK_UNIT":"mg","INTK_MEMO":"21.7.11: 기능성 내용 변경 26.7.23 주의사항 변경","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 결합조직 형성과 기능유지에 필요\n(2) 철의 흡수에 필요\n(3) 항산화 작용을 하여 유해산소로부터 세포를 보호하는데 필요","IFTKN_ATNT_MATR_CN":"(1) 과량 섭취하지 않도록 주의할 것\n(2) 신장질환이 있는 경우 섭취 전 전문가와 상담할 것\n(3) 이상사례 발생 시 섭취를 중단하고 전문가와 상담할 것"},{"RCOGN_NO":"2018-4","RAWMTRL_NM":"루테인지아잔틴복합추출물(기능성원료인정제2018-4호)","DAY_INTK_LOWLIMIT":"10","DAY_INTK_HIGHLIMIT":"20","INTK_UNIT":"mg/일","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"루테인(Lutein), 총지아잔틴(Total Zeaxanthin)","PRIMARY_FNCLTY":"(국문) ① 노화로 인해 감소될 수 있는 황반색소밀도를 유지하여 눈 건강에 도움을 줄 수 있음\n② 건조한 눈을 개선하여 눈 건강에 도움을 줄 수 있음\n(영문) ① May help the eye health by maintaining the density of macular pigments which can be decreased by aging\n② May help to maintain eyes healthy by relieving dryness","IFTKN_ATNT_MATR_CN":"(1) 영유아, 어린이, 임산부 및 수유부는 섭취를 피할 것\n(2) 흡연자는 섭취 시 전문가와 상담할 것\n(3) 과다 섭취 시 일시적으로 피부가 황색으로 변할 수 있음\n(4) 이상사례 발생 시 섭취를 중단하고 전문가와 상담할 것"},{"RCOGN_NO":"","RAWMTRL_NM":"헤마토코쿠스 추출물","DAY_INTK_LOWLIMIT":"4","DAY_INTK_HIGHLIMIT":"12","INTK_UNIT":"mg","INTK_MEMO":"(24.12.23.) 섭취시주의사항, 주된기능성 현행화 / '24 신뢰성 확보","SKLL_IX_IRDNT_RAWMTRL":"아스타잔틴(Astaxanthin)","PRIMARY_FNCLTY":"(1) 기능성 내용 : 눈의 피로도 개선에 도움을 줄 수 있음","IFTKN_ATNT_MATR_CN":"(1) 과다 섭취 시 일시적으로 피부가 황색으로 변할 수 있음\n(2) β-카로틴의 흡수를 저해할 수 있음"}]

## db_146_Z8k8OLPv2Zw / c20 / VIOLATION

영상 그룹: violation_2
제품: 아이클타임 / 주식회사 노바렉스 / DB ID 26136

아이클타임 제품은 성장호르몬 주사 대신 먹을 수 있다.

**판정 근거**

건강 보조 기능을 질병 예방·치료 또는 의약품 대체 주장으로 바꿈. 주간 발표의 질병·의약품 주장 기준에 따른 정답임.

**DB 원문: products:26136.main_functionality**

> (국문) 어린이 키성장에 도움을 줄 수 있음
> (영문) May help to children grow taller
> 면역력 증진･피로개선에 도움을 줄 수 있음
> 혈소판 응집억제를 통한 혈액흐름･기억력 개선･항산화에 도움을 줄 수 있음
> ①뼈와 치아 형성에 필요②신경과 근육 기능 유지에 필요③정상적인 혈액응고에 필요④골다공증발생 위험 감소에 도움을 줌

## db_146_Z8k8OLPv2Zw / c21 / VIOLATION

영상 그룹: violation_2
제품: 아이클타임 / 주식회사 노바렉스 / DB ID 26136

아이클타임 제품은 수유부도 먹을 수 있다.

**판정 근거**

광고와 DB가 모두 수유부 섭취를 말하며, 섭취 회피 조건에 직접 반하는 주장임.

**DB 원문: products:26136.intake_precautions**

> 특정질환, 특이체질, 알레르기체질, 임산부의 경우에는 간혹 개인에 따라 과민반응이 나타날 수 있으므로 원료를 확인하시고, 섭취전에 전문가와 상담하시기 바랍니다.
> 이상사례 발생시 섭취를 중단하고 전문가와 상담하시기 바랍니다.
> -임산부 및 수유부는 섭취를 피할 것
> -특정원료에 알레르기가 있거나 장기간 또는 의약품 복용시 전문가와 상담할 것
> -이상사례 발생 시 섭취를 중단하고 전문가와 상담할 것
> 당뇨치료제 및 혈액항응고제 복용 시 섭취에 주의
> 알레르기 체질 등은 개인에 따라 과민반응을 나타낼 수 있음
> 소비기한이 경과된 제품은 섭취하지 않도록 주의바랍니다.
> 제품 개봉 시 포장재에 의해 상처를 입을 위험이 있고, 개봉 시 내용물이 흘러나올 수 있으므로 취급 시 주의하십시오.

## db_160_qBFBNIBlB3Q / c37 / VIOLATION

영상 그룹: violation_1
제품: 안심뇨 / (주)서흥 / DB ID 26477

안심뇨 제품은 방광염을 치료한다.

**판정 근거**

건강 보조 기능을 질병 예방·치료 또는 의약품 대체 주장으로 바꿈. 주간 발표의 질병·의약품 주장 기준에 따른 정답임.

**DB 원문: products:26477.main_functionality**

> 호박씨추출물 등 복합물(제2014-43호) : (국문) 방광의 배뇨기능 개선에 도움을 줄 수 있음 (영문) May help to improve bladder control

## db_162_4jXlKg_Wko8 / c22 / OVERCLAIM

영상 그룹: overclaim_1
제품: 애터미 SCI 마이크로바이옴 / 콜마비앤에이치(주)음성공장 / DB ID 26939

애터미 SCI 마이크로바이옴 제품은 3일 만에 장내 유익균 수를 열 배로 늘리는 효과가 확실하다.

**판정 근거**

제품 및 원료의 인정 기능성에는 이 기간·수치·구체적 결과를 보장하는 문장이 없음. 질병 치료나 의약품 대체가 아니라, 인정 범위를 넘는 과장된 효과로 구성함. NLI 점수를 정답으로 사용하지 않으며 실제 NLI의 OVERCLAIM 출력은 별도 평가 대상임.

**DB 원문: products:26939.main_functionality**

> - 프로바이오틱스 : 유산균 증식 및 유해균 억제･배변활동 원활･장 건강에 도움을 줄 수 있음

**DB 원문: products:26939.RAWMTRL_STD_INFO**

> [{"RCOGN_NO":"","RAWMTRL_NM":"프로바이오틱스","DAY_INTK_LOWLIMIT":"100000000","DAY_INTK_HIGHLIMIT":"10000000000","INTK_UNIT":"CFU","INTK_MEMO":"21.7.11: 기능성 내용 변경","SKLL_IX_IRDNT_RAWMTRL":"생균","PRIMARY_FNCLTY":"유산균 증식 및 유해균 억제･배변활동 원활･장 건강에 도움을 줄 수 있음","IFTKN_ATNT_MATR_CN":"(가) 질환이 있거나 의약품 복용 시 전문가와 상담할 것\n(나) 알레르기 체질 등은 개인에 따라 과민반응을 나타낼 수 있음\n(다) 어린이가 함부로 섭취하지 않도록 일일섭취량 방법을 지도할 것\n(라) 이상사례 발생 시 섭취를 중단하고 전문가와 상담할 것"}]

## db_163_mIzLM0ZWBCU / c21 / VIOLATION

영상 그룹: violation_1
제품: 애터미 비건 조류 알티지 오메가3 / 콜마비앤에이치(주)음성공장 / DB ID 26990

애터미 비건 조류 알티지 오메가3 제품은 혈전증을 치료한다.

**판정 근거**

건강 보조 기능을 질병 예방·치료 또는 의약품 대체 주장으로 바꿈. 주간 발표의 질병·의약품 주장 기준에 따른 정답임.

**DB 원문: products:26990.main_functionality**

> - EPA 및 DHA 함유 유지 : 혈중 중성지질 개선･혈행 개선･건조한 눈을 개선하여 눈 건강에 도움을 줄 수 있음
> - 비타민 A : 어두운 곳에서 시각 적응을 위해 필요, 피부와 점막을 형성하고 기능을 유지하는데 필요, 상피세포의 성장과 발달에 필요
> - 비타민 E : 항산화 작용을 하여 유해산소로부터 세포를 보호하는데 필요,

## db_164_Gl7-zKA-GwI / c27 / VIOLATION

영상 그룹: violation_1
제품: 애터미 알티지 오메가3 / 콜마비앤에이치(주)음성공장 / DB ID 27050

애터미 알티지 오메가3의 등록된 하루 섭취량은 4캡슐이다.

**판정 근거**

같은 하루 기준에서 DB는 2캡슐이나 Claim은 4캡슐으로 변경함.

**DB 원문: products:27050.intake_method**

> 1일 1회, 1회 2캡슐을 충분한 물과 함께 섭취하십시오.

## db_167_pLQ_w6U6lx8 / c45 / OVERCLAIM

영상 그룹: overclaim_1
제품: 애터미헤모힘 / 콜마비앤에이치(주) / DB ID 27177

애터미헤모힘 제품은 3일 만에 면역세포 활성도를 세 배로 높이는 효과가 확실하다.

**판정 근거**

제품 및 원료의 인정 기능성에는 이 기간·수치·구체적 결과를 보장하는 문장이 없음. 질병 치료나 의약품 대체가 아니라, 인정 범위를 넘는 과장된 효과로 구성함. NLI 점수를 정답으로 사용하지 않으며 실제 NLI의 OVERCLAIM 출력은 별도 평가 대상임.

**DB 원문: products:27177.main_functionality**

> - 헤모힘 당귀등 혼합추출물(제2006-17호) : 면역기능 개선에 도움을 줄 수 있음, 피로개선에 도움을 줄 수 있음

**DB 원문: products:27177.RAWMTRL_STD_INFO**

> [{"RCOGN_NO":"2006-17","RAWMTRL_NM":"헤모힘 당귀등 혼합추출물(기능성원료인정제2006-17호)","DAY_INTK_LOWLIMIT":"20","DAY_INTK_HIGHLIMIT":"40","INTK_UNIT":"g/일","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"nodakenin, paeoniflorin, chlorogenic acid","PRIMARY_FNCLTY":"(국문) 면역기능 개선에 도움을 줄 수 있음 (영문) May help to improve immune function","IFTKN_ATNT_MATR_CN":"(1) 어린이, 임산부 및 수유부는 섭취를 피할 것 (2) 월경불순이나 출혈성 질환이 있는 여성의 경우 전문가와 상담할 것 (3) 항응고제 복용시 전문가와 상담할 것 (4) 알레르기 체질 등은 개인에 따라 과민반응을 나타낼 수 있음 (5) 이상사례 발생시 섭취를 중단하고 전문가와 상담할 것"}]

## db_179_mnl8jo33nD4 / c18 / VIOLATION

영상 그룹: violation_1_overclaim_1
제품: 야쿠르트 프로바이오틱스 / (주)알피바이오 / DB ID 27439

야쿠르트 프로바이오틱스 제품은 장염을 치료한다.

**판정 근거**

건강 보조 기능을 질병 예방·치료 또는 의약품 대체 주장으로 바꿈. 주간 발표의 질병·의약품 주장 기준에 따른 정답임.

**DB 원문: products:27439.main_functionality**

> [프로바이오틱스] 유산균 증식 및 유해균 억제･배변활동 원활･장 건강에 도움을 줄 수 있음
> [아연] ①정상적인 면역기능에 필요②정상적인 세포분열에 필요

## db_179_mnl8jo33nD4 / c19 / OVERCLAIM

영상 그룹: violation_1_overclaim_1
제품: 야쿠르트 프로바이오틱스 / (주)알피바이오 / DB ID 27439

야쿠르트 프로바이오틱스 제품은 3일 만에 장내 유익균 수를 열 배로 늘리는 효과가 확실하다.

**판정 근거**

제품 및 원료의 인정 기능성에는 이 기간·수치·구체적 결과를 보장하는 문장이 없음. 질병 치료나 의약품 대체가 아니라, 인정 범위를 넘는 과장된 효과로 구성함. NLI 점수를 정답으로 사용하지 않으며 실제 NLI의 OVERCLAIM 출력은 별도 평가 대상임.

**DB 원문: products:27439.main_functionality**

> [프로바이오틱스] 유산균 증식 및 유해균 억제･배변활동 원활･장 건강에 도움을 줄 수 있음
> [아연] ①정상적인 면역기능에 필요②정상적인 세포분열에 필요

**DB 원문: products:27439.RAWMTRL_STD_INFO**

> [{"RCOGN_NO":"","RAWMTRL_NM":"아연","DAY_INTK_LOWLIMIT":"2.55","DAY_INTK_HIGHLIMIT":"12","INTK_UNIT":"mg","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 정상적인 면역기능에 필요\n(2) 정상적인 세포분열에 필요","IFTKN_ATNT_MATR_CN":""},{"RCOGN_NO":"","RAWMTRL_NM":"프로바이오틱스","DAY_INTK_LOWLIMIT":"100000000","DAY_INTK_HIGHLIMIT":"10000000000","INTK_UNIT":"CFU","INTK_MEMO":"21.7.11: 기능성 내용 변경","SKLL_IX_IRDNT_RAWMTRL":"생균","PRIMARY_FNCLTY":"유산균 증식 및 유해균 억제･배변활동 원활･장 건강에 도움을 줄 수 있음","IFTKN_ATNT_MATR_CN":"(가) 질환이 있거나 의약품 복용 시 전문가와 상담할 것\n(나) 알레르기 체질 등은 개인에 따라 과민반응을 나타낼 수 있음\n(다) 어린이가 함부로 섭취하지 않도록 일일섭취량 방법을 지도할 것\n(라) 이상사례 발생 시 섭취를 중단하고 전문가와 상담할 것"}]

## db_181_NIjAo7fh-Kg / c26 / VIOLATION

영상 그룹: violation_1
제품: 에버콜라겐 인앤업 플러스 / 주식회사 노바렉스 / DB ID 27876

에버콜라겐 인앤업 플러스 제품은 수유부도 먹을 수 있다.

**판정 근거**

광고와 DB가 모두 수유부 섭취를 말하며, 섭취 회피 조건에 직접 반하는 주장임.

**DB 원문: products:27876.intake_precautions**

> 특정질환, 특이체질, 알레르기체질, 임산부의 경우에는 간혹 개인에 따라 과민반응이 나타날 수 있으므로 원료를 확인하시고, 섭취전에 전문가와 상담하시기 바랍니다.
> 제품 개봉 또는 섭취 시 포장재에 의해 다칠 우려가 있으니 주의하시기 바랍니다.
> 이상 사례 발생 시 섭취를 중단하고 전문가와 상담할 것
> 흡습이 잘되는 원료가 포함되어 병 내 손 삽입 금지
> 제품 내 습기제거제는 섭취 금지
> [저분자콜라겐펩타이드(제2013-30호)]
> 영·유아, 어린이, 임산부 및 수유부는 섭취를 피할 것
> 알레르기 체질 등은 개인에 따라 과민 반응을 나타낼 수 있음
> [비타민 C]
> 과량 섭취하지 않도록 주의할 것
> 신장질환이 있는 경우 섭취 전 전문가와 상담할 것
> [비타민 D] 고칼슘혈증이 있거나 의약품 복용 시 전문가와 상담할 것

## db_183_sofweMTrfjw / c21 / VIOLATION

영상 그룹: violation_1
제품: 에버콜라겐 타임 / 주식회사 노바렉스 / DB ID 27887

에버콜라겐 타임의 등록된 하루 섭취량은 3포이다.

**판정 근거**

같은 하루 기준에서 DB는 1포이나 Claim은 3포으로 변경함.

**DB 원문: products:27887.intake_method**

> 1일 1회, 1회 1포(1포당 3000mg)를 섭취하십시오.

## db_195_-RaTg6NEMZ0 / c12 / VIOLATION

영상 그룹: violation_1
제품: 엘레나 테아닌 / (주)빅솔 반월공장 / DB ID 28582

엘레나 테아닌 제품은 장염을 치료한다.

**판정 근거**

건강 보조 기능을 질병 예방·치료 또는 의약품 대체 주장으로 바꿈. 주간 발표의 질병·의약품 주장 기준에 따른 정답임.

**DB 원문: products:28582.main_functionality**

> [UREX프로바이오틱스]
> - 질내 유익균 증식 및 유해균 억제에 도움을 줄 수 있음
> - 유산균 증식 및 유해균 억제 · 배변활동 원활 · 장 건강에 도움을 줄 수 있음
> [테아닌]
> - 스트레스로 인한 긴장완화에 도움을 줄 수 있음

## db_196_CHOw23s17GA / c54 / VIOLATION

영상 그룹: violation_1_overclaim_1
제품: 연세 루테인 플러스 / 주식회사한미양행 / DB ID 29075

연세 루테인 플러스 제품은 황반변성을 치료한다.

**판정 근거**

건강 보조 기능을 질병 예방·치료 또는 의약품 대체 주장으로 바꿈. 주간 발표의 질병·의약품 주장 기준에 따른 정답임.

**DB 원문: products:29075.main_functionality**

> 노화로 인해 감소될 수 있는 황반색소밀도를 유지하여 눈 건강에 도움을 줄 수 있음
> 
> ①어두운 곳에서 시각 적응을 위해 필요②피부와 점막을 형성하고 기능을 유지하는데 필요③상피세포의 성장과 발달에 필요
> 
> ①칼슘과 인이 흡수되고 이용되는데 필요②뼈의 형성과 유지에 필요③골다공증발생 위험 감소에 도움을 줌
> 
> 항산화 작용을 하여 유해산소로부터 세포를 보호하는데 필요
> 
> (1) 탄수화물과 에너지 대사에 필요
> 
> (1) 체내 에너지 생성에 필요
> 
> ①단백질 및 아미노산 이용에 필요②혈액의 호모시스테인 수준을 정상으로 유지하는데 필요
> 
> ①결합조직 형성과 기능유지에 필요②철의 흡수에 필요③항산화 작용을 하여 유해산소로부터 세포를 보호하는데 필요
> 
> ①정상적인 면역기능에 필요②정상적인 세포분열에 필요

## db_196_CHOw23s17GA / c55 / OVERCLAIM

영상 그룹: violation_1_overclaim_1
제품: 연세 루테인 플러스 / 주식회사한미양행 / DB ID 29075

연세 루테인 플러스 제품은 일주일 만에 시력을 0.3 높여 주는 효과가 확실하다.

**판정 근거**

제품 및 원료의 인정 기능성에는 이 기간·수치·구체적 결과를 보장하는 문장이 없음. 질병 치료나 의약품 대체가 아니라, 인정 범위를 넘는 과장된 효과로 구성함. NLI 점수를 정답으로 사용하지 않으며 실제 NLI의 OVERCLAIM 출력은 별도 평가 대상임.

**DB 원문: products:29075.main_functionality**

> 노화로 인해 감소될 수 있는 황반색소밀도를 유지하여 눈 건강에 도움을 줄 수 있음
> 
> ①어두운 곳에서 시각 적응을 위해 필요②피부와 점막을 형성하고 기능을 유지하는데 필요③상피세포의 성장과 발달에 필요
> 
> ①칼슘과 인이 흡수되고 이용되는데 필요②뼈의 형성과 유지에 필요③골다공증발생 위험 감소에 도움을 줌
> 
> 항산화 작용을 하여 유해산소로부터 세포를 보호하는데 필요
> 
> (1) 탄수화물과 에너지 대사에 필요
> 
> (1) 체내 에너지 생성에 필요
> 
> ①단백질 및 아미노산 이용에 필요②혈액의 호모시스테인 수준을 정상으로 유지하는데 필요
> 
> ①결합조직 형성과 기능유지에 필요②철의 흡수에 필요③항산화 작용을 하여 유해산소로부터 세포를 보호하는데 필요
> 
> ①정상적인 면역기능에 필요②정상적인 세포분열에 필요

**DB 원문: products:29075.RAWMTRL_STD_INFO**

> [{"RCOGN_NO":"","RAWMTRL_NM":"마리골드꽃추출물","DAY_INTK_LOWLIMIT":"10","DAY_INTK_HIGHLIMIT":"20","INTK_UNIT":"mg","INTK_MEMO":"(24.12.23.) 섭취시주의사항, 주된기능성 현행화 / '24 신뢰성 확보","SKLL_IX_IRDNT_RAWMTRL":"루테인(Lutein)","PRIMARY_FNCLTY":"(1) 노화로 인해 감소될 수 있는 황반색소밀도를 유지하여 눈 건강에 도움을 줄 수 있음","IFTKN_ATNT_MATR_CN":"(가) 영‧유아, 어린이, 임산부 및 수유부는 섭취를 피할 것\n(나) 흡연자는 섭취 시 전문가와 상담할 것\n(다) 과다 섭취 시 일시적으로 피부가 황색으로 변할 수 있음\n(라) 이상사례 발생 시 섭취를 중단하고 전문가와 상담할 것"},{"RCOGN_NO":"","RAWMTRL_NM":"비타민 A","DAY_INTK_LOWLIMIT":"210","DAY_INTK_HIGHLIMIT":"1000","INTK_UNIT":"μg RAE","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 어두운 곳에서 시각 적응을 위해 필요\n(2) 피부와 점막을 형성하고 기능을 유지하는데 필요\n(3) 상피세포의 성장과 발달에 필요","IFTKN_ATNT_MATR_CN":""},{"RCOGN_NO":"","RAWMTRL_NM":"비타민 D","DAY_INTK_LOWLIMIT":"0.003","DAY_INTK_HIGHLIMIT":"0.01","INTK_UNIT":"mg","INTK_MEMO":"일일섭취량 : 3~10 μg(120∼400 IU)","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 칼슘과 인이 흡수되고 이용되는데 필요\n(2) 뼈의 형성과 유지에 필요\n(3) 골다공증발생 위험 감소에 도움을 줌","IFTKN_ATNT_MATR_CN":"(가) 고칼슘혈증이 있거나 의약품 복용 시 전문가와 상담할 것\n(나) 이상사례 발생 시 섭취를 중단하고 전문가와 상담할 것"},{"RCOGN_NO":"","RAWMTRL_NM":"비타민 E","DAY_INTK_LOWLIMIT":"3.3","DAY_INTK_HIGHLIMIT":"400","INTK_UNIT":"mg α-TE","INTK_MEMO":"2021.7.11: 기능성 내용 변경","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"항산화 작용을 하여 유해산소로부터 세포를 보호하는데 필요","IFTKN_ATNT_MATR_CN":""},{"RCOGN_NO":"","RAWMTRL_NM":"비타민 B1","DAY_INTK_LOWLIMIT":"0.36","DAY_INTK_HIGHLIMIT":"100","INTK_UNIT":"mg","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 탄수화물과 에너지 대사에 필요","IFTKN_ATNT_MATR_CN":"(1) 이상사례 발생 시 섭취를 중단하고 전문가와 상담할 것"},{"RCOGN_NO":"","RAWMTRL_NM":"비타민 B2","DAY_INTK_LOWLIMIT":"0.42","DAY_INTK_HIGHLIMIT":"40","INTK_UNIT":"mg","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 체내 에너지 생성에 필요","IFTKN_ATNT_MATR_CN":"(1) 이상사례 발생 시 섭취를 중단하고 전문가와 상담할 것"},{"RCOGN_NO":"","RAWMTRL_NM":"비타민 B6","DAY_INTK_LOWLIMIT":"0.45","DAY_INTK_HIGHLIMIT":"67","INTK_UNIT":"mg","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 단백질 및 아미노산 이용에 필요\n(2) 혈액의 호모시스테인 수준을 정상으로 유지하는데 필요","IFTKN_ATNT_MATR_CN":"(1) 손발 따끔거림, 작열감 또는 저림 등의 이상사례 발생 시 섭취를 중단하고 전문가와 상담할 것"},{"RCOGN_NO":"","RAWMTRL_NM":"비타민 C","DAY_INTK_LOWLIMIT":"30","DAY_INTK_HIGHLIMIT":"1000","INTK_UNIT":"mg","INTK_MEMO":"21.7.11: 기능성 내용 변경 26.7.23 주의사항 변경","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 결합조직 형성과 기능유지에 필요\n(2) 철의 흡수에 필요\n(3) 항산화 작용을 하여 유해산소로부터 세포를 보호하는데 필요","IFTKN_ATNT_MATR_CN":"(1) 과량 섭취하지 않도록 주의할 것\n(2) 신장질환이 있는 경우 섭취 전 전문가와 상담할 것\n(3) 이상사례 발생 시 섭취를 중단하고 전문가와 상담할 것"},{"RCOGN_NO":"","RAWMTRL_NM":"아연","DAY_INTK_LOWLIMIT":"2.55","DAY_INTK_HIGHLIMIT":"12","INTK_UNIT":"mg","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 정상적인 면역기능에 필요\n(2) 정상적인 세포분열에 필요","IFTKN_ATNT_MATR_CN":""}]

## db_197_X0jCGgzhae0 / c15 / VIOLATION

영상 그룹: violation_2
제품: 옵티머스트 / (주)한국씨엔에스팜 / DB ID 30166

옵티머스트 제품은 퇴행성 관절염을 치료한다.

**판정 근거**

건강 보조 기능을 질병 예방·치료 또는 의약품 대체 주장으로 바꿈. 주간 발표의 질병·의약품 주장 기준에 따른 정답임.

**DB 원문: products:30166.main_functionality**

> [MSM] ①관절 및 연골건강에 도움을 줄 수 있음
> 
> [비타민D] ①칼슘과 인이 흡수되고 이용되는데 필요 ②뼈의 형성과 유지에 필요 ③골다공증발생 위험 감소에 도움을 줌

## db_197_X0jCGgzhae0 / c16 / VIOLATION

영상 그룹: violation_2
제품: 옵티머스트 / (주)한국씨엔에스팜 / DB ID 30166

옵티머스트의 등록된 하루 섭취량은 5정이다.

**판정 근거**

같은 하루 기준에서 DB는 3정이나 Claim은 5정으로 변경함.

**DB 원문: products:30166.intake_method**

> 1일 1회, 1회 3정을 충분한 물과 함께 섭취하십시오.

## db_198_JkqRTHd0Nsg / c12 / VIOLATION

영상 그룹: violation_2
제품: 위건강엔 그린세라F액상 / 주식회사 노바렉스 / DB ID 31052

위건강엔 그린세라F액상 제품은 위염과 위궤양을 치료한다.

**판정 근거**

건강 보조 기능을 질병 예방·치료 또는 의약품 대체 주장으로 바꿈. 주간 발표의 질병·의약품 주장 기준에 따른 정답임.

**DB 원문: products:31052.main_functionality**

> (국문) 위 점막을 보호하여 위 건강에 도움을 줄 수 있음
> (영문) May help to maintain healthy stomach by protecting gastric mucosa

## db_198_JkqRTHd0Nsg / c13 / VIOLATION

영상 그룹: violation_2
제품: 위건강엔 그린세라F액상 / 주식회사 노바렉스 / DB ID 31052

위건강엔 그린세라F액상의 등록된 하루 섭취량은 3포이다.

**판정 근거**

같은 하루 기준에서 DB는 1포이나 Claim은 3포으로 변경함.

**DB 원문: products:31052.intake_method**

> 1일 1회, 1회 1포를 섭취하십시오.

## db_199_fgMIEID1N30 / c25 / VIOLATION

영상 그룹: violation_1_overclaim_1
제품: 위슬로 루바브 레드밸런스 / 콜마비앤에이치(주)음성공장 / DB ID 31099

위슬로 루바브 레드밸런스 제품은 갱년기 호르몬 치료제를 대신할 수 있다.

**판정 근거**

건강 보조 기능을 질병 예방·치료 또는 의약품 대체 주장으로 바꿈. 주간 발표의 질병·의약품 주장 기준에 따른 정답임.

**DB 원문: products:31099.main_functionality**

> - 루바브뿌리추출물 : 갱년기 여성 건강에 도움을 줄 수 있음

## db_199_fgMIEID1N30 / c26 / OVERCLAIM

영상 그룹: violation_1_overclaim_1
제품: 위슬로 루바브 레드밸런스 / 콜마비앤에이치(주)음성공장 / DB ID 31099

위슬로 루바브 레드밸런스 제품은 한 번만 먹어도 갱년기로 떨어진 체력이 즉시 두 배로 좋아진다.

**판정 근거**

제품 및 원료의 인정 기능성에는 이 기간·수치·구체적 결과를 보장하는 문장이 없음. 질병 치료나 의약품 대체가 아니라, 인정 범위를 넘는 과장된 효과로 구성함. NLI 점수를 정답으로 사용하지 않으며 실제 NLI의 OVERCLAIM 출력은 별도 평가 대상임.

**DB 원문: products:31099.main_functionality**

> - 루바브뿌리추출물 : 갱년기 여성 건강에 도움을 줄 수 있음

**DB 원문: products:31099.RAWMTRL_STD_INFO**

> [{"RCOGN_NO":"2021-17","RAWMTRL_NM":"루바브뿌리추출물(기능성원료인정제2021-17호)","DAY_INTK_LOWLIMIT":"4","DAY_INTK_HIGHLIMIT":"4","INTK_UNIT":"mg","INTK_MEMO":"제2021-17호","SKLL_IX_IRDNT_RAWMTRL":"라폰티신","PRIMARY_FNCLTY":"(국문) 갱년기 여성 건강에 도움을 줄 수 있음 (영문) May help to maintain female health in menopause","IFTKN_ATNT_MATR_CN":"(1) 영·유아, 어린이, 임산부 및 수유부는 섭취에 주의 (2) 에스트로겐 호르몬에 민감한 사람은 섭취에 주의 (3) 메스꺼움 등 소화계통의 불편함과 설사를 유발할 수 있음 (4) 알레르기 체질이거나 특정질환이 있는 사람은 섭취 전 전문가와 상담할 것 (5) 이상사례 발생 시 섭취를 중단하고 전문가와 상담할 것"}]

## db_200_WLfMEmR3ZF4 / c10 / OVERCLAIM

영상 그룹: overclaim_1
제품: 유니베라 슈퍼겔 맥스 / (주)네이처텍 / DB ID 31291

유니베라 슈퍼겔 맥스 제품은 일주일 만에 피부 수분량을 두 배로 높이는 효과가 확실하다.

**판정 근거**

제품 및 원료의 인정 기능성에는 이 기간·수치·구체적 결과를 보장하는 문장이 없음. 질병 치료나 의약품 대체가 아니라, 인정 범위를 넘는 과장된 효과로 구성함. NLI 점수를 정답으로 사용하지 않으며 실제 NLI의 OVERCLAIM 출력은 별도 평가 대상임.

**DB 원문: products:31291.main_functionality**

> -피부건강·장 건강·면역력 증진에 도움을 줄 수 있음

**DB 원문: products:31291.RAWMTRL_STD_INFO**

> [{"RCOGN_NO":"","RAWMTRL_NM":"알로에 겔","DAY_INTK_LOWLIMIT":"110","DAY_INTK_HIGHLIMIT":"420","INTK_UNIT":"mg","INTK_MEMO":"(24.12.23.) 섭취시주의사항, 일일섭취량 현행화 / '24 신뢰성 확보","SKLL_IX_IRDNT_RAWMTRL":"총 다당체","PRIMARY_FNCLTY":"(1) 피부건강·장 건강·면역력 증진에 도움을 줄 수 있음","IFTKN_ATNT_MATR_CN":"(1) 이상사례 발생 시 섭취를 중단하고 전문가와 상담할 것"}]

## db_201_YBn7emsawpQ / c19 / VIOLATION

영상 그룹: violation_1
제품: 익스트림 올인원 포 맨 / 주식회사 노바렉스 / DB ID 32492

익스트림 올인원 포 맨 제품은 간염을 치료한다.

**판정 근거**

건강 보조 기능을 질병 예방·치료 또는 의약품 대체 주장으로 바꿈. 주간 발표의 질병·의약품 주장 기준에 따른 정답임.

**DB 원문: products:32492.main_functionality**

> [마그네슘] 에너지 이용에 필요, 신경과 근육 기능 유지에 필요
> [밀크씨슬(카르두스마리아누스)추출물] 간 건강에 도움을 줄 수 있음
> [비타민B6] 단백질 및 아미노산 이용에 필요, 혈액의 호모시스테인 수준을 정상으로 유지하는데 필요
> [비타민B1] 탄수화물과 에너지 대사에 필요
> [비타민B2] 체내 에너지 생성에 필요
> [나이아신] 체내 에너지 생성에 필요
> [판토텐산] 지방, 탄수화물, 단백질 대사와 에너지 생성에 필요
> [비타민B12] 정상적인 엽산 대사에 필요
> [엽산] 세포와 혈액생성에 필요, 태아 신경관의 정상 발달에 필요, 혈액의 호모시스테인 수준을 정상으로 유지하는데 필요
> [비오틴] 지방, 탄수화물, 단백질 대사와 에너지 생성에 필요
> [비타민C] 결합조직 형성과 기능유지에 필요, 철의 흡수에 필요, 항산화 작용을 하여 유해산소로부터 세포를 보호하는데 필요
> [셀렌] 유해산소로부터 세포를 보호하는데 필요
> [철] 체내 산소운반과 혈액생성에 필요, 에너지 생성에 필요
> [아연] 정상적인 면역기능에 필요, 정상적인 세포분열에 필요
> [크롬] 체내 탄수화물, 지방, 단백질 대사에 관여
> [망간] 뼈 형성에 필요, 에너지 이용에 필요, 유해산소로부터 세포를 보호하는데 필요
> [비타민A] 어두운 곳에서 시각 적응을 위해 필요, 피부와 점막을 형성하고 기능을 유지하는데 필요, 상피세포의 성장과 발달에 필요
> [구리] 철의 운반과 이용에 필요, 유해산소로부터 세포를 보호하는데 필요
> [EPA및DHA함유유지] 혈중 중성지질 개선･혈행 개선･건조한 눈을 개선하여 눈 건강에 도움을 줄 수 있음
> [마리골드꽃추출물] 노화로 인해 감소될 수 있는 황반색소밀도를 유지하여 눈 건강에 도움을 줄 수 있음
> [비타민E] 항산화 작용을 하여 유해산소로부터 세포를 보호하는데 필요
> [비타민D] 칼슘과 인이 흡수되고 이용되는데 필요, 뼈의 형성과 유지에 필요, 골다공증발생 위험 감소에 도움을 줌

## db_202_oTg1JYJBG6I / c61 / OVERCLAIM

영상 그룹: overclaim_1
제품: 일양 혈당건강 면역건강 / (주)세종바이오팜 / DB ID 33015

일양 혈당건강 면역건강 제품은 탄수화물을 두 배로 먹어도 식후 혈당 상승을 완전히 막는다.

**판정 근거**

제품 및 원료의 인정 기능성에는 이 기간·수치·구체적 결과를 보장하는 문장이 없음. 질병 치료나 의약품 대체가 아니라, 인정 범위를 넘는 과장된 효과로 구성함. NLI 점수를 정답으로 사용하지 않으며 실제 NLI의 OVERCLAIM 출력은 별도 평가 대상임.

**DB 원문: products:33015.main_functionality**

> ①정상적인 면역기능에 필요②정상적인 세포분열에 필요
> 
> ①식후 혈당상승 억제에 도움을 줄 수 있음
> 
> (1) 탄수화물과 에너지 대사에 필요

**DB 원문: products:33015.RAWMTRL_STD_INFO**

> [{"RCOGN_NO":"","RAWMTRL_NM":"바나바잎 추출물","DAY_INTK_LOWLIMIT":"0.45","DAY_INTK_HIGHLIMIT":"1.3","INTK_UNIT":"mg","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"코로솔산(Corosolic acid)","PRIMARY_FNCLTY":"(1) 식후 혈당상승 억제에 도움을 줄 수 있음","IFTKN_ATNT_MATR_CN":"(1) 어린이, 임산부 및 수유부는 섭취를 피할 것\n(2) 이상사례 발생 시 섭취를 중단하고 전문가와 상담할 것"},{"RCOGN_NO":"","RAWMTRL_NM":"아연","DAY_INTK_LOWLIMIT":"2.55","DAY_INTK_HIGHLIMIT":"12","INTK_UNIT":"mg","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 정상적인 면역기능에 필요\n(2) 정상적인 세포분열에 필요","IFTKN_ATNT_MATR_CN":""},{"RCOGN_NO":"","RAWMTRL_NM":"비타민 B1","DAY_INTK_LOWLIMIT":"0.36","DAY_INTK_HIGHLIMIT":"100","INTK_UNIT":"mg","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 탄수화물과 에너지 대사에 필요","IFTKN_ATNT_MATR_CN":"(1) 이상사례 발생 시 섭취를 중단하고 전문가와 상담할 것"}]

## db_203_hBfs_yl13uQ / c11 / OVERCLAIM

영상 그룹: overclaim_1
제품: 짜증날땐 먹어도 돼 / 주식회사한미양행 / DB ID 34975

짜증날땐 먹어도 돼 제품은 2주 만에 체지방 5kg을 확실히 줄인다.

**판정 근거**

제품 및 원료의 인정 기능성에는 이 기간·수치·구체적 결과를 보장하는 문장이 없음. 질병 치료나 의약품 대체가 아니라, 인정 범위를 넘는 과장된 효과로 구성함. NLI 점수를 정답으로 사용하지 않으며 실제 NLI의 OVERCLAIM 출력은 별도 평가 대상임.

**DB 원문: products:34975.main_functionality**

> 체지방 감소에 도움을 줄 수 있음 (생리활성기능 2등급)
> 
> ① 스트레스로 인한 긴장완화에 도움을 줄 수 있음
> 
> (1) 탄수화물과 에너지 대사에 필요
> 
> (1) 체내 에너지 생성에 필요
> 
> ①체내 에너지 생성에 필요
> 
> (1) 지방, 탄수화물, 단백질 대사와 에너지 생성에 필요
> 
> (1) 지방, 탄수화물, 단백질 대사와 에너지 생성에 필요

**DB 원문: products:34975.RAWMTRL_STD_INFO**

> [{"RCOGN_NO":"2012-5","RAWMTRL_NM":"콜레우스 포스콜리 추출물(기능성원료인정제2012-5호)","DAY_INTK_LOWLIMIT":"500","DAY_INTK_HIGHLIMIT":"500","INTK_UNIT":"mg","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"포스콜린","PRIMARY_FNCLTY":"(국문) 체지방 감소에 도움을 줄 수 있음(생리활성기능 2등급)","IFTKN_ATNT_MATR_CN":"(1) 임산부, 수유여성, 어린이는 섭취에 주의"},{"RCOGN_NO":"","RAWMTRL_NM":"테아닌","DAY_INTK_LOWLIMIT":"200","DAY_INTK_HIGHLIMIT":"250","INTK_UNIT":"mg","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"L-테아닌","PRIMARY_FNCLTY":"(1) 스트레스로 인한 긴장완화에 도움을 줄 수 있음","IFTKN_ATNT_MATR_CN":"(1) 임산부 및 수유부는 섭취를 피할 것\n(2) 카페인 함유음료(커피, 홍차, 녹차 등)와의 병용 섭취에 주의할 것\n(3) 수술전후 환자는 전문가와 상담할 것\n(4) 이상사례 발생 시 섭취를 중단하고 전문가와 상담할 것"},{"RCOGN_NO":"","RAWMTRL_NM":"비타민 B1","DAY_INTK_LOWLIMIT":"0.36","DAY_INTK_HIGHLIMIT":"100","INTK_UNIT":"mg","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 탄수화물과 에너지 대사에 필요","IFTKN_ATNT_MATR_CN":"(1) 이상사례 발생 시 섭취를 중단하고 전문가와 상담할 것"},{"RCOGN_NO":"","RAWMTRL_NM":"비타민 B2","DAY_INTK_LOWLIMIT":"0.42","DAY_INTK_HIGHLIMIT":"40","INTK_UNIT":"mg","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 체내 에너지 생성에 필요","IFTKN_ATNT_MATR_CN":"(1) 이상사례 발생 시 섭취를 중단하고 전문가와 상담할 것"},{"RCOGN_NO":"","RAWMTRL_NM":"나이아신","DAY_INTK_LOWLIMIT":"4.5","DAY_INTK_HIGHLIMIT":"670","INTK_UNIT":"mg","INTK_MEMO":"니코틴산 4.5～23 mg, 니코틴산아미드 4.5～670 mg","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 체내 에너지 생성에 필요","IFTKN_ATNT_MATR_CN":""},{"RCOGN_NO":"","RAWMTRL_NM":"판토텐산","DAY_INTK_LOWLIMIT":"1.5","DAY_INTK_HIGHLIMIT":"200","INTK_UNIT":"mg","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 지방, 탄수화물, 단백질 대사와 에너지 생성에 필요","IFTKN_ATNT_MATR_CN":"(1) 이상사례 발생 시 섭취를 중단하고 전문가와 상담할 것"},{"RCOGN_NO":"","RAWMTRL_NM":"비오틴","DAY_INTK_LOWLIMIT":"0.009","DAY_INTK_HIGHLIMIT":"0.9","INTK_UNIT":"mg","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 지방, 탄수화물, 단백질 대사와 에너지 생성에 필요","IFTKN_ATNT_MATR_CN":"(1) 이상사례 발생 시 섭취를 중단하고 전문가와 상담할 것"}]

## db_204_73yGR-979W0 / c11 / VIOLATION

영상 그룹: violation_1_overclaim_1
제품: 천관보 프리미엄 / (주)그린바이오 / DB ID 35126

천관보 프리미엄의 등록된 하루 섭취량은 3포이다.

**판정 근거**

같은 하루 기준에서 DB는 1포이나 Claim은 3포으로 변경함.

**DB 원문: products:35126.intake_method**

> 1일 1회, 1회 1포(1포당 70ml)를 그대로 섭취하십시오.

## db_204_73yGR-979W0 / c12 / OVERCLAIM

영상 그룹: violation_1_overclaim_1
제품: 천관보 프리미엄 / (주)그린바이오 / DB ID 35126

천관보 프리미엄 제품은 하루 만에 무릎 움직임 범위를 50% 넓혀 주는 효과가 확실하다.

**판정 근거**

제품 및 원료의 인정 기능성에는 이 기간·수치·구체적 결과를 보장하는 문장이 없음. 질병 치료나 의약품 대체가 아니라, 인정 범위를 넘는 과장된 효과로 구성함. NLI 점수를 정답으로 사용하지 않으며 실제 NLI의 OVERCLAIM 출력은 별도 평가 대상임.

**DB 원문: products:35126.main_functionality**

> ① 관절 및 연골건강에 도움을 줄 수 있음
> 
> (국문) 근력 개선에 도움을 줄 수 있음
> (영문) Help to improve muscle strength
> 
> (1) 체내 에너지 생성에 필요
> 
> ①단백질 및 아미노산 이용에 필요②혈액의 호모시스테인 수준을 정상으로 유지하는데 필요
> 
> ①정상적인 면역기능에 필요②정상적인 세포분열에 필요,오미자추출물 : 근력 개선에 도움을 줄 수 있음
> 엠에스엠 : 관절 및 연골 건강에 도움을 줄 수 있음
> 비타민B2 : 체내 에너지 생성에 필요
> 비타민B6 : 단백질 및 아미노산 이용에 필요
>           혈액의 호모시스테인 수준을 정상으로 유지하는데 필요
> 아연 : 정상적인 면역 기능에 필요
>        정상적인 세포분열에 필요

**DB 원문: products:35126.RAWMTRL_STD_INFO**

> [{"RCOGN_NO":"","RAWMTRL_NM":"비타민 B6","DAY_INTK_LOWLIMIT":"0.45","DAY_INTK_HIGHLIMIT":"67","INTK_UNIT":"mg","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 단백질 및 아미노산 이용에 필요\n(2) 혈액의 호모시스테인 수준을 정상으로 유지하는데 필요","IFTKN_ATNT_MATR_CN":"(1) 손발 따끔거림, 작열감 또는 저림 등의 이상사례 발생 시 섭취를 중단하고 전문가와 상담할 것"},{"RCOGN_NO":"","RAWMTRL_NM":"비타민 B2","DAY_INTK_LOWLIMIT":"0.42","DAY_INTK_HIGHLIMIT":"40","INTK_UNIT":"mg","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 체내 에너지 생성에 필요","IFTKN_ATNT_MATR_CN":"(1) 이상사례 발생 시 섭취를 중단하고 전문가와 상담할 것"},{"RCOGN_NO":"2018-9","RAWMTRL_NM":"오미자추출물(기능성원료인정제2018-9호)","DAY_INTK_LOWLIMIT":"1582","DAY_INTK_HIGHLIMIT":"1582","INTK_UNIT":"mg","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"쉬잔드린(Schizandrin)","PRIMARY_FNCLTY":"(국문) 근력 개선에 도움을 줄 수 있음 (영문) Help to improve muscle strength","IFTKN_ATNT_MATR_CN":"(1) 영·유아, 어린이, 임산부 및 수유부는 섭취에 주의 (2) 수술 전․후 섭취에 주의 (3) 식사조절, 운동을 병행하는 것이 바람직함"},{"RCOGN_NO":"","RAWMTRL_NM":"엠에스엠(MSM, Methyl sulfonylmethane, 디메틸설폰)","DAY_INTK_LOWLIMIT":"1.5","DAY_INTK_HIGHLIMIT":"2","INTK_UNIT":"g","INTK_MEMO":"(24.12.23.) 섭취시주의사항 현행화 / '24 신뢰성 확보","SKLL_IX_IRDNT_RAWMTRL":"엠에스엠(MSM)","PRIMARY_FNCLTY":"(1) 관절 및 연골건강에 도움을 줄 수 있음","IFTKN_ATNT_MATR_CN":"(가) 신장질환이 있는 사람은 섭취 전 전문가와 상담할 것\n(나) 이상사례 발생 시 섭취를 중단하고 전문가와 상담할 것"},{"RCOGN_NO":"","RAWMTRL_NM":"아연","DAY_INTK_LOWLIMIT":"2.55","DAY_INTK_HIGHLIMIT":"12","INTK_UNIT":"mg","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 정상적인 면역기능에 필요\n(2) 정상적인 세포분열에 필요","IFTKN_ATNT_MATR_CN":""}]

## db_208_0drznbKPJgc / c21 / VIOLATION

영상 그룹: violation_1
제품: 총총 / (주)삼진GNF / DB ID 35845

총총 제품은 독감을 예방한다.

**판정 근거**

건강 보조 기능을 질병 예방·치료 또는 의약품 대체 주장으로 바꿈. 주간 발표의 질병·의약품 주장 기준에 따른 정답임.

**DB 원문: products:35845.main_functionality**

> ①탄수화물과 에너지 대사에 필요
> 
> ①단백질 및 아미노산 이용에 필요②혈액의 호모시스테인 수준을 정상으로 유지하는데 필요
> 
> ①정상적인 면역기능에 필요②정상적인 세포분열에 필요
> 
> ①체내 에너지 생성에 필요

## db_210_NKyAOi6Hrg8 / c17 / VIOLATION

영상 그룹: violation_1
제품: 코어틴 그린프로틴 / 맥널티바이오(주) / DB ID 36843

코어틴 그린프로틴 제품은 독감을 예방한다.

**판정 근거**

건강 보조 기능을 질병 예방·치료 또는 의약품 대체 주장으로 바꿈. 주간 발표의 질병·의약품 주장 기준에 따른 정답임.

**DB 원문: products:36843.main_functionality**

> ①근육, 결합조직 등 신체조직의 구성성분②효소, 호르몬, 항체의 구성에 필요③체내 필수 영양성분이나 활성물질의 운반과 저장에 필요④체액, 산-염기의 균형 유지에 필요⑤에너지, 포도당, 지질의 합성에 필요
> 
> ①뼈와 치아 형성에 필요②신경과 근육 기능 유지에 필요③정상적인 혈액응고에 필요④골다공증발생 위험 감소에 도움을 줌
> 
> ①에너지 이용에 필요②신경과 근육 기능 유지에 필요
> 
> ①칼슘과 인이 흡수되고 이용되는데 필요②뼈의 형성과 유지에 필요③골다공증발생 위험 감소에 도움을 줌
> 
> ①정상적인 면역기능에 필요②정상적인 세포분열에 필요
> 
> ①탄수화물과 에너지 대사에 필요
> 
> ①단백질 및 아미노산 이용에 필요②혈액의 호모시스테인 수준을 정상으로 유지하는데 필요
> 
> ①지방, 탄수화물, 단백질 대사와 에너지 생성에 필요

## db_211_L4KfNfwGB1s / c28 / OVERCLAIM

영상 그룹: overclaim_1
제품: 콜라겐 히알루론산 앰플샷 / (주)서흥헬스케어 / DB ID 37111

콜라겐 히알루론산 앰플샷 제품은 일주일 만에 피부 수분량을 두 배로 높이는 효과가 확실하다.

**판정 근거**

제품 및 원료의 인정 기능성에는 이 기간·수치·구체적 결과를 보장하는 문장이 없음. 질병 치료나 의약품 대체가 아니라, 인정 범위를 넘는 과장된 효과로 구성함. NLI 점수를 정답으로 사용하지 않으며 실제 NLI의 OVERCLAIM 출력은 별도 평가 대상임.

**DB 원문: products:37111.main_functionality**

> 저분자콜라겐펩타이드GT(제2022-6호) : (국문) (1) 피부 보습에 도움을 줄 수 있음 (2) 자외선에 의한 피부손상으로부터 피부건강을 유지하는데 도움을 줄 수 있음, (영문) (1) May help to moisturize (dry) skin (2) May help to maintain good skin health by protecting against damage from UV exposure
> 히알루론산 : 피부보습에 도움을 줄 수 있음
> 아연 : 정상적인 면역기능에 필요, 정상적인 세포분열에 필요
> 셀레늄 : 유해산소로부터 세포를 보호하는데 필요
> 나이아신 : 체내 에너지 생성에 필요
> 비타민B6 : (1) 단백질 및 아미노산 이용에 필요 (2) 혈액의 호모시스테인 수준을 정상으로 유지하는데 필요
> 비타민B1 : 탄수화물과 에너지 대사에 필요
> 비타민B2 : 체내 에너지 생성에 필요

**DB 원문: products:37111.RAWMTRL_STD_INFO**

> [{"RCOGN_NO":"","RAWMTRL_NM":"비타민 B2","DAY_INTK_LOWLIMIT":"0.42","DAY_INTK_HIGHLIMIT":"40","INTK_UNIT":"mg","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 체내 에너지 생성에 필요","IFTKN_ATNT_MATR_CN":"(1) 이상사례 발생 시 섭취를 중단하고 전문가와 상담할 것"},{"RCOGN_NO":"","RAWMTRL_NM":"비타민 B1","DAY_INTK_LOWLIMIT":"0.36","DAY_INTK_HIGHLIMIT":"100","INTK_UNIT":"mg","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 탄수화물과 에너지 대사에 필요","IFTKN_ATNT_MATR_CN":"(1) 이상사례 발생 시 섭취를 중단하고 전문가와 상담할 것"},{"RCOGN_NO":"","RAWMTRL_NM":"비타민 B6","DAY_INTK_LOWLIMIT":"0.45","DAY_INTK_HIGHLIMIT":"67","INTK_UNIT":"mg","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 단백질 및 아미노산 이용에 필요\n(2) 혈액의 호모시스테인 수준을 정상으로 유지하는데 필요","IFTKN_ATNT_MATR_CN":"(1) 손발 따끔거림, 작열감 또는 저림 등의 이상사례 발생 시 섭취를 중단하고 전문가와 상담할 것"},{"RCOGN_NO":"","RAWMTRL_NM":"나이아신","DAY_INTK_LOWLIMIT":"4.5","DAY_INTK_HIGHLIMIT":"670","INTK_UNIT":"mg","INTK_MEMO":"니코틴산 4.5～23 mg, 니코틴산아미드 4.5～670 mg","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 체내 에너지 생성에 필요","IFTKN_ATNT_MATR_CN":""},{"RCOGN_NO":"","RAWMTRL_NM":"셀레늄(또는 셀렌)","DAY_INTK_LOWLIMIT":"0.0165","DAY_INTK_HIGHLIMIT":"0.135","INTK_UNIT":"mg","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 유해산소로부터 세포를 보호하는데 필요","IFTKN_ATNT_MATR_CN":""},{"RCOGN_NO":"","RAWMTRL_NM":"아연","DAY_INTK_LOWLIMIT":"2.55","DAY_INTK_HIGHLIMIT":"12","INTK_UNIT":"mg","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 정상적인 면역기능에 필요\n(2) 정상적인 세포분열에 필요","IFTKN_ATNT_MATR_CN":""},{"RCOGN_NO":"","RAWMTRL_NM":"히알루론산","DAY_INTK_LOWLIMIT":"120","DAY_INTK_HIGHLIMIT":"240","INTK_UNIT":"mg","INTK_MEMO":"건기공전(제2019-91호, 기능성내용 변경)","SKLL_IX_IRDNT_RAWMTRL":"히알루론산","PRIMARY_FNCLTY":"(1)기능성 내용 : 피부보습･자외선에 의한 피부손상으로부터 피부건강 유지에 도움을 줄 수 있음\n(2) 일일섭취량\n (가) 피부보습에 도움을 줄 수 있음 : 히알루론산으로서 120∼240 mg\n (나)자외선에 의한 피부손상으로부터 피부건강 유지에 도움을 줄 수 있음 : 히알루론산으로서 240 mg","IFTKN_ATNT_MATR_CN":""},{"RCOGN_NO":"2022-6","RAWMTRL_NM":"저분자콜라겐펩타이드GT(기능성원료인정제2022-6호)","DAY_INTK_LOWLIMIT":"2","DAY_INTK_HIGHLIMIT":"2","INTK_UNIT":"g","INTK_MEMO":"제2022-6호","SKLL_IX_IRDNT_RAWMTRL":"Val-Gly-Pro-Hyp-Gly-Pro-Ala-Gly","PRIMARY_FNCLTY":"(국문) 피부 보습에 도움을 줄 수 있음 (영문) May help to moisturize (dry) skin","IFTKN_ATNT_MATR_CN":"(1) 영‧유아, 어린이, 임산부 및 수유부는 섭취에 주의할 것 (2) 특정질환(알레르기 체질 등)이 있는 분은 섭취에 주의할 것 (3) 이상사례 발생 시 섭취를 중단하고 전문가와 상담할 것"}]

## db_212_qbQfBqPEqGQ / c13 / OVERCLAIM

영상 그룹: overclaim_1
제품: 토비콤 아이 포커스 / (주)알피바이오 / DB ID 38148

토비콤 아이 포커스 제품은 단 하루 만에 눈의 피로를 90%까지 확실히 줄인다.

**판정 근거**

제품 및 원료의 인정 기능성에는 이 기간·수치·구체적 결과를 보장하는 문장이 없음. 질병 치료나 의약품 대체가 아니라, 인정 범위를 넘는 과장된 효과로 구성함. NLI 점수를 정답으로 사용하지 않으며 실제 NLI의 OVERCLAIM 출력은 별도 평가 대상임.

**DB 원문: products:38148.main_functionality**

> [헤마토코쿠스 추출물]
> ①눈의 피로도 개선에 도움을 줄 수 있음
> 
> [비타민 A]
> ①어두운 곳에서 시각 적응을 위해 필요②피부와 점막을 형성하고 기능을 유지하는데 필요③상피세포의 성장과 발달에 필요
> 
> [비타민 B1]
> ①탄수화물과 에너지 대사에 필요
> 
> [비타민 B2]
> ①체내 에너지 생성에 필요
> 
> [비타민 B6]
> ①단백질 및 아미노산 이용에 필요②혈액의 호모시스테인 수준을 정상으로 유지하는데 필요
> 
> [비타민 B12]
> ①정상적인 엽산 대사에 필요
> 
> [나이아신]
> ①체내 에너지 생성에 필요
> 
> [판토텐산]
> ①지방, 탄수화물, 단백질 대사와 에너지 생성에 필요

**DB 원문: products:38148.RAWMTRL_STD_INFO**

> [{"RCOGN_NO":"","RAWMTRL_NM":"판토텐산","DAY_INTK_LOWLIMIT":"1.5","DAY_INTK_HIGHLIMIT":"200","INTK_UNIT":"mg","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 지방, 탄수화물, 단백질 대사와 에너지 생성에 필요","IFTKN_ATNT_MATR_CN":"(1) 이상사례 발생 시 섭취를 중단하고 전문가와 상담할 것"},{"RCOGN_NO":"","RAWMTRL_NM":"나이아신","DAY_INTK_LOWLIMIT":"4.5","DAY_INTK_HIGHLIMIT":"670","INTK_UNIT":"mg","INTK_MEMO":"니코틴산 4.5～23 mg, 니코틴산아미드 4.5～670 mg","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 체내 에너지 생성에 필요","IFTKN_ATNT_MATR_CN":""},{"RCOGN_NO":"","RAWMTRL_NM":"비타민 B12","DAY_INTK_LOWLIMIT":"0.00072","DAY_INTK_HIGHLIMIT":"2","INTK_UNIT":"mg","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 정상적인 엽산 대사에 필요","IFTKN_ATNT_MATR_CN":"(1) 이상사례 발생 시 섭취를 중단하고 전문가와 상담할 것"},{"RCOGN_NO":"","RAWMTRL_NM":"비타민 B6","DAY_INTK_LOWLIMIT":"0.45","DAY_INTK_HIGHLIMIT":"67","INTK_UNIT":"mg","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 단백질 및 아미노산 이용에 필요\n(2) 혈액의 호모시스테인 수준을 정상으로 유지하는데 필요","IFTKN_ATNT_MATR_CN":"(1) 손발 따끔거림, 작열감 또는 저림 등의 이상사례 발생 시 섭취를 중단하고 전문가와 상담할 것"},{"RCOGN_NO":"","RAWMTRL_NM":"비타민 B2","DAY_INTK_LOWLIMIT":"0.42","DAY_INTK_HIGHLIMIT":"40","INTK_UNIT":"mg","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 체내 에너지 생성에 필요","IFTKN_ATNT_MATR_CN":"(1) 이상사례 발생 시 섭취를 중단하고 전문가와 상담할 것"},{"RCOGN_NO":"","RAWMTRL_NM":"비타민 B1","DAY_INTK_LOWLIMIT":"0.36","DAY_INTK_HIGHLIMIT":"100","INTK_UNIT":"mg","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 탄수화물과 에너지 대사에 필요","IFTKN_ATNT_MATR_CN":"(1) 이상사례 발생 시 섭취를 중단하고 전문가와 상담할 것"},{"RCOGN_NO":"","RAWMTRL_NM":"비타민 A","DAY_INTK_LOWLIMIT":"210","DAY_INTK_HIGHLIMIT":"1000","INTK_UNIT":"μg RAE","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 어두운 곳에서 시각 적응을 위해 필요\n(2) 피부와 점막을 형성하고 기능을 유지하는데 필요\n(3) 상피세포의 성장과 발달에 필요","IFTKN_ATNT_MATR_CN":""},{"RCOGN_NO":"","RAWMTRL_NM":"헤마토코쿠스 추출물","DAY_INTK_LOWLIMIT":"4","DAY_INTK_HIGHLIMIT":"12","INTK_UNIT":"mg","INTK_MEMO":"(24.12.23.) 섭취시주의사항, 주된기능성 현행화 / '24 신뢰성 확보","SKLL_IX_IRDNT_RAWMTRL":"아스타잔틴(Astaxanthin)","PRIMARY_FNCLTY":"(1) 기능성 내용 : 눈의 피로도 개선에 도움을 줄 수 있음","IFTKN_ATNT_MATR_CN":"(1) 과다 섭취 시 일시적으로 피부가 황색으로 변할 수 있음\n(2) β-카로틴의 흡수를 저해할 수 있음"}]

## db_213_P8VZYBOsflM / c09 / VIOLATION

영상 그룹: violation_2
제품: 트루바이타민 / (주)비오팜 / DB ID 38286

트루바이타민 제품은 아토피 피부염을 치료한다.

**판정 근거**

건강 보조 기능을 질병 예방·치료 또는 의약품 대체 주장으로 바꿈. 주간 발표의 질병·의약품 주장 기준에 따른 정답임.

**DB 원문: products:38286.main_functionality**

> [비타민C] ①결합조직 형성과 기능유지에 필요②철의 흡수에 필요③항산화 작용을 하여 유해산소로부터 세포를 보호하는데 필요
> [비타민B6] ①단백질 및 아미노산 이용에 필요②혈액의 호모시스테인 수준을 정상으로 유지하는데 필요
> [비타민B1] ①탄수화물과 에너지 대사에 필요
> [비타민B2] ①체내 에너지 생성에 필요 
> [나이아신] ①체내 에너지 생성에 필요
> [비타민E] ①항산화 작용을 하여 유해산소로부터 세포를 보호하는데 필요
> [판토텐산] ①지방, 탄수화물, 단백질 대사와 에너지 생성에 필요
> [비오틴] ①지방, 탄수화물, 단백질 대사와 에너지 생성에 필요
> [비타민A] ①어두운 곳에서 시각 적응을 위해 필요 ②피부와 점막을 형성하고 기능을 유지하는데 필요 ③상피세포의 성장과 발달에 필요
> [비타민B12] ①정상적인 엽산 대사에 필요
> [비타민K] ①정상적인 혈액응고에 필요 ② 뼈의 구성에 필요
> [비타민D] ①칼슘과 인이 흡수되고 이용되는데 필요②뼈의 형성과 유지에 필요③골다공증발생 위험 감소에 도움을 줌
> [엽산] ①세포와 혈액생성에 필요②태아 신경관의 정상 발달에 필요③혈액의 호모시스테인 수준을 정상으로 유지하는데 필요

## db_213_P8VZYBOsflM / c10 / VIOLATION

영상 그룹: violation_2
제품: 트루바이타민 / (주)비오팜 / DB ID 38286

트루바이타민의 등록된 하루 섭취량은 3포이다.

**판정 근거**

같은 하루 기준에서 DB는 1포이나 Claim은 3포으로 변경함.

**DB 원문: products:38286.intake_method**

> 1일 1회, 1회 1포(2제피정제, 1연질캡슐)를 물과 함께 섭취하십시오.

## db_217_SHhSMRCCVEM / c04 / VIOLATION

영상 그룹: violation_2
제품: 트루바이타민 X / (주)비오팜 / DB ID 38296

트루바이타민 X 제품은 아토피 피부염을 치료한다.

**판정 근거**

건강 보조 기능을 질병 예방·치료 또는 의약품 대체 주장으로 바꿈. 주간 발표의 질병·의약품 주장 기준에 따른 정답임.

**DB 원문: products:38296.main_functionality**

> [비타민C] ①결합조직 형성과 기능유지에 필요 ②철의 흡수에 필요 ③항산화 작용을 하여 유해산소로부터 세포를 보호하는데 필요
> [비타민B6] ①단백질 및 아미노산 이용에 필요 ②혈액의 호모시스테인 수준을 정상으로 유지하는데 필요
> [비타민B1] ① 탄수화물과 에너지 대사에 필요
> [비타민B2] ① 체내 에너지 생성에 필요
> [비타민E] ①항산화 작용을 하여 유해산소로부터 세포를 보호하는데 필요
> [비타민A] ①어두운 곳에서 시각 적응을 위해 필요 ②피부와 점막을 형성하고 기능을 유지하는데 필요 ③상피세포의 성장과 발달에 필요
> [비타민D] ①칼슘과 인이 흡수되고 이용되는데 필요 ②뼈의 형성과 유지에 필요 ③골다공증발생 위험 감소에 도움을 줌

## db_217_SHhSMRCCVEM / c05 / VIOLATION

영상 그룹: violation_2
제품: 트루바이타민 X / (주)비오팜 / DB ID 38296

트루바이타민 X의 등록된 하루 섭취량은 3포이다.

**판정 근거**

같은 하루 기준에서 DB는 1포이나 Claim은 3포으로 변경함.

**DB 원문: products:38296.intake_method**

> 1일 1회, 1회 1포(2제피정제, 1캡슐)를 물과 함께 섭취하십시오.

## db_228_80wkuzl_Slk / c20 / OVERCLAIM

영상 그룹: overclaim_1
제품: 프로비 프로폴리스 트리오 / 서울프로폴리스(주) / DB ID 40440

프로비 프로폴리스 트리오 제품은 한 번만 먹어도 입안 유해균을 100% 깨끗이 제거한다.

**판정 근거**

제품 및 원료의 인정 기능성에는 이 기간·수치·구체적 결과를 보장하는 문장이 없음. 질병 치료나 의약품 대체가 아니라, 인정 범위를 넘는 과장된 효과로 구성함. NLI 점수를 정답으로 사용하지 않으며 실제 NLI의 OVERCLAIM 출력은 별도 평가 대상임.

**DB 원문: products:40440.main_functionality**

> ①항산화·구강에서의 항균작용에 도움을 줄 수 있음

**DB 원문: products:40440.RAWMTRL_STD_INFO**

> [{"RCOGN_NO":"","RAWMTRL_NM":"프로폴리스추출물","DAY_INTK_LOWLIMIT":"20","DAY_INTK_HIGHLIMIT":"40","INTK_UNIT":"mg","INTK_MEMO":"(24.12.20.) 섭취시주의사항, 주된기능성 현행화 / '24 신뢰성 확보","SKLL_IX_IRDNT_RAWMTRL":"총 플라보노이드","PRIMARY_FNCLTY":"(1) 기능성 내용 : 항산화 ․ 구강에서의 항균작용에 도움을 줄 수 있음\n  ※ 구강에서의 항균작용은 구강에 직접 접촉할 수 있는 형태에 한하며, 섭취량을 적용하지 않음","IFTKN_ATNT_MATR_CN":"(가) 프로폴리스에 알레르기를 나타내는 사람은 섭취에 주의\n(나) 이상사례 발생 시 섭취를 중단하고 전문가와 상담할 것"}]

## db_231_Gc0b5hpZldE / c08 / OVERCLAIM

영상 그룹: overclaim_1
제품: 하루한포 액상 칼마 디데이 칼슘 마그네슘 / (주)케이씨엔바이오텍 / DB ID 42224

하루한포 액상 칼마 디데이 칼슘 마그네슘 제품은 일주일 만에 뼈의 강도를 두 배로 높여 준다.

**판정 근거**

제품 및 원료의 인정 기능성에는 이 기간·수치·구체적 결과를 보장하는 문장이 없음. 질병 치료나 의약품 대체가 아니라, 인정 범위를 넘는 과장된 효과로 구성함. NLI 점수를 정답으로 사용하지 않으며 실제 NLI의 OVERCLAIM 출력은 별도 평가 대상임.

**DB 원문: products:42224.main_functionality**

> 1. 칼슘
> 1) 뼈와 치아 형성에 필요
> 2) 신경과 근육 기능 유지에 필요
> 3) 정상적인 혈액응고에 필요
> 4) 골다공증발생 위험 감소에 도움을 줌,2. 마그네슘
> 1) 에너지 이용에 필요
> 2) 신경과 근육 기능 유지에 필요

**DB 원문: products:42224.RAWMTRL_STD_INFO**

> [{"RCOGN_NO":"","RAWMTRL_NM":"마그네슘","DAY_INTK_LOWLIMIT":"94.5","DAY_INTK_HIGHLIMIT":"250","INTK_UNIT":"mg","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 에너지 이용에 필요\n(2) 신경과 근육 기능 유지에 필요","IFTKN_ATNT_MATR_CN":""},{"RCOGN_NO":"","RAWMTRL_NM":"칼슘","DAY_INTK_LOWLIMIT":"210","DAY_INTK_HIGHLIMIT":"800","INTK_UNIT":"mg","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 뼈와 치아 형성에 필요\n(2) 신경과 근육 기능 유지에 필요\n(3) 정상적인 혈액응고에 필요\n(4) 골다공증발생 위험 감소에 도움을 줌","IFTKN_ATNT_MATR_CN":""}]

## db_235_qzFJGnEY2EA / c16 / VIOLATION

영상 그룹: violation_1
제품: 혈당 혈압 콜레스테롤 기억력엔 바나바잎 코큐텐 홍국 은행잎추출물 / 주식회사 코스팜 / DB ID 43481

혈당 혈압 콜레스테롤 기억력엔 바나바잎 코큐텐 홍국 은행잎추출물 제품은 당뇨병을 치료한다.

**판정 근거**

건강 보조 기능을 질병 예방·치료 또는 의약품 대체 주장으로 바꿈. 주간 발표의 질병·의약품 주장 기준에 따른 정답임.

**DB 원문: products:43481.main_functionality**

> [홍국]
> 1) 혈중 콜레스테롤 개선에 도움을 줄 수 있음
> 
> [은행잎 추출물]
> 1) 기억력 개선･혈행 개선에 도움을 줄 수 있음
> 
> [바나바잎 추출물]
> 1) 식후 혈당상승 억제에 도움을 줄 수 있음
> 
> [코엔자임Q10]
> 1) 항산화･높은 혈압 감소에 도움을 줄 수 있음

## db_236_mTVnYCElFYs / c14 / VIOLATION

영상 그룹: violation_1
제품: 혈당건강 바나바리프 / 우리바이오(주) / DB ID 43531

혈당건강 바나바리프 제품은 당뇨병을 치료한다.

**판정 근거**

건강 보조 기능을 질병 예방·치료 또는 의약품 대체 주장으로 바꿈. 주간 발표의 질병·의약품 주장 기준에 따른 정답임.

**DB 원문: products:43531.main_functionality**

> [바나바잎 추출물] 식후 혈당상승 억제에 도움을 줄 수 있음
> 
> [셀렌] 유해산소로부터 세포를 보호하는데 필요
> 
> [비타민 B1]  탄수화물과 에너지 대사에 필요
> 
> [아연] ①정상적인 면역기능에 필요②정상적인 세포분열에 필요
> 
> [크롬] 체내 탄수화물, 지방, 단백질 대사에 관여

## db_240_1je805Mt6e8 / c11 / OVERCLAIM

영상 그룹: overclaim_1
제품: 화애락 이너제틱 / (주)한국인삼공사 / DB ID 45395

화애락 이너제틱 제품은 하루 만에 장내 유해균을 99% 깨끗이 제거한다.

**판정 근거**

제품 및 원료의 인정 기능성에는 이 기간·수치·구체적 결과를 보장하는 문장이 없음. 질병 치료나 의약품 대체가 아니라, 인정 범위를 넘는 과장된 효과로 구성함. NLI 점수를 정답으로 사용하지 않으며 실제 NLI의 OVERCLAIM 출력은 별도 평가 대상임.

**DB 원문: products:45395.main_functionality**

> [홍삼] 면역력 증진·피로개선·혈소판 응집억제를 통한 혈액흐름·기억력 개선·항산화에 도움을 줄 수 있음
> 
> [난소화성말토덱스트린] 배변활동 원활에 도움을 줄 수 있음

**DB 원문: products:45395.RAWMTRL_STD_INFO**

> [{"RCOGN_NO":"","RAWMTRL_NM":"난소화성말토덱스트린","DAY_INTK_LOWLIMIT":"4","DAY_INTK_HIGHLIMIT":"30","INTK_UNIT":"g","INTK_MEMO":"식후 혈당상승억제:난소화성말토덱스트린식이섬유로서11.9～30g,혈중중성지질개선:난소화성말토덱스트린식이섬유로서12.7～30g,배변활동원활:난소화성말토덱스트린식이섬유로서2.5～30g","SKLL_IX_IRDNT_RAWMTRL":"난소화성말토덱스트린 식이섬유","PRIMARY_FNCLTY":"(1)기능성 내용 : 식후 혈당상승 억제･혈중 중성지질 개선･배변활동 원활에 도움을 줄 수 있음\n(2) 일일섭취량\n (가)식후 혈당상승 억제에 도움을 줄 수 있음 : 난소화성말토덱스트린 식이섬유로서 4.0~30 g (액상원료는 4.0~44 g)\n (나)혈중 중성지질 개선에 도움을 줄 수 있음 : 난소화성말토덱스트린 식이섬유로서 5.0~30 g (액상원료는 5.0~44 g)\n (다)배변활동 원활에 도움을 줄 수 있음 : 난소화성말토덱스트린 식이섬유로서 4.2~30 g (액상원료는 4.2~44 g)","IFTKN_ATNT_MATR_CN":"(3) 섭취 시 주의사항\n (가)반드시 충분한 물과 함께 섭취할 것(액상제외)\n (나)이상사례 발생 시 섭취를 중단하고 전문가와 상담할 것"},{"RCOGN_NO":"","RAWMTRL_NM":"홍삼","DAY_INTK_LOWLIMIT":"2.4","DAY_INTK_HIGHLIMIT":"80","INTK_UNIT":"mg","INTK_MEMO":"면역력증진·피로개선:진세노사이드Rg1,Rb1및Rg3의합계로서3～80mg,혈소판응집억제를 통한 혈액흐름·기억력 개선·항산화:진세노사이드Rg1,Rb1및Rg3의합계로서2.4～80mg,갱년기여성의 건강:진세노사이드Rg1,Rb1및Rg3의합계로서25∼80mg","SKLL_IX_IRDNT_RAWMTRL":"진세노사이드 Rg1, Rb1 및 Rg3 의 합","PRIMARY_FNCLTY":"(1)기능성 내용 : 면역력 증진･피로개선･혈소판 응집억제를 통한 혈액흐름･기억력 개선･항산화･갱년기 여성의 건강에 도움을 줄 수 있음\n(2) 일일섭취량\n (가)면역력 증진･피로개선에 도움을 줄 수 있음 : 진세노사이드 Rg1, Rb1 및 Rg3의 합계로서 3~80 mg\n (나)혈소판 응집억제를 통한 혈액흐름･기억력 개선･항산화에 도움을 줄 수 있음 : 진세노사이드 Rg1, Rb1 및 Rg3의 합계로서 2.4~80 mg\n (다)갱년기 여성의 건강에 도움을 줄 수 있음 : 진세노사이드 Rg1, Rb1 및 Rg3의 합계로서 25~80 mg","IFTKN_ATNT_MATR_CN":"(3) 섭취 시 주의사항 \n (가)당뇨치료제 및 혈액항응고제 복용 시 섭취에 주의\n (나)알레르기 체질 등은 개인에 따라 과민반응을 나타낼 수 있음\n (다)이상사례 발생 시 섭취를 중단하고 전문가와 상담할 것"}]

## db_241_h39aPD9onHk / c22 / OVERCLAIM

영상 그룹: overclaim_1
제품: 화애락 터닝미 / (주)한국인삼공사 / DB ID 45403

화애락 터닝미 제품은 한 번만 먹어도 갱년기로 떨어진 체력이 즉시 두 배로 좋아진다.

**판정 근거**

제품 및 원료의 인정 기능성에는 이 기간·수치·구체적 결과를 보장하는 문장이 없음. 질병 치료나 의약품 대체가 아니라, 인정 범위를 넘는 과장된 효과로 구성함. NLI 점수를 정답으로 사용하지 않으며 실제 NLI의 OVERCLAIM 출력은 별도 평가 대상임.

**DB 원문: products:45403.main_functionality**

> ①면역력 증진·피로개선·혈소판 응집억제를 통한 혈액흐름·기억력 개선·항산화·갱년기 여성의 건강에 도움을 줄 수 있음

**DB 원문: products:45403.RAWMTRL_STD_INFO**

> [{"RCOGN_NO":"","RAWMTRL_NM":"홍삼","DAY_INTK_LOWLIMIT":"2.4","DAY_INTK_HIGHLIMIT":"80","INTK_UNIT":"mg","INTK_MEMO":"면역력증진·피로개선:진세노사이드Rg1,Rb1및Rg3의합계로서3～80mg,혈소판응집억제를 통한 혈액흐름·기억력 개선·항산화:진세노사이드Rg1,Rb1및Rg3의합계로서2.4～80mg,갱년기여성의 건강:진세노사이드Rg1,Rb1및Rg3의합계로서25∼80mg","SKLL_IX_IRDNT_RAWMTRL":"진세노사이드 Rg1, Rb1 및 Rg3 의 합","PRIMARY_FNCLTY":"(1)기능성 내용 : 면역력 증진･피로개선･혈소판 응집억제를 통한 혈액흐름･기억력 개선･항산화･갱년기 여성의 건강에 도움을 줄 수 있음\n(2) 일일섭취량\n (가)면역력 증진･피로개선에 도움을 줄 수 있음 : 진세노사이드 Rg1, Rb1 및 Rg3의 합계로서 3~80 mg\n (나)혈소판 응집억제를 통한 혈액흐름･기억력 개선･항산화에 도움을 줄 수 있음 : 진세노사이드 Rg1, Rb1 및 Rg3의 합계로서 2.4~80 mg\n (다)갱년기 여성의 건강에 도움을 줄 수 있음 : 진세노사이드 Rg1, Rb1 및 Rg3의 합계로서 25~80 mg","IFTKN_ATNT_MATR_CN":"(3) 섭취 시 주의사항 \n (가)당뇨치료제 및 혈액항응고제 복용 시 섭취에 주의\n (나)알레르기 체질 등은 개인에 따라 과민반응을 나타낼 수 있음\n (다)이상사례 발생 시 섭취를 중단하고 전문가와 상담할 것"}]

## db_248_OzOYRNQo40Q / c14 / VIOLATION

영상 그룹: violation_1
제품: 프로메가 식물성 알티지 오메가3 듀얼 / (주)서흥 / DB ID 40145

프로메가 식물성 알티지 오메가3 듀얼의 등록된 하루 섭취량은 4캡슐이다.

**판정 근거**

같은 하루 기준에서 DB는 2캡슐이나 Claim은 4캡슐으로 변경함.

**DB 원문: products:40145.intake_method**

> 1일 1회, 1회 2캡슐을 충분한 물과 함께 섭취하십시오.

## db_251_8rlh8WopDFc / c20 / VIOLATION

영상 그룹: violation_1_overclaim_1
제품: 프로메가 알티지 오메가3 트리플S / 종근당건강(주) / DB ID 40163

프로메가 알티지 오메가3 트리플S 제품은 혈전증을 치료한다.

**판정 근거**

건강 보조 기능을 질병 예방·치료 또는 의약품 대체 주장으로 바꿈. 주간 발표의 질병·의약품 주장 기준에 따른 정답임.

**DB 원문: products:40163.main_functionality**

> EPA 및 DHA 함유 유지: 혈중 중성지질 개선·혈행 개선에 도움을 줄 수 있음, 건조한 눈을 개선하여 눈 건강에 도움을 줄 수 있음, 기억력 개선에 도움을 줄 수 있음
> 
> 비타민E: 항산화 작용을 하여 유해산소로부터 세포를 보호하는데 필요

## db_251_8rlh8WopDFc / c21 / OVERCLAIM

영상 그룹: violation_1_overclaim_1
제품: 프로메가 알티지 오메가3 트리플S / 종근당건강(주) / DB ID 40163

프로메가 알티지 오메가3 트리플S 제품은 한 번만 먹어도 말초 혈류량이 두 배로 늘어나는 효과가 확실하다.

**판정 근거**

제품 및 원료의 인정 기능성에는 이 기간·수치·구체적 결과를 보장하는 문장이 없음. 질병 치료나 의약품 대체가 아니라, 인정 범위를 넘는 과장된 효과로 구성함. NLI 점수를 정답으로 사용하지 않으며 실제 NLI의 OVERCLAIM 출력은 별도 평가 대상임.

**DB 원문: products:40163.main_functionality**

> EPA 및 DHA 함유 유지: 혈중 중성지질 개선·혈행 개선에 도움을 줄 수 있음, 건조한 눈을 개선하여 눈 건강에 도움을 줄 수 있음, 기억력 개선에 도움을 줄 수 있음
> 
> 비타민E: 항산화 작용을 하여 유해산소로부터 세포를 보호하는데 필요

**DB 원문: products:40163.RAWMTRL_STD_INFO**

> [{"RCOGN_NO":"","RAWMTRL_NM":"EPA 및 DHA 함유 유지","DAY_INTK_LOWLIMIT":"0.5","DAY_INTK_HIGHLIMIT":"2.24","INTK_UNIT":"g","INTK_MEMO":"건강기능식품의 기준 및 규격 2-16","SKLL_IX_IRDNT_RAWMTRL":"EPA와 DHA","PRIMARY_FNCLTY":"(1) 기능성 내용 : 혈중 중성지질 개선･혈행 개선･기억력 개선･건조한 눈을 개선하여 눈 건강에 도움을 줄 수 있음","IFTKN_ATNT_MATR_CN":"(가) 의약품(항응고제, 항혈소판제, 혈압강하제 등) 복용 시 전문가와 상담할 것\n(나) 개인에 따라 피부 관련 이상반응이 발생할 수 있음\n(다) 이상사례 발생 시 섭취를 중단하고 전문가와 상담할 것"},{"RCOGN_NO":"","RAWMTRL_NM":"비타민 E","DAY_INTK_LOWLIMIT":"3.3","DAY_INTK_HIGHLIMIT":"400","INTK_UNIT":"mg α-TE","INTK_MEMO":"2021.7.11: 기능성 내용 변경","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"항산화 작용을 하여 유해산소로부터 세포를 보호하는데 필요","IFTKN_ATNT_MATR_CN":""}]

## db_269_krmlXPXA0Hs / c22 / OVERCLAIM

영상 그룹: overclaim_1
제품: 락토핏 골드 / 종근당건강(주) / DB ID 13073

락토핏 골드 제품은 3일 만에 장내 유익균 수를 열 배로 늘리는 효과가 확실하다.

**판정 근거**

제품 및 원료의 인정 기능성에는 이 기간·수치·구체적 결과를 보장하는 문장이 없음. 질병 치료나 의약품 대체가 아니라, 인정 범위를 넘는 과장된 효과로 구성함. NLI 점수를 정답으로 사용하지 않으며 실제 NLI의 OVERCLAIM 출력은 별도 평가 대상임.

**DB 원문: products:13073.main_functionality**

> (1) 정상적인 면역기능에 필요
> (2) 정상적인 세포분열에 필요
> 
> 유산균 증식 및 유해균 억제･배변활동 원활･장 건강에 도움을 줄 수 있음

**DB 원문: products:13073.RAWMTRL_STD_INFO**

> [{"RCOGN_NO":"","RAWMTRL_NM":"프로바이오틱스","DAY_INTK_LOWLIMIT":"100000000","DAY_INTK_HIGHLIMIT":"10000000000","INTK_UNIT":"CFU","INTK_MEMO":"21.7.11: 기능성 내용 변경","SKLL_IX_IRDNT_RAWMTRL":"생균","PRIMARY_FNCLTY":"유산균 증식 및 유해균 억제･배변활동 원활･장 건강에 도움을 줄 수 있음","IFTKN_ATNT_MATR_CN":"(가) 질환이 있거나 의약품 복용 시 전문가와 상담할 것\n(나) 알레르기 체질 등은 개인에 따라 과민반응을 나타낼 수 있음\n(다) 어린이가 함부로 섭취하지 않도록 일일섭취량 방법을 지도할 것\n(라) 이상사례 발생 시 섭취를 중단하고 전문가와 상담할 것"},{"RCOGN_NO":"","RAWMTRL_NM":"아연","DAY_INTK_LOWLIMIT":"2.55","DAY_INTK_HIGHLIMIT":"12","INTK_UNIT":"mg","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 정상적인 면역기능에 필요\n(2) 정상적인 세포분열에 필요","IFTKN_ATNT_MATR_CN":""}]

## db_286_MLpfJQOIv0Y / c16 / VIOLATION

영상 그룹: violation_1
제품: 생유산균골드 / 종근당건강(주) / DB ID 22548

생유산균골드 제품은 장염을 치료한다.

**판정 근거**

건강 보조 기능을 질병 예방·치료 또는 의약품 대체 주장으로 바꿈. 주간 발표의 질병·의약품 주장 기준에 따른 정답임.

**DB 원문: products:22548.main_functionality**

> ①유산균 증식 및 유해균 억제에 도움을 줄 수 있음 ②배변활동 원활에 도움을 줄 수 있음 ③장건강에 도움을 줄 수 있음

## db_302_cWlIJW4kIg4 / c37 / VIOLATION

영상 그룹: violation_1
제품: 프로메가 알티지 오메가3 듀얼 / 종근당건강(주) / DB ID 40154

프로메가 알티지 오메가3 듀얼의 등록된 하루 섭취량은 4캡슐이다.

**판정 근거**

같은 하루 기준에서 DB는 2캡슐이나 Claim은 4캡슐으로 변경함.

**DB 원문: products:40154.intake_method**

> 1일 1회, 1회 2캡슐(1.04 g) 식전, 식후 관계 없이 충분한 물과 함께 섭취하십시오.

## db_321_UYK0Glxte04 / c18 / VIOLATION

영상 그룹: violation_1
제품: 관절보궁궁 / (주)오투바이오 / DB ID 6177

관절보궁궁 제품은 퇴행성 관절염을 치료한다.

**판정 근거**

건강 보조 기능을 질병 예방·치료 또는 의약품 대체 주장으로 바꿈. 주간 발표의 질병·의약품 주장 기준에 따른 정답임.

**DB 원문: products:6177.main_functionality**

> ①관절 및 연골 건강에 도움을 줄 수 있음
> 
> ①뼈와 치아 형성에 필요②신경과 근육 기능 유지에 필요③정상적인 혈액응고에 필요④골다공증발생 위험 감소에 도움을 줌
> 
> ①정상적인 면역기능에 필요②정상적인 세포분열에 필요
> 
> ①칼슘과 인이 흡수되고 이용되는데 필요②뼈의 형성과 유지에 필요③골다공증발생 위험 감소에 도움을 줌

## db_336_2VSBEs0WzSM / c14 / VIOLATION

영상 그룹: violation_1
제품: 시그니처 메가렉스 / 코스맥스바이오(주) / DB ID 24699

시그니처 메가렉스 제품은 혈전증을 치료한다.

**판정 근거**

건강 보조 기능을 질병 예방·치료 또는 의약품 대체 주장으로 바꿈. 주간 발표의 질병·의약품 주장 기준에 따른 정답임.

**DB 원문: products:24699.main_functionality**

> 1) EPA 및 DHA 함유 유지 : 혈중 중성지질 개선 · 혈행 개선 · 건조한 눈을 개선하여 눈 건강에 도움을 줄 수 있음.
> 2) 비타민E : 항산화 작용을 하여 유해산소로부터 세포를 보호하는데 필요.

## db_340_HU-3Hj26KpA / c13 / OVERCLAIM

영상 그룹: overclaim_1
제품: 올인원 종합비타민 이뮨샷 / 주식회사 네추럴웨이 포천 제2공장 / DB ID 30039

올인원 종합비타민 이뮨샷 제품은 3일 만에 면역세포 활성도를 세 배로 높이는 효과가 확실하다.

**판정 근거**

제품 및 원료의 인정 기능성에는 이 기간·수치·구체적 결과를 보장하는 문장이 없음. 질병 치료나 의약품 대체가 아니라, 인정 범위를 넘는 과장된 효과로 구성함. NLI 점수를 정답으로 사용하지 않으며 실제 NLI의 OVERCLAIM 출력은 별도 평가 대상임.

**DB 원문: products:30039.main_functionality**

> ①정상적인 면역기능에 필요②정상적인 세포분열에 필요
> 
> ①체내 에너지 생성에 필요
> 
> ①뼈 형성에 필요②에너지 이용에 필요③유해산소로부터 세포를 보호하는데 필요
> 
> ①갑상선 호르몬의 합성에 필요②에너지 생성에 필요③신경발달에 필요
> 
> (1) 정상적인 엽산 대사에 필요
> 
> (1) 탄수화물과 에너지 대사에 필요
> 
> (1) 체내 에너지 생성에 필요
> 
> ①단백질 및 아미노산 이용에 필요②혈액의 호모시스테인 수준을 정상으로 유지하는데 필요
> 
> ①결합조직 형성과 기능유지에 필요②철의 흡수에 필요③항산화 작용을 하여 유해산소로부터 세포를 보호하는데 필요
> 
> ①체내 산소운반과 혈액생성에 필요②에너지 생성에 필요
> 
> ①유해산소로부터 세포를 보호하는데 필요
> 
> (1) 어두운 곳에서 시각 적응을 위해 필요
> (2) 피부와 점막을 형성하고 기능을 유지하는데 필요
> (3) 상피세포의 성장과 발달에 필요
> 
> 항산화 작용을 하여 유해산소로부터 세포를 보호하는데 필요
> 
> (1) 체내 탄수화물, 지방, 단백질 대사에 관여
> 
> -산화·환원 효소의 활성에 필요
> 
> ①철의 운반과 이용에 필요②유해산소로부터 세포를 보호하는데 필요
> 
> (1) 정상적인 혈액응고에 필요
> (2) 뼈의 구성에 필요
> 
> (1) 지방, 탄수화물, 단백질 대사와 에너지 생성에 필요
> 
> ①칼슘과 인이 흡수되고 이용되는데 필요②뼈의 형성과 유지에 필요③골다공증발생 위험 감소에 도움을 줌
> 
> (1) 지방, 탄수화물, 단백질 대사와 에너지 생성에 필요

**DB 원문: products:30039.RAWMTRL_STD_INFO**

> [{"RCOGN_NO":"","RAWMTRL_NM":"판토텐산","DAY_INTK_LOWLIMIT":"1.5","DAY_INTK_HIGHLIMIT":"200","INTK_UNIT":"mg","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 지방, 탄수화물, 단백질 대사와 에너지 생성에 필요","IFTKN_ATNT_MATR_CN":"(1) 이상사례 발생 시 섭취를 중단하고 전문가와 상담할 것"},{"RCOGN_NO":"","RAWMTRL_NM":"비타민 D","DAY_INTK_LOWLIMIT":"0.003","DAY_INTK_HIGHLIMIT":"0.01","INTK_UNIT":"mg","INTK_MEMO":"일일섭취량 : 3~10 μg(120∼400 IU)","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 칼슘과 인이 흡수되고 이용되는데 필요\n(2) 뼈의 형성과 유지에 필요\n(3) 골다공증발생 위험 감소에 도움을 줌","IFTKN_ATNT_MATR_CN":"(가) 고칼슘혈증이 있거나 의약품 복용 시 전문가와 상담할 것\n(나) 이상사례 발생 시 섭취를 중단하고 전문가와 상담할 것"},{"RCOGN_NO":"","RAWMTRL_NM":"비오틴","DAY_INTK_LOWLIMIT":"0.009","DAY_INTK_HIGHLIMIT":"0.9","INTK_UNIT":"mg","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 지방, 탄수화물, 단백질 대사와 에너지 생성에 필요","IFTKN_ATNT_MATR_CN":"(1) 이상사례 발생 시 섭취를 중단하고 전문가와 상담할 것"},{"RCOGN_NO":"","RAWMTRL_NM":"비타민 K","DAY_INTK_LOWLIMIT":"0.021","DAY_INTK_HIGHLIMIT":"1","INTK_UNIT":"mg","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 정상적인 혈액응고에 필요\n(2) 뼈의 구성에 필요","IFTKN_ATNT_MATR_CN":"(1) 항응고제 등 복용 시 전문가와 상담할 것\n(2) 이상사례 발생 시 섭취를 중단하고 전문가와 상담할 것"},{"RCOGN_NO":"","RAWMTRL_NM":"구리","DAY_INTK_LOWLIMIT":"0.24","DAY_INTK_HIGHLIMIT":"7","INTK_UNIT":"mg","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 철의 운반과 이용에 필요\n(2) 유해산소로부터 세포를 보호하는데 필요","IFTKN_ATNT_MATR_CN":""},{"RCOGN_NO":"","RAWMTRL_NM":"몰리브덴","DAY_INTK_LOWLIMIT":"0.0075","DAY_INTK_HIGHLIMIT":"0.23","INTK_UNIT":"mg","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 산화·환원 효소의 활성에 필요","IFTKN_ATNT_MATR_CN":""},{"RCOGN_NO":"","RAWMTRL_NM":"크롬","DAY_INTK_LOWLIMIT":"0.009","DAY_INTK_HIGHLIMIT":"9","INTK_UNIT":"mg","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 체내 탄수화물, 지방, 단백질 대사에 관여","IFTKN_ATNT_MATR_CN":"(1) 당뇨병이 있는 경우 섭취 전 전문가와 상담할 것\n(2) 이상사례 발생 시 섭취를 중단하고 전문가와 상담할 것"},{"RCOGN_NO":"","RAWMTRL_NM":"비타민 E","DAY_INTK_LOWLIMIT":"3.3","DAY_INTK_HIGHLIMIT":"400","INTK_UNIT":"mg α-TE","INTK_MEMO":"2021.7.11: 기능성 내용 변경","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"항산화 작용을 하여 유해산소로부터 세포를 보호하는데 필요","IFTKN_ATNT_MATR_CN":""},{"RCOGN_NO":"","RAWMTRL_NM":"베타카로틴","DAY_INTK_LOWLIMIT":"0.42","DAY_INTK_HIGHLIMIT":"7","INTK_UNIT":"mg","INTK_MEMO":"식품원료를 사용하여 제조가공한 경우는 1.26mg 이상(상한섭취량 없음)","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 어두운 곳에서 시각 적응을 위해 필요\n(2) 피부와 점막을 형성하고 기능을 유지하는데 필요\n(3) 상피세포의 성장과 발달에 필요","IFTKN_ATNT_MATR_CN":"(1) 흡연자는 섭취 시 전문가와 상담할 것\n(2) 이상사례 발생 시 섭취를 중단하고 전문가와 상담할 것"},{"RCOGN_NO":"","RAWMTRL_NM":"셀레늄(또는 셀렌)","DAY_INTK_LOWLIMIT":"0.0165","DAY_INTK_HIGHLIMIT":"0.135","INTK_UNIT":"mg","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 유해산소로부터 세포를 보호하는데 필요","IFTKN_ATNT_MATR_CN":""},{"RCOGN_NO":"","RAWMTRL_NM":"철","DAY_INTK_LOWLIMIT":"3.6","DAY_INTK_HIGHLIMIT":"15","INTK_UNIT":"mg","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 체내 산소운반과 혈액생성에 필요\n(2) 에너지 생성에 필요","IFTKN_ATNT_MATR_CN":"특히 6세 이하는 과량섭취하지 않도록 주의"},{"RCOGN_NO":"","RAWMTRL_NM":"비타민 C","DAY_INTK_LOWLIMIT":"30","DAY_INTK_HIGHLIMIT":"1000","INTK_UNIT":"mg","INTK_MEMO":"21.7.11: 기능성 내용 변경 26.7.23 주의사항 변경","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 결합조직 형성과 기능유지에 필요\n(2) 철의 흡수에 필요\n(3) 항산화 작용을 하여 유해산소로부터 세포를 보호하는데 필요","IFTKN_ATNT_MATR_CN":"(1) 과량 섭취하지 않도록 주의할 것\n(2) 신장질환이 있는 경우 섭취 전 전문가와 상담할 것\n(3) 이상사례 발생 시 섭취를 중단하고 전문가와 상담할 것"},{"RCOGN_NO":"","RAWMTRL_NM":"비타민 B6","DAY_INTK_LOWLIMIT":"0.45","DAY_INTK_HIGHLIMIT":"67","INTK_UNIT":"mg","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 단백질 및 아미노산 이용에 필요\n(2) 혈액의 호모시스테인 수준을 정상으로 유지하는데 필요","IFTKN_ATNT_MATR_CN":"(1) 손발 따끔거림, 작열감 또는 저림 등의 이상사례 발생 시 섭취를 중단하고 전문가와 상담할 것"},{"RCOGN_NO":"","RAWMTRL_NM":"비타민 B2","DAY_INTK_LOWLIMIT":"0.42","DAY_INTK_HIGHLIMIT":"40","INTK_UNIT":"mg","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 체내 에너지 생성에 필요","IFTKN_ATNT_MATR_CN":"(1) 이상사례 발생 시 섭취를 중단하고 전문가와 상담할 것"},{"RCOGN_NO":"","RAWMTRL_NM":"비타민 B1","DAY_INTK_LOWLIMIT":"0.36","DAY_INTK_HIGHLIMIT":"100","INTK_UNIT":"mg","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 탄수화물과 에너지 대사에 필요","IFTKN_ATNT_MATR_CN":"(1) 이상사례 발생 시 섭취를 중단하고 전문가와 상담할 것"},{"RCOGN_NO":"","RAWMTRL_NM":"비타민 B12","DAY_INTK_LOWLIMIT":"0.00072","DAY_INTK_HIGHLIMIT":"2","INTK_UNIT":"mg","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 정상적인 엽산 대사에 필요","IFTKN_ATNT_MATR_CN":"(1) 이상사례 발생 시 섭취를 중단하고 전문가와 상담할 것"},{"RCOGN_NO":"","RAWMTRL_NM":"요오드","DAY_INTK_LOWLIMIT":"0.045","DAY_INTK_HIGHLIMIT":"0.15","INTK_UNIT":"mg","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 갑상선 호르몬의 합성에 필요\n(2) 에너지 생성에 필요\n(3) 신경발달에 필요","IFTKN_ATNT_MATR_CN":""},{"RCOGN_NO":"","RAWMTRL_NM":"망간","DAY_INTK_LOWLIMIT":"0.9","DAY_INTK_HIGHLIMIT":"3.5","INTK_UNIT":"mg","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 뼈 형성에 필요\n(2) 에너지 이용에 필요\n(3) 유해산소로부터 세포를 보호하는데 필요","IFTKN_ATNT_MATR_CN":""},{"RCOGN_NO":"","RAWMTRL_NM":"나이아신","DAY_INTK_LOWLIMIT":"4.5","DAY_INTK_HIGHLIMIT":"670","INTK_UNIT":"mg","INTK_MEMO":"니코틴산 4.5～23 mg, 니코틴산아미드 4.5～670 mg","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 체내 에너지 생성에 필요","IFTKN_ATNT_MATR_CN":""},{"RCOGN_NO":"","RAWMTRL_NM":"아연","DAY_INTK_LOWLIMIT":"2.55","DAY_INTK_HIGHLIMIT":"12","INTK_UNIT":"mg","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 정상적인 면역기능에 필요\n(2) 정상적인 세포분열에 필요","IFTKN_ATNT_MATR_CN":""}]

## db_352_CcFF2Di8tmo / c23 / OVERCLAIM

영상 그룹: overclaim_2
제품: 듀오락 얌얌 플러스 / (주)쎌바이오텍 / DB ID 11996

듀오락 얌얌 플러스 제품은 하루 만에 장내 유해균을 99% 깨끗이 제거한다.

**판정 근거**

제품 및 원료의 인정 기능성에는 이 기간·수치·구체적 결과를 보장하는 문장이 없음. 질병 치료나 의약품 대체가 아니라, 인정 범위를 넘는 과장된 효과로 구성함. NLI 점수를 정답으로 사용하지 않으며 실제 NLI의 OVERCLAIM 출력은 별도 평가 대상임.

**DB 원문: products:11996.main_functionality**

> ①유산균 증식 및 유해균 억제에 도움을 줄 수 있음 ②배변활동 원활에 도움을 줄 수 있음 
> 
> ①칼슘과 인이 흡수되고 이용되는데 필요②뼈의 형성과 유지에 필요③골다공증발생 위험 감소에 도움을 줌
> 
> ①정상적인 면역기능에 필요②정상적인 세포분열에 필요

**DB 원문: products:11996.RAWMTRL_STD_INFO**

> [{"RCOGN_NO":"","RAWMTRL_NM":"프로바이오틱스","DAY_INTK_LOWLIMIT":"100000000","DAY_INTK_HIGHLIMIT":"10000000000","INTK_UNIT":"CFU","INTK_MEMO":"21.7.11: 기능성 내용 변경","SKLL_IX_IRDNT_RAWMTRL":"생균","PRIMARY_FNCLTY":"유산균 증식 및 유해균 억제･배변활동 원활･장 건강에 도움을 줄 수 있음","IFTKN_ATNT_MATR_CN":"(가) 질환이 있거나 의약품 복용 시 전문가와 상담할 것\n(나) 알레르기 체질 등은 개인에 따라 과민반응을 나타낼 수 있음\n(다) 어린이가 함부로 섭취하지 않도록 일일섭취량 방법을 지도할 것\n(라) 이상사례 발생 시 섭취를 중단하고 전문가와 상담할 것"},{"RCOGN_NO":"","RAWMTRL_NM":"비타민 D","DAY_INTK_LOWLIMIT":"0.003","DAY_INTK_HIGHLIMIT":"0.01","INTK_UNIT":"mg","INTK_MEMO":"일일섭취량 : 3~10 μg(120∼400 IU)","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 칼슘과 인이 흡수되고 이용되는데 필요\n(2) 뼈의 형성과 유지에 필요\n(3) 골다공증발생 위험 감소에 도움을 줌","IFTKN_ATNT_MATR_CN":"(가) 고칼슘혈증이 있거나 의약품 복용 시 전문가와 상담할 것\n(나) 이상사례 발생 시 섭취를 중단하고 전문가와 상담할 것"},{"RCOGN_NO":"","RAWMTRL_NM":"아연","DAY_INTK_LOWLIMIT":"2.55","DAY_INTK_HIGHLIMIT":"12","INTK_UNIT":"mg","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 정상적인 면역기능에 필요\n(2) 정상적인 세포분열에 필요","IFTKN_ATNT_MATR_CN":""}]

## db_352_CcFF2Di8tmo / c24 / OVERCLAIM

영상 그룹: overclaim_2
제품: 듀오락 얌얌 플러스 / (주)쎌바이오텍 / DB ID 11996

듀오락 얌얌 플러스 제품은 3일 만에 장내 유익균 수를 열 배로 늘리는 효과가 확실하다.

**판정 근거**

제품 및 원료의 인정 기능성에는 이 기간·수치·구체적 결과를 보장하는 문장이 없음. 질병 치료나 의약품 대체가 아니라, 인정 범위를 넘는 과장된 효과로 구성함. NLI 점수를 정답으로 사용하지 않으며 실제 NLI의 OVERCLAIM 출력은 별도 평가 대상임.

**DB 원문: products:11996.main_functionality**

> ①유산균 증식 및 유해균 억제에 도움을 줄 수 있음 ②배변활동 원활에 도움을 줄 수 있음 
> 
> ①칼슘과 인이 흡수되고 이용되는데 필요②뼈의 형성과 유지에 필요③골다공증발생 위험 감소에 도움을 줌
> 
> ①정상적인 면역기능에 필요②정상적인 세포분열에 필요

**DB 원문: products:11996.RAWMTRL_STD_INFO**

> [{"RCOGN_NO":"","RAWMTRL_NM":"프로바이오틱스","DAY_INTK_LOWLIMIT":"100000000","DAY_INTK_HIGHLIMIT":"10000000000","INTK_UNIT":"CFU","INTK_MEMO":"21.7.11: 기능성 내용 변경","SKLL_IX_IRDNT_RAWMTRL":"생균","PRIMARY_FNCLTY":"유산균 증식 및 유해균 억제･배변활동 원활･장 건강에 도움을 줄 수 있음","IFTKN_ATNT_MATR_CN":"(가) 질환이 있거나 의약품 복용 시 전문가와 상담할 것\n(나) 알레르기 체질 등은 개인에 따라 과민반응을 나타낼 수 있음\n(다) 어린이가 함부로 섭취하지 않도록 일일섭취량 방법을 지도할 것\n(라) 이상사례 발생 시 섭취를 중단하고 전문가와 상담할 것"},{"RCOGN_NO":"","RAWMTRL_NM":"비타민 D","DAY_INTK_LOWLIMIT":"0.003","DAY_INTK_HIGHLIMIT":"0.01","INTK_UNIT":"mg","INTK_MEMO":"일일섭취량 : 3~10 μg(120∼400 IU)","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 칼슘과 인이 흡수되고 이용되는데 필요\n(2) 뼈의 형성과 유지에 필요\n(3) 골다공증발생 위험 감소에 도움을 줌","IFTKN_ATNT_MATR_CN":"(가) 고칼슘혈증이 있거나 의약품 복용 시 전문가와 상담할 것\n(나) 이상사례 발생 시 섭취를 중단하고 전문가와 상담할 것"},{"RCOGN_NO":"","RAWMTRL_NM":"아연","DAY_INTK_LOWLIMIT":"2.55","DAY_INTK_HIGHLIMIT":"12","INTK_UNIT":"mg","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 정상적인 면역기능에 필요\n(2) 정상적인 세포분열에 필요","IFTKN_ATNT_MATR_CN":""}]

## db_369_QqSgAP8YFbY / c10 / OVERCLAIM

영상 그룹: overclaim_1
제품: 디어퀸 콜라겐 스틱 / 아미코젠(주)문산제2공장 / DB ID 12200

디어퀸 콜라겐 스틱 제품은 단 3일 만에 얼굴 잔주름을 절반으로 확실히 줄인다.

**판정 근거**

제품 및 원료의 인정 기능성에는 이 기간·수치·구체적 결과를 보장하는 문장이 없음. 질병 치료나 의약품 대체가 아니라, 인정 범위를 넘는 과장된 효과로 구성함. NLI 점수를 정답으로 사용하지 않으며 실제 NLI의 OVERCLAIM 출력은 별도 평가 대상임.

**DB 원문: products:12200.main_functionality**

> [저분자콜라겐펩타이드 AG] (국문) ① 피부 보습에 도움을 줄 수 있음 ② 자외선에 의한 피부손상으로부터 피부건강을 유지하는데 도움을 줄 수 있음(영문) ① May help to moisturize (dry) skin ② May help to maintain good skin health by protecting against damage from UV exposure
> [비타민C] ① 결합조직 형성과 기능유지에 필요 ② 철의 흡수에 필요 ③ 항산화 작용을 하여 유해산소로부터 세포를 보호하는데 필요
> [비오틴]  ① 지방, 탄수화물, 단백질 대사와 에너지 생성에 필요

**DB 원문: products:12200.RAWMTRL_STD_INFO**

> [{"RCOGN_NO":"2023-10","RAWMTRL_NM":"저분자콜라겐펩타이드 AG(제2023-10호)","DAY_INTK_LOWLIMIT":"1","DAY_INTK_HIGHLIMIT":"1","INTK_UNIT":"g/일","INTK_MEMO":"제2023-10호","SKLL_IX_IRDNT_RAWMTRL":"Glycine-Proline-Hydroxyproline(Gly-Pro-Hyp, GPH)","PRIMARY_FNCLTY":"(국문) ① 피부 보습에 도움을 줄 수 있음 : 저분자콜라겐펩타이드 AG로서 1 g/일\n② 자외선에 의한 피부손상으로부터 피부건강을 유지하는데 도움을 줄 수 있음 : 저분자콜라겐펩타이드 AG로서 1 g/일\n(영문) ① May help to moisturize (dry) skin\n② May help to maintain good skin health by protecting against damage from UV exposure","IFTKN_ATNT_MATR_CN":"(1) 영ˑ유아, 어린이, 임산부 및 수유부는 섭취를 피할 것\n(2) 알레르기 체질 등은 개인에 따라 과민반응을 나타낼 수 있음\n(3) 이상사례 발생 시 섭취를 중단하고 전문가와 상담할 것"},{"RCOGN_NO":"","RAWMTRL_NM":"비타민 C","DAY_INTK_LOWLIMIT":"30","DAY_INTK_HIGHLIMIT":"1000","INTK_UNIT":"mg","INTK_MEMO":"21.7.11: 기능성 내용 변경 26.7.23 주의사항 변경","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 결합조직 형성과 기능유지에 필요\n(2) 철의 흡수에 필요\n(3) 항산화 작용을 하여 유해산소로부터 세포를 보호하는데 필요","IFTKN_ATNT_MATR_CN":"(1) 과량 섭취하지 않도록 주의할 것\n(2) 신장질환이 있는 경우 섭취 전 전문가와 상담할 것\n(3) 이상사례 발생 시 섭취를 중단하고 전문가와 상담할 것"},{"RCOGN_NO":"","RAWMTRL_NM":"비오틴","DAY_INTK_LOWLIMIT":"0.009","DAY_INTK_HIGHLIMIT":"0.9","INTK_UNIT":"mg","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 지방, 탄수화물, 단백질 대사와 에너지 생성에 필요","IFTKN_ATNT_MATR_CN":"(1) 이상사례 발생 시 섭취를 중단하고 전문가와 상담할 것"}]

## db_372_03XarAyVtII / c13 / VIOLATION

영상 그룹: violation_1
제품: 위건강엔매스틱 / 코스맥스바이오(주) / DB ID 31064

위건강엔매스틱의 등록된 하루 섭취량은 3포이다.

**판정 근거**

같은 하루 기준에서 DB는 1포이나 Claim은 3포으로 변경함.

**DB 원문: products:31064.intake_method**

> 1일 1회, 1회 1포를 직접 섭취하거나 물과 함께 섭취하십시오.

## db_405_9o2PblzU7zA / c12 / VIOLATION

영상 그룹: violation_1_overclaim_1
제품: 안국 눈에 좋은 루테인 플러스 / (주)서흥 / DB ID 26401

안국 눈에 좋은 루테인 플러스 제품은 황반변성을 치료한다.

**판정 근거**

건강 보조 기능을 질병 예방·치료 또는 의약품 대체 주장으로 바꿈. 주간 발표의 질병·의약품 주장 기준에 따른 정답임.

**DB 원문: products:26401.main_functionality**

> 아연 : ①정상적인 면역기능에 필요②정상적인 세포분열에 필요
> 
> 마리골드꽃추출물 : 노화로 인해 감소될 수 있는 황반색소밀도를 유지하여 눈 건강에 도움을 줄 수 있음
> 
> 셀렌 : ①유해산소로부터 세포를 보호하는데 필요
> 
> 망간 : ①뼈 형성에 필요②에너지 이용에 필요③유해산소로부터 세포를 보호하는데 필요
> 
> 비타민E : ①유해산소로부터 세포를 보호하는데 필요
> 
> 베타카로틴 : ①어두운 곳에서 시각 적응을 위해 필요②피부와 점막을 형성하고 기능을 유지하는데 필요③상피세포의 성장과 발달에 필요
> 
> 구리 : ①철의 운반과 이용에 필요②유해산소로부터 세포를 보호하는데 필요

## db_405_9o2PblzU7zA / c13 / OVERCLAIM

영상 그룹: violation_1_overclaim_1
제품: 안국 눈에 좋은 루테인 플러스 / (주)서흥 / DB ID 26401

안국 눈에 좋은 루테인 플러스 제품은 일주일 만에 시력을 0.3 높여 주는 효과가 확실하다.

**판정 근거**

제품 및 원료의 인정 기능성에는 이 기간·수치·구체적 결과를 보장하는 문장이 없음. 질병 치료나 의약품 대체가 아니라, 인정 범위를 넘는 과장된 효과로 구성함. NLI 점수를 정답으로 사용하지 않으며 실제 NLI의 OVERCLAIM 출력은 별도 평가 대상임.

**DB 원문: products:26401.main_functionality**

> 아연 : ①정상적인 면역기능에 필요②정상적인 세포분열에 필요
> 
> 마리골드꽃추출물 : 노화로 인해 감소될 수 있는 황반색소밀도를 유지하여 눈 건강에 도움을 줄 수 있음
> 
> 셀렌 : ①유해산소로부터 세포를 보호하는데 필요
> 
> 망간 : ①뼈 형성에 필요②에너지 이용에 필요③유해산소로부터 세포를 보호하는데 필요
> 
> 비타민E : ①유해산소로부터 세포를 보호하는데 필요
> 
> 베타카로틴 : ①어두운 곳에서 시각 적응을 위해 필요②피부와 점막을 형성하고 기능을 유지하는데 필요③상피세포의 성장과 발달에 필요
> 
> 구리 : ①철의 운반과 이용에 필요②유해산소로부터 세포를 보호하는데 필요

**DB 원문: products:26401.RAWMTRL_STD_INFO**

> [{"RCOGN_NO":"","RAWMTRL_NM":"아연","DAY_INTK_LOWLIMIT":"2.55","DAY_INTK_HIGHLIMIT":"12","INTK_UNIT":"mg","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 정상적인 면역기능에 필요\n(2) 정상적인 세포분열에 필요","IFTKN_ATNT_MATR_CN":""},{"RCOGN_NO":"","RAWMTRL_NM":"마리골드꽃추출물","DAY_INTK_LOWLIMIT":"10","DAY_INTK_HIGHLIMIT":"20","INTK_UNIT":"mg","INTK_MEMO":"(24.12.23.) 섭취시주의사항, 주된기능성 현행화 / '24 신뢰성 확보","SKLL_IX_IRDNT_RAWMTRL":"루테인(Lutein)","PRIMARY_FNCLTY":"(1) 노화로 인해 감소될 수 있는 황반색소밀도를 유지하여 눈 건강에 도움을 줄 수 있음","IFTKN_ATNT_MATR_CN":"(가) 영‧유아, 어린이, 임산부 및 수유부는 섭취를 피할 것\n(나) 흡연자는 섭취 시 전문가와 상담할 것\n(다) 과다 섭취 시 일시적으로 피부가 황색으로 변할 수 있음\n(라) 이상사례 발생 시 섭취를 중단하고 전문가와 상담할 것"},{"RCOGN_NO":"","RAWMTRL_NM":"셀레늄(또는 셀렌)","DAY_INTK_LOWLIMIT":"0.0165","DAY_INTK_HIGHLIMIT":"0.135","INTK_UNIT":"mg","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 유해산소로부터 세포를 보호하는데 필요","IFTKN_ATNT_MATR_CN":""},{"RCOGN_NO":"","RAWMTRL_NM":"망간","DAY_INTK_LOWLIMIT":"0.9","DAY_INTK_HIGHLIMIT":"3.5","INTK_UNIT":"mg","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 뼈 형성에 필요\n(2) 에너지 이용에 필요\n(3) 유해산소로부터 세포를 보호하는데 필요","IFTKN_ATNT_MATR_CN":""},{"RCOGN_NO":"","RAWMTRL_NM":"비타민 E","DAY_INTK_LOWLIMIT":"3.3","DAY_INTK_HIGHLIMIT":"400","INTK_UNIT":"mg α-TE","INTK_MEMO":"2021.7.11: 기능성 내용 변경","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"항산화 작용을 하여 유해산소로부터 세포를 보호하는데 필요","IFTKN_ATNT_MATR_CN":""},{"RCOGN_NO":"","RAWMTRL_NM":"베타카로틴","DAY_INTK_LOWLIMIT":"0.42","DAY_INTK_HIGHLIMIT":"7","INTK_UNIT":"mg","INTK_MEMO":"식품원료를 사용하여 제조가공한 경우는 1.26mg 이상(상한섭취량 없음)","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 어두운 곳에서 시각 적응을 위해 필요\n(2) 피부와 점막을 형성하고 기능을 유지하는데 필요\n(3) 상피세포의 성장과 발달에 필요","IFTKN_ATNT_MATR_CN":"(1) 흡연자는 섭취 시 전문가와 상담할 것\n(2) 이상사례 발생 시 섭취를 중단하고 전문가와 상담할 것"},{"RCOGN_NO":"","RAWMTRL_NM":"구리","DAY_INTK_LOWLIMIT":"0.24","DAY_INTK_HIGHLIMIT":"7","INTK_UNIT":"mg","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 철의 운반과 이용에 필요\n(2) 유해산소로부터 세포를 보호하는데 필요","IFTKN_ATNT_MATR_CN":""}]

## db_409_NX_s-sRNr2E / c14 / VIOLATION

영상 그룹: violation_2
제품: 에버콜라겐 로열에이지 시그니처 앰플 / (주)네이처텍 / DB ID 27864

에버콜라겐 로열에이지 시그니처 앰플 제품은 아토피 피부염을 치료한다.

**판정 근거**

건강 보조 기능을 질병 예방·치료 또는 의약품 대체 주장으로 바꿈. 주간 발표의 질병·의약품 주장 기준에 따른 정답임.

**DB 원문: products:27864.main_functionality**

> (국문) ① 피부 보습에 도움을 줄 수 있음
>          ② 자외선에 의한 피부손상으로부터 피부 건강을 유지하는데 도움을 줄 수 있음
>          ③관절 및 연골 건강에 도움을 줄 수 있음.
> (영문) ① May help to maintain skin moisturizing
>           ② May help to maintain skin health from skin damage by UV radiation
>           ③ May help to maintain joint and cartilage health

## db_409_NX_s-sRNr2E / c15 / VIOLATION

영상 그룹: violation_2
제품: 에버콜라겐 로열에이지 시그니처 앰플 / (주)네이처텍 / DB ID 27864

에버콜라겐 로열에이지 시그니처 앰플의 소비기한은 제조일로부터 30개월이다.

**판정 근거**

DB의 제조일 기준 18개월을 같은 기준의 30개월로 변경함.

**DB 원문: products:27864.shelf_life**

> 제조일로부터 18개월

## db_433_UKR3tvDLDTI / c18 / VIOLATION

영상 그룹: violation_1
제품: 다이어트 유산균 비에날씬 / (주)서흥 / DB ID 9378

다이어트 유산균 비에날씬 제품은 비만 치료제를 대신할 수 있다.

**판정 근거**

건강 보조 기능을 질병 예방·치료 또는 의약품 대체 주장으로 바꿈. 주간 발표의 질병·의약품 주장 기준에 따른 정답임.

**DB 원문: products:9378.main_functionality**

> 체지방 감소에 도움을 줄 수 있음
> 유산균 증식 및 유해균 억제. 배변활동 원활. 장건강에 도움을 줄 수 있음

## db_442_XM-Hh0iD20g / c17 / OVERCLAIM

영상 그룹: overclaim_1
제품: 다이어트 유산균 비에날씬 프로틴 / (주)서흥 / DB ID 9387

다이어트 유산균 비에날씬 프로틴 제품은 식사량을 줄이지 않아도 일주일 만에 뱃살만 골라 30% 없애 준다.

**판정 근거**

제품 및 원료의 인정 기능성에는 이 기간·수치·구체적 결과를 보장하는 문장이 없음. 질병 치료나 의약품 대체가 아니라, 인정 범위를 넘는 과장된 효과로 구성함. NLI 점수를 정답으로 사용하지 않으며 실제 NLI의 OVERCLAIM 출력은 별도 평가 대상임.

**DB 원문: products:9387.main_functionality**

> 단백질 : (1) 근육, 결합조직 등 신체조직의 구성성분 (2) 효소, 호르몬, 항체의 구성에 필요 (3) 체내 필수 영양성분이나 활성물질의 운반과 저장에 필요 (4) 체액, 산-염기의 균형 유지에 필요 (5) 에너지, 포도당, 지질의 합성에 필요
> 칼슘 : (1) 뼈와 치아 형성에 필요 (2) 신경과 근육 기능 유지에 필요 (3) 정상적인 혈액응고에 필요 (4) 골다공증발생 위험 감소에 도움을 줌
> Lactobacillus gasseriBNR17 : (국문) 체지방감소에 도움을 줄 수 있음(생리활성기능) (영문) May help to reduce body fat.
> 유산균 증식 및 유해균 억제, 배변활동 원활, 장건강에 도움을 줄 수 있음
> 비타민D : (1) 칼슘과 인이 흡수되고 이용되는데 필요 (2) 뼈의 형성과 유지에 필요 (3) 골다공증발생 위험 감소에 도움을 줌

**DB 원문: products:9387.RAWMTRL_STD_INFO**

> [{"RCOGN_NO":"","RAWMTRL_NM":"단백질","DAY_INTK_LOWLIMIT":"12","DAY_INTK_HIGHLIMIT":"999999999","INTK_UNIT":"g","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 근육, 결합조직 등 신체조직의 구성성분\n(2) 효소, 호르몬, 항체의 구성에 필요\n(3) 체내 필수 영양성분이나 활성물질의 운반과 저장에 필요\n(4) 체액, 산-염기의 균형 유지에 필요\n(5) 에너지, 포도당, 지질의 합성에 필요","IFTKN_ATNT_MATR_CN":"특정 단백질에 알레르기를 나타내는 경우에는 섭취 주의"},{"RCOGN_NO":"","RAWMTRL_NM":"칼슘","DAY_INTK_LOWLIMIT":"210","DAY_INTK_HIGHLIMIT":"800","INTK_UNIT":"mg","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 뼈와 치아 형성에 필요\n(2) 신경과 근육 기능 유지에 필요\n(3) 정상적인 혈액응고에 필요\n(4) 골다공증발생 위험 감소에 도움을 줌","IFTKN_ATNT_MATR_CN":""},{"RCOGN_NO":"","RAWMTRL_NM":"비타민 D","DAY_INTK_LOWLIMIT":"0.003","DAY_INTK_HIGHLIMIT":"0.01","INTK_UNIT":"mg","INTK_MEMO":"일일섭취량 : 3~10 μg(120∼400 IU)","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 칼슘과 인이 흡수되고 이용되는데 필요\n(2) 뼈의 형성과 유지에 필요\n(3) 골다공증발생 위험 감소에 도움을 줌","IFTKN_ATNT_MATR_CN":"(가) 고칼슘혈증이 있거나 의약품 복용 시 전문가와 상담할 것\n(나) 이상사례 발생 시 섭취를 중단하고 전문가와 상담할 것"},{"RCOGN_NO":"2017-6","RAWMTRL_NM":"Lactobacillus gasseri BNR17(기능성원료인정제2017-6호)","DAY_INTK_LOWLIMIT":"10000000000","DAY_INTK_HIGHLIMIT":"10000000000","INTK_UNIT":"CFU","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"Lactobacillus gasseri BNR17","PRIMARY_FNCLTY":"(국문) 체지방 감소에 도움을 줄 수 있음(생리활성기능) (영문) May help to reduce body fat","IFTKN_ATNT_MATR_CN":"(1) 산성도가 낮은 음료나 뜨거운 물과 함께 복용하는 것을 피하는 것이 좋음"}]

## db_464_Lum90Oum2y8 / c09 / VIOLATION

영상 그룹: violation_1
제품: 에브리타임 / (주)한국인삼공사 / DB ID 27966

에브리타임 제품은 독감을 예방한다.

**판정 근거**

건강 보조 기능을 질병 예방·치료 또는 의약품 대체 주장으로 바꿈. 주간 발표의 질병·의약품 주장 기준에 따른 정답임.

**DB 원문: products:27966.main_functionality**

> ①면역력 증진에 도움을 줄 수 있음②피로개선에 도움을 줄 수 있음③혈소판 응집 억제를 통한 혈액흐름에 도움을 줄 수 있음④기억력 개선에 도움을 줄 수 있음⑤항산화에 도움을 줄 수 있음

## db_501_VlYQV13qc4E / c09 / VIOLATION

영상 그룹: violation_2
제품: 장건강 포스트 솔루션 / 일동바이오사이언스(주) / DB ID 33343

장건강 포스트 솔루션 제품은 장염을 치료한다.

**판정 근거**

건강 보조 기능을 질병 예방·치료 또는 의약품 대체 주장으로 바꿈. 주간 발표의 질병·의약품 주장 기준에 따른 정답임.

**DB 원문: products:33343.main_functionality**

> 장내 유익균 증식, 유해균 억제, 배변활동에 도움을 줄 수 있음(기타기능II)
> 
> (국문) 면역과민반응에 의한 피부상태 개선에 도움을 줄 수 있음 (생리활성기능) 
> (영문) May help to improve skin condition of immune hypersensitivity reaction

## db_501_VlYQV13qc4E / c10 / VIOLATION

영상 그룹: violation_2
제품: 장건강 포스트 솔루션 / 일동바이오사이언스(주) / DB ID 33343

장건강 포스트 솔루션의 등록된 하루 섭취량은 3포이다.

**판정 근거**

같은 하루 기준에서 DB는 1포이나 Claim은 3포으로 변경함.

**DB 원문: products:33343.intake_method**

> 1일 1회, 1회 1포씩 직접 또는 물과 함께 섭취하십시오.

## db_503_g-JbKI3VyZA / c13 / OVERCLAIM

영상 그룹: overclaim_2
제품: 퍼멘진 발효홍삼 젤리스틱 / (주)서흥헬스케어 / DB ID 39188

퍼멘진 발효홍삼 젤리스틱 제품은 3일 만에 면역세포 활성도를 세 배로 높이는 효과가 확실하다.

**판정 근거**

제품 및 원료의 인정 기능성에는 이 기간·수치·구체적 결과를 보장하는 문장이 없음. 질병 치료나 의약품 대체가 아니라, 인정 범위를 넘는 과장된 효과로 구성함. NLI 점수를 정답으로 사용하지 않으며 실제 NLI의 OVERCLAIM 출력은 별도 평가 대상임.

**DB 원문: products:39188.main_functionality**

> 홍삼 : 면역력 증진･피로개선･혈소판 응집억제를 통한 혈액흐름･기억력 개선･항산화에 도움을 줄 수 있음 
> 아연 : (1) 정상적인 면역기능에 필요 (2) 정상적인 세포분열에 필요
> 비타민D : (1) 칼슘과 인이 흡수되고 이용되는데 필요 (2) 뼈의 형성과 유지에 필요 (3) 골다공증발생 위험 감소에 도움을 줌

**DB 원문: products:39188.RAWMTRL_STD_INFO**

> [{"RCOGN_NO":"","RAWMTRL_NM":"홍삼","DAY_INTK_LOWLIMIT":"2.4","DAY_INTK_HIGHLIMIT":"80","INTK_UNIT":"mg","INTK_MEMO":"면역력증진·피로개선:진세노사이드Rg1,Rb1및Rg3의합계로서3～80mg,혈소판응집억제를 통한 혈액흐름·기억력 개선·항산화:진세노사이드Rg1,Rb1및Rg3의합계로서2.4～80mg,갱년기여성의 건강:진세노사이드Rg1,Rb1및Rg3의합계로서25∼80mg","SKLL_IX_IRDNT_RAWMTRL":"진세노사이드 Rg1, Rb1 및 Rg3 의 합","PRIMARY_FNCLTY":"(1)기능성 내용 : 면역력 증진･피로개선･혈소판 응집억제를 통한 혈액흐름･기억력 개선･항산화･갱년기 여성의 건강에 도움을 줄 수 있음\n(2) 일일섭취량\n (가)면역력 증진･피로개선에 도움을 줄 수 있음 : 진세노사이드 Rg1, Rb1 및 Rg3의 합계로서 3~80 mg\n (나)혈소판 응집억제를 통한 혈액흐름･기억력 개선･항산화에 도움을 줄 수 있음 : 진세노사이드 Rg1, Rb1 및 Rg3의 합계로서 2.4~80 mg\n (다)갱년기 여성의 건강에 도움을 줄 수 있음 : 진세노사이드 Rg1, Rb1 및 Rg3의 합계로서 25~80 mg","IFTKN_ATNT_MATR_CN":"(3) 섭취 시 주의사항 \n (가)당뇨치료제 및 혈액항응고제 복용 시 섭취에 주의\n (나)알레르기 체질 등은 개인에 따라 과민반응을 나타낼 수 있음\n (다)이상사례 발생 시 섭취를 중단하고 전문가와 상담할 것"},{"RCOGN_NO":"","RAWMTRL_NM":"아연","DAY_INTK_LOWLIMIT":"2.55","DAY_INTK_HIGHLIMIT":"12","INTK_UNIT":"mg","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 정상적인 면역기능에 필요\n(2) 정상적인 세포분열에 필요","IFTKN_ATNT_MATR_CN":""},{"RCOGN_NO":"","RAWMTRL_NM":"비타민 D","DAY_INTK_LOWLIMIT":"0.003","DAY_INTK_HIGHLIMIT":"0.01","INTK_UNIT":"mg","INTK_MEMO":"일일섭취량 : 3~10 μg(120∼400 IU)","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 칼슘과 인이 흡수되고 이용되는데 필요\n(2) 뼈의 형성과 유지에 필요\n(3) 골다공증발생 위험 감소에 도움을 줌","IFTKN_ATNT_MATR_CN":"(가) 고칼슘혈증이 있거나 의약품 복용 시 전문가와 상담할 것\n(나) 이상사례 발생 시 섭취를 중단하고 전문가와 상담할 것"}]

## db_503_g-JbKI3VyZA / c14 / OVERCLAIM

영상 그룹: overclaim_2
제품: 퍼멘진 발효홍삼 젤리스틱 / (주)서흥헬스케어 / DB ID 39188

퍼멘진 발효홍삼 젤리스틱 제품은 단 한 번 섭취로 면역세포 활동이 즉시 두 배로 늘어난다.

**판정 근거**

제품 및 원료의 인정 기능성에는 이 기간·수치·구체적 결과를 보장하는 문장이 없음. 질병 치료나 의약품 대체가 아니라, 인정 범위를 넘는 과장된 효과로 구성함. NLI 점수를 정답으로 사용하지 않으며 실제 NLI의 OVERCLAIM 출력은 별도 평가 대상임.

**DB 원문: products:39188.main_functionality**

> 홍삼 : 면역력 증진･피로개선･혈소판 응집억제를 통한 혈액흐름･기억력 개선･항산화에 도움을 줄 수 있음 
> 아연 : (1) 정상적인 면역기능에 필요 (2) 정상적인 세포분열에 필요
> 비타민D : (1) 칼슘과 인이 흡수되고 이용되는데 필요 (2) 뼈의 형성과 유지에 필요 (3) 골다공증발생 위험 감소에 도움을 줌

**DB 원문: products:39188.RAWMTRL_STD_INFO**

> [{"RCOGN_NO":"","RAWMTRL_NM":"홍삼","DAY_INTK_LOWLIMIT":"2.4","DAY_INTK_HIGHLIMIT":"80","INTK_UNIT":"mg","INTK_MEMO":"면역력증진·피로개선:진세노사이드Rg1,Rb1및Rg3의합계로서3～80mg,혈소판응집억제를 통한 혈액흐름·기억력 개선·항산화:진세노사이드Rg1,Rb1및Rg3의합계로서2.4～80mg,갱년기여성의 건강:진세노사이드Rg1,Rb1및Rg3의합계로서25∼80mg","SKLL_IX_IRDNT_RAWMTRL":"진세노사이드 Rg1, Rb1 및 Rg3 의 합","PRIMARY_FNCLTY":"(1)기능성 내용 : 면역력 증진･피로개선･혈소판 응집억제를 통한 혈액흐름･기억력 개선･항산화･갱년기 여성의 건강에 도움을 줄 수 있음\n(2) 일일섭취량\n (가)면역력 증진･피로개선에 도움을 줄 수 있음 : 진세노사이드 Rg1, Rb1 및 Rg3의 합계로서 3~80 mg\n (나)혈소판 응집억제를 통한 혈액흐름･기억력 개선･항산화에 도움을 줄 수 있음 : 진세노사이드 Rg1, Rb1 및 Rg3의 합계로서 2.4~80 mg\n (다)갱년기 여성의 건강에 도움을 줄 수 있음 : 진세노사이드 Rg1, Rb1 및 Rg3의 합계로서 25~80 mg","IFTKN_ATNT_MATR_CN":"(3) 섭취 시 주의사항 \n (가)당뇨치료제 및 혈액항응고제 복용 시 섭취에 주의\n (나)알레르기 체질 등은 개인에 따라 과민반응을 나타낼 수 있음\n (다)이상사례 발생 시 섭취를 중단하고 전문가와 상담할 것"},{"RCOGN_NO":"","RAWMTRL_NM":"아연","DAY_INTK_LOWLIMIT":"2.55","DAY_INTK_HIGHLIMIT":"12","INTK_UNIT":"mg","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 정상적인 면역기능에 필요\n(2) 정상적인 세포분열에 필요","IFTKN_ATNT_MATR_CN":""},{"RCOGN_NO":"","RAWMTRL_NM":"비타민 D","DAY_INTK_LOWLIMIT":"0.003","DAY_INTK_HIGHLIMIT":"0.01","INTK_UNIT":"mg","INTK_MEMO":"일일섭취량 : 3~10 μg(120∼400 IU)","SKLL_IX_IRDNT_RAWMTRL":"","PRIMARY_FNCLTY":"(1) 칼슘과 인이 흡수되고 이용되는데 필요\n(2) 뼈의 형성과 유지에 필요\n(3) 골다공증발생 위험 감소에 도움을 줌","IFTKN_ATNT_MATR_CN":"(가) 고칼슘혈증이 있거나 의약품 복용 시 전문가와 상담할 것\n(나) 이상사례 발생 시 섭취를 중단하고 전문가와 상담할 것"}]

## db_504_-Mkbm1V_NQc / c21 / OVERCLAIM

영상 그룹: overclaim_1
제품: 콜레올로지 티 하비탈출(Hobby Escape) / (주)비오팜 / DB ID 37182

콜레올로지 티 하비탈출(Hobby Escape) 제품은 2주 만에 체지방 5kg을 확실히 줄인다.

**판정 근거**

제품 및 원료의 인정 기능성에는 이 기간·수치·구체적 결과를 보장하는 문장이 없음. 질병 치료나 의약품 대체가 아니라, 인정 범위를 넘는 과장된 효과로 구성함. NLI 점수를 정답으로 사용하지 않으며 실제 NLI의 OVERCLAIM 출력은 별도 평가 대상임.

**DB 원문: products:37182.main_functionality**

> -기억력 개선·혈행 개선에 도움을 줄 수 있음
> 
> 장내 유익균 증식 및 배변활동 원활에 도움을 줄 수 있음
> 
> 체지방 감소에 도움을 줄 수 있음

**DB 원문: products:37182.RAWMTRL_STD_INFO**

> [{"RCOGN_NO":"","RAWMTRL_NM":"은행잎 추출물","DAY_INTK_LOWLIMIT":"28","DAY_INTK_HIGHLIMIT":"36","INTK_UNIT":"mg","INTK_MEMO":"(24.12.20.) 섭취시주의사항, 주된기능성 현행화 / '24 신뢰성 확보","SKLL_IX_IRDNT_RAWMTRL":"플라보놀 배당체(flavonol glycoside)","PRIMARY_FNCLTY":"(1) 기능성 내용 : 기억력 개선･혈행 개선에 도움을 줄 수 있음","IFTKN_ATNT_MATR_CN":"(1) 어린이, 임산부 및 수유부는 섭취를 피할 것\n(2) 수술 전후, 의약품(항응고제) 복용 시 전문가와 상담할 것\n(3) 이상사례 발생 시 섭취를 중단하고 전문가와 상담할 것"},{"RCOGN_NO":"","RAWMTRL_NM":"프락토올리고당","DAY_INTK_LOWLIMIT":"3","DAY_INTK_HIGHLIMIT":"8","INTK_UNIT":"g","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"프락토올리고당","PRIMARY_FNCLTY":"(1) 장내 유익균 증식 및 배변활동 원활에 도움을 줄 수 있음","IFTKN_ATNT_MATR_CN":"(가) 섭취 시 가스참, 트림, 복통, 복부팽만감 등이 발생할 수 있음\n(나) 이상사례 발생 시 섭취를 중단하고 전문가와 상담할 것"},{"RCOGN_NO":"","RAWMTRL_NM":"콜레우스포스콜리 추출물","DAY_INTK_LOWLIMIT":"50","DAY_INTK_HIGHLIMIT":"50","INTK_UNIT":"mg","INTK_MEMO":"","SKLL_IX_IRDNT_RAWMTRL":"콜레우스 포스콜리(Coleus forskohlii)의 뿌리","PRIMARY_FNCLTY":"(1) 체지방 감소에 도움을 줄 수 있음","IFTKN_ATNT_MATR_CN":"(1) 어린이, 임산부 및 수유부는 섭취를 피할 것\n(2) 항응고제 또는 혈압조절제를 복용하거나 혈압이 낮은 경우 전문가와 상담할 것\n(3) 이상사례 발생 시 섭취를 중단하고 전문가와 상담할 것"}]
