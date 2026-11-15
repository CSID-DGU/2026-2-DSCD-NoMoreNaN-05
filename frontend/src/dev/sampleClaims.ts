/**
 * 미리보기용 예시 데이터 — Figma v5 final 화면에 적힌 문구를 그대로 옮겼어요.
 * 실제 데이터는 API 명세가 나오면 백엔드에서 받아요.
 */
import type { ClaimPart } from '@/features/result/ClaimPart'

export const SAMPLE_PARTS: ClaimPart[] = [
  {
    kind: 'compare',
    item: '섭취 방법',
    tone: 'VIOLATION',
    aHead: '광고에서',
    aValue: '하루 하나',
    bHead: '식약처 등록 정보 · 섭취 방법',
    bValue: '1일 2회, 1회 1정',
    explain: '광고는 하루 1정, 등록된 섭취 방법은 하루 2정이에요.',
  },
  {
    kind: 'reason',
    item: '효능 표현',
    tone: 'UNCLEAR',
    head: '판단 사유 · 광고가 모호함',
    text: '‘식단·식품 상관없이 관리 가능’과 같은 내용이 인정 기능성에 없어 맞는지 판단할 수 없어요.',
  },
]

export const SAMPLE_EXPRESSION_PART: ClaimPart = {
  kind: 'compare',
  item: '효능 표현',
  aHead: '지적된 표현',
  aValue: '“엉덩이 허벅지 체지방 탈출”',
  bHead: '등록된 기능성',
  bValue: '체지방 감소에 도움을 줄 수 있음',
  explain: '부위를 정해 빠진다거나 ‘탈출’처럼 결과를 단정하는 근거는 인정된 기능성에 없어요.',
}

export const SAMPLE_NOTICE_PART: ClaimPart = {
  kind: 'notice',
  item: '안내',
  head: '판정 건너뜀 · 제품을 찾지 못함',
  text: '광고 제품을 식약처 공개 데이터에서 찾지 못해 이 주장은 판정하지 않았어요.',
}
