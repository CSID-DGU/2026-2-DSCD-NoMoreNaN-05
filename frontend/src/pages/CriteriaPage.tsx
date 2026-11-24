import { ArrowRight, Bot, ChevronRight, FileQuestion, Info, MessageCircleQuestion } from 'lucide-react'
import { Fragment } from 'react'
import { Tag } from '@/components/ui/Tag'
import { IconTile, InfoLayout, InfoSection } from '@/features/info/InfoLayout'
import { LABEL_GUIDE } from '@/features/info/labelGuide'
import { cn } from '@/lib/cn'
import { LABEL_PRIORITY as PRIORITY, LABEL_STYLES, LABELS, type Label } from '@/lib/labels'

/** 팀 문서 §2-1 표의 예시 문장 */
const EXAMPLE_PARTS: { item: string; value: string; tone: Label }[] = [
  { item: '성분', value: '비타민D', tone: 'SUPPORTED' },
  { item: '수치', value: '0.5mg', tone: 'VIOLATION' },
  { item: '효과', value: '뼈 형성에 필요', tone: 'SUPPORTED' },
]

// 갈래 이름은 결과 카드에 그대로 보여서 바꾸지 않아요
const REASONS = [
  {
    icon: FileQuestion,
    title: '공식 정보에 없는 내용',
    text: '식약처에 등록되는 정보에 원래 없는 내용이에요.',
    examples: ['포장 단위 “500mg × 90정”', '원산지 “청정 지역에서 키운”', '“국내 최초”'],
  },
  {
    icon: MessageCircleQuestion,
    title: '광고가 모호함',
    text: '기준이나 대상이 빠져 있어서 비교할 수 없어요.',
    examples: ['“유산균 20억 마리” (얼마만큼 먹었을 때?)', '“비타민 듬뿍” (어떤 비타민?)', '“3가지 효과” (무엇을 센 걸까?)'],
  },
  {
    icon: Bot,
    title: '자동 판단 실패',
    text: '자동 분석이 정확하게 판단하지 못했어요.',
    examples: ['처음 보는 브랜드 이름의 성분', '무엇과 비교할지 정하기 어려운 수치', '뜻이 애매해서 판단이 엇갈린 문장'],
  },
]

const COMPARE_ROWS = [
  { item: '성분', ad: '‘○○ 성분이 들어 있어요’', official: '제품에 등록된 원료 목록 (다른 이름으로 적힌 것도 찾아요)' },
  { item: '수치', ad: '함량, 하루에 먹는 양, 소비기한, 하루 권장량 대비 %', official: '제품에 등록된 함량·먹는 방법·소비기한, 식약처 영양성분 기준' },
  { item: '인증', ad: '‘건강기능식품’, ‘식약처 인정 원료’, ‘GMP 인증’', official: '식약처 제품 신고 정보, 식약처가 인정한 원료 정보, 제조 업체 정보' },
  { item: '효과', ad: '‘피로 회복에 좋아요’ 같은 효과', official: '식약처가 인정한 효과 문구, 먹을 때 주의사항, 질병·의약품 표현 기준' },
]

const NOTES = [
  '결과는 식약처 공개 정보와 비교한 참고용이며, 법적인 판단은 아닙니다.',
  'GMP(우수제조기준) 인증서는 공개 정보에 직접 나오지 않아요. 대신 건강기능식품 제조업은 GMP 적용이 의무라서, 등록된 업종으로 확인해요.',
  '광고 속 제품이 무엇인지 정확히 알 수 없으면, 그 말은 확인하지 않고 ‘판단 보류’로 보여 드려요.',
  '목소리 인식과 자막 읽기는 자동으로 이뤄져서 가끔 틀릴 수 있어요. 결과 화면에서 비교한 원문을 함께 확인해 주세요.',
]

const TOC = [
  ['labels', '6가지 결과'],
  ['priority', '한 문장에 결과가 여러 개면'],
  ['unclear', '판단 보류가 나오는 이유'],
  ['compare', '무엇과 비교하나요'],
  ['notes', '알아 두세요'],
] as const

