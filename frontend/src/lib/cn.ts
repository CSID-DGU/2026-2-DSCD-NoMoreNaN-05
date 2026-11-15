/** 조건부 클래스 이름 합치기. false·null·undefined·빈 문자열은 빠져요.
 *  예: cn('px-4', isOpen && 'bg-bg-sunken', className) */
export function cn(...classes: Array<string | false | null | undefined>): string {
  return classes.filter(Boolean).join(' ')
}
