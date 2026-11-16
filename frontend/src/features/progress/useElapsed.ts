import { useEffect, useState } from 'react'

/**
 * 경과 시간을 1초마다 올려 보여요. 폴링은 2초마다라, 서버 값(elapsedSec)을 받은 시각부터 흐른 만큼 더해요.
 * running이 false면(완료·실패) 서버 값 그대로예요.
 */
export function useElapsed(elapsedSec: number | undefined, receivedAt: number, running: boolean) {
  const [now, setNow] = useState(() => Date.now())

  useEffect(() => {
    if (!running) return
    const id = window.setInterval(() => setNow(Date.now()), 1000)
    return () => window.clearInterval(id)
  }, [running])

  if (elapsedSec === undefined) return 0
  return running ? elapsedSec + Math.max(0, now - receivedAt) / 1000 : elapsedSec
}
