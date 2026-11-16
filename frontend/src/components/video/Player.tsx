import { useState } from 'react'
import { cn } from '@/lib/cn'

type PlayerProps = {
  /** md: 544×306 (S3 결과) / lg: 608×342 (S2 처리 중) — 둘 다 16:9 */
  size?: 'md' | 'lg'
  /** 영상 주소(/api/jobs/{id}/video). 없으면 검은 화면에 message만 보여요(영상을 아직 못 받았을 때). */
  src?: string
  message?: string
  className?: string
}

/**
 * Figma v5/Player — 16:9 검은 틀. 숏폼(세로) 영상은 좌우가 검게 남아요(개발 노트 §4).
 * 영상을 불러오지 못하면 안내 글자로 바꿔요.
 *
 * TODO: Figma의 재생 막대(일시정지·시간·마젠타 진행 막대)는 아직 브라우저 기본 컨트롤로 대신해요.
 */
export function Player({ size = 'md', src, message, className }: PlayerProps) {
  const [failedSrc, setFailedSrc] = useState<string | null>(null)
  const showVideo = src && failedSrc !== src
  const text = src && failedSrc === src ? '영상을 불러오지 못했어요' : message

  return (
    <div
      className={cn(
        'relative flex aspect-video shrink-0 items-center justify-center overflow-hidden rounded-popover bg-bg-player',
        size === 'md' ? 'w-136' : 'w-152',
        className,
      )}
    >
      {showVideo ? (
        <video
          key={src}
          src={src}
          controls
          playsInline
          preload="metadata"
          onError={() => setFailedSrc(src)}
          className="size-full object-contain"
        />
      ) : (
        text && <p className="text-small text-text-on-dark">{text}</p>
      )}
    </div>
  )
}
