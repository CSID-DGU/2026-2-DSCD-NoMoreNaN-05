import {
  AudioLines,
  BadgeCheck,
  Database,
  Download,
  FlaskConical,
  HeartPulse,
  Ruler,
  ScanText,
  SearchX,
  ShieldCheck,
  Sparkles,
} from 'lucide-react'
import { Tag } from '@/components/ui/Tag'
import { IconTile, InfoLayout, InfoSection } from '@/features/info/InfoLayout'
import { LABEL_GUIDE } from '@/features/info/labelGuide'
import { ClaimCard } from '@/features/result/ClaimCard'
import type { ClaimPart } from '@/features/result/ClaimPart'
import { LABEL_STYLES, LABELS } from '@/lib/labels'

/** 머리 오른쪽 결과 카드 예시 — 실제 결과 화면과 같은 카드 컴포넌트. 실제 제품처럼 보이지 않게 이름은 '예시 제품' */
const PREVIEW_PARTS: ClaimPart[] = [
  {
    kind: 'compare',
    item: '효능 표현',
    tone: 'OVERCLAIM',
    aHead: '지적된 표현',
    aValue: '“장 속 유해균이 싹 사라져요”',
    bHead: '비교한 인정 기능성',
    bValue: '유익균 증식 및 유해균 억제에 도움을 줄 수 있음',
    explain: '인정된 효과는 유해균을 ‘억제’하는 데 도움을 주는 정도예요.',
  },
  {
    kind: 'compare',
    item: '원료',
    tone: 'SUPPORTED',
    aHead: '광고에서',
    aValue: '프로바이오틱스',
    bHead: '식약처 등록 정보 · 원료',
    bValue: '프로바이오틱스',
    explain: '광고한 성분이 제품에 등록된 원료에 있어요.',
  },
]

const PAINS = [
  {
    icon: Sparkles,
    title: '과장된 말은 몇 초 만에 지나가요',
    text: '‘하루 만에’, ‘100% 효과’ 같은 말이 순식간에 지나가, 사실인지 따져 볼 틈이 없어요.',
  },
  {
    icon: SearchX,
    title: '어디서 확인해야 할지 모르겠어요',
    text: '제품 정보는 식약처에 공개돼 있지만, 찾아서 읽기가 쉽지 않아요.',
  },
  {
    icon: ScanText,
    title: '맞는 말과 부풀린 말이 섞여 있어요',
    text: '사실 사이에 과장이 섞여 있으면 구별하기 어려워요.',
  },
]

// 단계 이름은 처리 화면(S2)과 같게 둬요
const STEPS = [
  { no: '01', icon: Download, title: '영상 가져오기', text: '주소만 넣으면 YouTube · 인스타그램 · 틱톡 영상을 불러와요.' },
  { no: '02', icon: AudioLines, title: '주장 추출', text: '영상 속 목소리와 자막을 읽고, 제품에 대해 한 말을 문장마다 골라내요.' },
  { no: '03', icon: ShieldCheck, title: '주장 검증', text: '광고 속 제품을 찾아, 식약처에 등록된 정보와 하나씩 맞춰 봐요.' },
]

const CHECKS = [
  { icon: FlaskConical, title: '성분', quote: '“비타민D 듬뿍”', text: '들어 있다고 한 성분이 실제 제품에 들어 있는지' },
  { icon: Ruler, title: '수치', quote: '“하루 3정이면 충분”', text: '함량, 하루에 먹는 양, 소비기한 같은 수치가 맞는지' },
  { icon: BadgeCheck, title: '인증', quote: '“식약처 인정 원료”', text: '‘건강기능식품’, ‘식약처 인정’ 같은 말이 사실인지' },
  { icon: HeartPulse, title: '효과', quote: '“먹기만 해도 살이 쏙”', text: '인정된 효과보다 부풀리거나, 병을 고친다고 말하지 않는지' },
]

