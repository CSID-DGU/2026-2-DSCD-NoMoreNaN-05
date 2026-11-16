import { type FormEvent, useId, useState } from 'react'
import errorIcon from '@/assets/icons/error.svg'
import linkIcon from '@/assets/icons/link.svg'
import { Button } from '@/components/ui/Button'
import { URL_FORMAT_ERROR, isSupportedVideoUrl } from '@/features/input/videoUrl'
import { cn } from '@/lib/cn'

type UrlFormProps = {
  /** 처음 칸에 넣어 둘 주소 (만료된 주소로 돌아왔을 때 등) */
  defaultUrl?: string
  /** 서버가 돌려준 오류 문장 — 입력란 아래에 보여요 */
  serverError?: string | null
  pending: boolean
  onSubmit: (url: string) => void
  /** 입력을 고치기 시작하면 서버 오류를 지워요 */
  onEdit: () => void
}

/**
 * Figma S1 입력란 + [검증하기].
 * 오류는 팝업이 아니라 입력란 아래 빨간 글자로 보여요(명세 I02). 오류일 때는 위에 "광고 영상 주소" 이름이 보여요.
 */
export function UrlForm({ defaultUrl = '', serverError, pending, onSubmit, onEdit }: UrlFormProps) {
  const [url, setUrl] = useState(defaultUrl)
  const [formatError, setFormatError] = useState(false)
  const inputId = useId()
  const messageId = useId()
  const error = formatError ? URL_FORMAT_ERROR : (serverError ?? null)

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault()
    if (pending) return
    const value = url.trim()
    if (!isSupportedVideoUrl(value)) {
      setFormatError(true)
      return
    }
    onSubmit(value)
  }

  return (
    <form noValidate onSubmit={handleSubmit} className={cn('flex w-full flex-col gap-2', error ? 'pt-8.75' : 'pt-8')}>
      <label htmlFor={inputId} className={error ? 'text-small-m text-text-primary' : 'sr-only'}>
        광고 영상 주소
      </label>
      <div className="flex w-full gap-2">
        <div
          className={cn(
            'flex h-13 min-w-0 flex-1 items-center gap-2.5 rounded-control bg-bg-raised px-4',
            error
              ? 'border-[1.5px] border-label-violation-vivid'
              : 'border border-line-mid focus-within:border-text-secondary',
          )}
        >
          <img src={linkIcon} alt="" width={18} height={18} />
          <input
            id={inputId}
            type="url"
            inputMode="url"
            autoComplete="off"
            spellCheck={false}
            value={url}
            onChange={(e) => {
              setUrl(e.target.value)
              setFormatError(false)
              onEdit()
            }}
            placeholder="https://www.youtube.com/shorts/…"
            aria-invalid={Boolean(error)}
            aria-describedby={messageId}
            className="min-w-0 flex-1 bg-transparent text-body text-text-primary outline-none placeholder:text-text-secondary"
          />
        </div>
        <Button type="submit" disabled={pending} className="self-stretch">
          검증하기
        </Button>
      </div>
      {error ? (
        <p id={messageId} role="alert" className="flex items-center gap-1.5 text-meta-m text-label-violation">
          <img src={errorIcon} alt="" width={14} height={14} />
          {error}
        </p>
      ) : (
        <p id={messageId} className="text-meta text-text-secondary">
          YouTube · Instagram · TikTok 영상 주소를 넣을 수 있어요
        </p>
      )}
    </form>
  )
}