/** 검증 기준 */
export default function CriteriaPage() {
  return (
    <InfoLayout
      active="criteria"
      align="left"
      eyebrow="검증 기준"
      title="이렇게 확인해요"
      sub="광고에서 한 말을 성분·수치·효과처럼 확인할 수 있는 부분으로 나누고, 식약처에 등록된 정보와 하나씩 비교해요."
    >
      <nav aria-label="이 페이지 목차" className="flex flex-wrap gap-2 pt-2">
        {TOC.map(([id, label]) => (
          <a
            key={id}
            href={`#${id}`}
            className="rounded-pill border border-line-hair px-4 py-2 text-small-m text-text-secondary hover:border-text-secondary hover:text-text-primary"
          >
            {label}
          </a>
        ))}
      </nav>

      <InfoSection
        id="labels"
        title="6가지 결과"
        sub="위의 셋은 한 번 더 살펴볼 필요가 있는 말이고, 아래 셋은 문제가 없거나 확인하지 않는 말이에요."
      >
        <div className="grid grid-cols-3 gap-5">
          {LABELS.map((label) => {
            const g = LABEL_GUIDE[label]
            const s = LABEL_STYLES[label]
            return (
              <article key={label} className="flex overflow-hidden rounded-card border border-line-hair bg-bg-raised">
                <span aria-hidden className={cn('w-1.5 shrink-0', s.vivid)} />
                <div className="flex flex-1 flex-col gap-4 p-6">
                  <Tag tone={label} className="self-start" />
                  <p className="text-small text-text-secondary">{g.detail}</p>
                  <div className={cn('mt-auto flex flex-col gap-1 rounded-popover px-4 py-3', s.tint)}>
                    <p className="text-small-m text-text-primary">{g.example}</p>
                    <p className={cn('text-meta', s.text)}>→ {g.why}</p>
                  </div>
                </div>
              </article>
            )
          })}
        </div>
      </InfoSection>

      <InfoSection
        id="priority"
        title="한 문장에 결과가 여러 개면"
        sub="한 문장에 성분, 수치, 효과가 함께 있으면 따로따로 확인해요. 그중 가장 주의가 필요한 결과를 그 문장의 결과로 보여 드려요."
      >
        <div className="grid grid-cols-[1fr_1.15fr] gap-5">
          <div className="flex flex-col gap-6 rounded-card bg-bg-sunken p-8">
            <h3 className="text-h3 text-text-primary">주의가 필요한 순서</h3>
            <ol className="flex flex-wrap items-center gap-2">
              {PRIORITY.map((label, i) => (
                <Fragment key={label}>
                  <li>
                    <Tag tone={label} />
                  </li>
                  {i < PRIORITY.length - 1 && <ChevronRight aria-hidden size={16} className="text-text-disabled" />}
                </Fragment>
              ))}
            </ol>
            <p className="text-small text-text-secondary">
              왼쪽일수록 더 주의가 필요해요. 광고에 넣는 안내 문구(면책 문구)는 처음부터 따로 모아요.
            </p>
          </div>

          <div className="flex flex-col gap-5 rounded-card border border-line-hair p-8">
            <h3 className="text-h3 text-text-primary">예시</h3>
            <p className="text-claim text-text-primary">“0.5mg 비타민D, 뼈 형성에 필요해요”</p>
            <ul className="flex flex-col divide-y divide-line-hair border-y border-line-hair">
              {EXAMPLE_PARTS.map((p) => (
                <li key={p.item} className="flex items-center gap-4 py-3">
                  <span className="w-10 text-meta-m text-text-tertiary">{p.item}</span>
                  <span className="flex-1 text-small text-text-primary">{p.value}</span>
                  <Tag tone={p.tone} size="sm" />
                </li>
              ))}
            </ul>
            <div className="flex items-center gap-3">
              <span className="text-small-m text-text-secondary">이 문장의 결과</span>
              <ArrowRight aria-hidden size={16} className="text-text-disabled" />
              <Tag tone="VIOLATION" />
              <span className="text-meta text-text-tertiary">‘일치’ 2개, ‘위반’ 1개 중 더 주의가 필요한 쪽</span>
            </div>
          </div>
        </div>
      </InfoSection>

      <InfoSection
        id="unclear"
        title="판단 보류가 나오는 이유"
        sub="‘판단 보류’는 틀렸다는 뜻이 아니라, 공개 정보만으로는 맞는지 알 수 없다는 뜻이에요. 결과 화면에서 아래 셋 중 어떤 이유인지 함께 알려 드려요."
      >
        <div className="grid grid-cols-3 gap-5">
          {REASONS.map(({ icon: Icon, title, text, examples }) => (
            <div key={title} className="flex flex-col gap-5 rounded-card border border-line-hair p-7">
              <IconTile className="bg-label-unclear-tint text-label-unclear">
                <Icon size={22} />
              </IconTile>
              <div className="flex flex-col gap-1.5">
                <h3 className="text-h3 text-text-primary">{title}</h3>
                <p className="text-small text-text-secondary">{text}</p>
              </div>
              <ul className="flex flex-col gap-1.5 border-t border-line-hair pt-4">
                {examples.map((e) => (
                  <li key={e} className="flex gap-2 text-meta text-text-tertiary">
                    <span aria-hidden>·</span>
                    {e}
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </InfoSection>

      <InfoSection id="compare" title="무엇과 비교하나요" sub="광고에서 한 말의 종류에 따라 비교하는 정보가 달라요.">
        <table className="w-full border-t border-line-strong text-left">
          <thead>
            <tr className="border-b border-line-hair text-small-m text-text-tertiary">
              <th scope="col" className="w-32 py-4 pr-6 font-medium">
                종류
              </th>
              <th scope="col" className="py-4 pr-6 font-medium">
                광고에서 이런 말을 하면
              </th>
              <th scope="col" className="py-4 font-medium">
                이것과 비교해요
              </th>
            </tr>
          </thead>
          <tbody>
            {COMPARE_ROWS.map((r) => (
              <tr key={r.item} className="border-b border-line-hair">
                <th scope="row" className="py-5 pr-6 text-body-m text-text-primary">
                  {r.item}
                </th>
                <td className="py-5 pr-6 text-body text-text-secondary">{r.ad}</td>
                <td className="py-5 text-body text-text-secondary">{r.official}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </InfoSection>

      <InfoSection id="notes" title="알아 두세요">
        <ul className="flex flex-col gap-3 rounded-card bg-bg-sunken p-8">
          {NOTES.map((n) => (
            <li key={n} className="flex gap-3 text-body text-text-secondary">
              <Info aria-hidden size={18} className="mt-1 shrink-0 text-text-tertiary" />
              {n}
            </li>
          ))}
        </ul>
      </InfoSection>
    </InfoLayout>
  )
}
