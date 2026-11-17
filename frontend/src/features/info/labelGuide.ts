/**
 * 서비스 소개·검증 기준 화면의 라벨 설명 (이용자용 쉬운 말).
 * 뜻은 팀 문서 data/exports/final_result_ui_cases.md §2-3·§3 기준이에요.
 */
import type { Label } from '@/lib/labels'

type LabelGuide = {
  /** 한 줄 요약 (서비스 소개) */
  summary: string
  /** 검증 기준 카드 본문 */
  detail: string
  /** 이런 광고 문장이면 */
  example: string
  /** 예시를 그렇게 본 이유 */
  why: string
}

export const LABEL_GUIDE: Record<Label, LabelGuide> = {
  VIOLATION: {
    summary: '식약처 정보와 다르거나 쓰면 안 되는 표현',
    detail: '식약처에 등록된 내용과 다르거나, ‘병을 고친다’, ‘약 대신 먹어도 된다’처럼 건강기능식품 광고에서 쓸 수 없는 표현이에요.',
    example: '“하루 3정이면 충분해요”',
    why: '제품에 등록된 섭취량은 하루 1정이에요',
  },
  OVERCLAIM: {
    summary: '효과를 실제보다 부풀린 표현',
    detail: '식약처가 인정한 효과는 있지만, 그보다 훨씬 크거나 빠른 효과가 있는 것처럼 말했어요.',
    example: '“하루 만에 유해균 99% 제거”',
    why: '인정된 효과는 ‘유익균 증식·유해균 억제에 도움’까지예요',
  },
  UNCLEAR: {
    summary: '공개 정보만으로는 판단하기 어려움',
    detail: '틀렸다는 뜻은 아니에요. 공개된 정보에 없는 내용이거나, 광고가 애매하게 말해서 맞는지 판단할 수 없었어요.',
    example: '“유산균 20억 마리”',
    why: '얼마만큼 먹었을 때 기준인지 없어서 비교할 수 없어요',
  },
  SUPPORTED: {
    summary: '식약처 정보와 같음',
    detail: '성분·함량·먹는 방법·효과가 식약처에 등록된 내용과 같아요.',
    example: '“아연 12mg 꽉꽉!”',
    why: '제품에 등록된 아연 함량과 같아요',
  },
  OUT_OF_SCOPE: {
    summary: '가격·순위처럼 확인할 수 없는 말',
    detail: '가격, 판매 순위, 수상 경력처럼 공개 정보로 확인할 수 없는 말은 따로 모아 보여 드려요.',
    example: '“판매량 1위”',
    why: '판매 순위는 공개 정보에 없어요',
  },
  DISCLAIMER: {
    summary: '광고에 넣는 안내 문구',
    detail: '‘개인에 따라 다를 수 있어요’처럼 광고에 넣는 안내 문구예요. 제품을 자랑하는 말이 아니라서 따로 모아 보여 드려요.',
    example: '“개인에 따라 결과가 다를 수 있습니다”',
    why: '제품에 대한 주장이 아닌 안내 문구예요',
  },
}
