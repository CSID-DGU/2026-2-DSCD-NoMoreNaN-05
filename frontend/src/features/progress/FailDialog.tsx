import { type ReactNode, useEffect, useRef } from 'react'
import close from '@/assets/icons/close.svg'
import { Button } from '@/components/ui/Button'

type FailDialogProps = {
  open: boolean
  title: string
  /** 본문. 줄바꿈이 필요하면 <br />이나 <p>를 넣어요. */
  children: ReactNode
  /** X 버튼·Esc → 팝업만 닫힘 ("팝업 닫은 뒤" 화면) */
  onClose: () => void
  /** [처음으로 돌아가기] → S1 */
  onGoHome: () => void
}

/**
 * Figma v5/FailDialog — S2에서 단계가 실패하면 뜨는 팝업 (개발 노트 §3).
 * 브라우저 기본 <dialog>를 써서 뒤 화면 막기·초점 가두기·Esc 닫기가 기본으로 돼요.
 * 뒤 배경: text-primary 42% (Figma Scrim).
 */
export function FailDialog({ open, title, children, onClose, onGoHome }: FailDialogProps) {
  const ref = useRef<HTMLDialogElement>(null)

  useEffect(() => {
    const dialog = ref.current
    if (!dialog) return
    if (open && !dialog.open) {
      dialog.showModal()
      // 기본으로는 첫 버튼(X)에 초점 테두리가 생겨요. 팝업 자체에 초점을 두고, Tab으로 버튼에 가게 해요.
      dialog.focus()
    }
    if (!open && dialog.open) dialog.close()
  }, [open])

  return (
    <dialog
      ref={ref}
      tabIndex={-1}
      aria-labelledby="fail-dialog-title"
      onCancel={(e) => {
        // Esc: 브라우저가 직접 닫지 않게 막고, 상태(open)를 바꿔서 닫아요.
        e.preventDefault()
        onClose()
      }}
      className="m-auto w-130 rounded-dialog outline-none bg-bg-raised px-8 pt-7 pb-6 shadow-dialog backdrop:bg-text-primary/42"
    >
      <div className="flex items-start justify-between gap-4">
        <h2 id="fail-dialog-title" className="text-h2 text-text-primary">
          {title}
        </h2>
        <button type="button" aria-label="닫기" onClick={onClose} className="shrink-0 cursor-pointer">
          <img src={close} alt="" width={20} height={20} />
        </button>
      </div>
      <div className="pt-3 text-body text-text-secondary">{children}</div>
      <div className="flex justify-end pt-6 pb-5">
        <Button onClick={onGoHome}>처음으로 돌아가기</Button>
      </div>
    </dialog>
  )
}