/** 서비스 소개 */
export default function AboutPage() {
  return (
    <InfoLayout
      active="about"
      eyebrow="서비스 소개"
      title={
        <>
          광고에서 한 말,
          <br />
          사실인지 확인해 드려요
        </>
      }
      sub="건강기능식품 광고 영상 주소를 넣으면, 광고에서 한 말을 하나하나 찾아 식약처에 등록된 제품 정보와 비교해 드려요."
      aside={
        <div className="relative w-140 shrink-0" aria-label="결과 카드 예시">
          {/* 뒤에 겹친 카드 — 여러 결과가 쌓인 느낌 */}
          <div aria-hidden className="absolute inset-x-6 -bottom-3 h-full rounded-card border border-line-hair bg-bg-raised" />
          <div className="relative rounded-card shadow-popover">
            <ClaimCard
              tone="OVERCLAIM"
              productName="예시 제품"
              timeRange="00:12 – 00:16"
              sentence="프로바이오틱스 한 포면 장 속 유해균이 싹 사라져요"
              explain="식약처가 인정한 효과보다 훨씬 크게 말하고 있어요."
              parts={PREVIEW_PARTS}
              defaultOpen
            />
          </div>
          <span className="absolute -top-3 left-6 rounded-pill bg-text-primary px-3 py-1 text-tag-sm text-text-on-dark">
            결과 예시
          </span>
        </div>
      }
    >
      <InfoSection title="이런 광고, 본 적 있나요?">
        <div className="grid grid-cols-3 gap-5">
          {PAINS.map(({ icon: Icon, title, text }) => (
            <div key={title} className="flex flex-col gap-4 rounded-card bg-bg-sunken p-7">
              <Icon aria-hidden size={24} className="text-text-tertiary" />
              <div className="flex flex-col gap-1.5">
                <h3 className="text-h3 text-text-primary">{title}</h3>
                <p className="text-small text-text-secondary">{text}</p>
              </div>
            </div>
          ))}
        </div>
      </InfoSection>

      <InfoSection title="어떻게 확인하나요" sub="주소를 넣으면 세 단계를 거쳐요.">
        <ol className="relative grid grid-cols-3 gap-5">
          {/* 단계를 잇는 선 */}
          <div aria-hidden className="absolute top-6 right-[16.6%] left-[16.6%] h-px bg-line-mid" />
          {STEPS.map(({ no, icon: Icon, title, text }) => (
            <li key={no} className="relative flex flex-col items-center gap-5 px-4 text-center">
              <IconTile className="ring-8 ring-bg-page">
                <Icon size={22} />
              </IconTile>
              <div className="flex flex-col gap-2">
                <p className="text-meta-m text-brand-magenta">STEP {no}</p>
                <h3 className="text-h3 text-text-primary">{title}</h3>
                <p className="text-small text-text-secondary">{text}</p>
              </div>
            </li>
          ))}
        </ol>
      </InfoSection>

      <InfoSection title="무엇을 확인하나요" sub="광고에서 한 말을 네 가지로 나눠 따로 확인해요.">
        <div className="grid grid-cols-4 gap-5">
          {CHECKS.map(({ icon: Icon, title, quote, text }) => (
            <div
              key={title}
              className="flex flex-col gap-5 rounded-card border border-line-hair bg-bg-raised p-6 transition-shadow hover:shadow-popover"
            >
              <IconTile>
                <Icon size={22} />
              </IconTile>
              <div className="flex flex-col gap-2">
                <h3 className="text-h3 text-text-primary">{title}</h3>
                <p className="text-small-m text-text-tertiary">{quote}</p>
                <p className="text-small text-text-secondary">{text}</p>
              </div>
            </div>
          ))}
        </div>
      </InfoSection>

      <InfoSection
        title="결과는 6가지로 알려 드려요"
        sub="광고에서 한 말마다 아래 중 하나로 알려 드리고, 왜 그렇게 봤는지도 함께 보여 드려요."
      >
        <div className="grid grid-cols-3 gap-x-5 gap-y-4">
          {LABELS.map((label) => (
            <div key={label} className="flex items-center gap-4 rounded-card border border-line-hair px-5 py-4">
              <span aria-hidden className={`h-9 w-1 shrink-0 rounded-pill ${LABEL_STYLES[label].vivid}`} />
              <Tag tone={label} />
              <p className="text-small text-text-secondary">{LABEL_GUIDE[label].summary}</p>
            </div>
          ))}
        </div>
      </InfoSection>

      <InfoSection title="무엇과 비교하나요">
        <div className="flex items-start gap-6 rounded-card bg-bg-sunken p-8">
          <IconTile className="bg-bg-raised">
            <Database size={22} />
          </IconTile>
          <div className="flex flex-col gap-2">
            <h3 className="text-h3 text-text-primary">식약처(식품의약품안전처) 공개 정보</h3>
            <p className="text-body text-text-secondary">
              식약처에 신고된 건강기능식품 정보(원료, 함량, 먹는 방법, 소비기한, 주의사항)와 식약처가 인정한 효과를
              기준으로 비교해요. 결과는 공개 정보와 비교한 참고용이며, 법적인 판단은 아닙니다.
            </p>
          </div>
        </div>
      </InfoSection>
    </InfoLayout>
  )
}
