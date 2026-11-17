/**
 * S1 첫 화면 뒤 궤도 그림 — Figma 'S1-01 · 깔끔 C1 궤도'를 TRUEAD에 맞게 다시 그렸어요.
 * - 궤도 3개가 제목 위쪽 배경에 걸려요. 아래로 내려오는 부분은 흐려져서 제목·입력창을 가리지 않아요.
 * - 흰 점들이 궤도를 따라 아주 천천히 돌아요: 광고 속 주장을 하나씩 살펴본다는 뜻이에요.
 * - 움직임 줄이기 설정이면 점이 멈춰 있어요.
 * 좌표는 가로 1920 · 세로 1010(메뉴~바닥글 사이) 기준이고, 화면 크기가 달라도 가운데를 맞춰 잘라 채워요(slice).
 */
const W = 1920
const H = 1010
/** 궤도 중심 — 제목(세로 약 430)보다 위 */
const CX = W / 2
const CY = 300

type Orbit = { rx: number; ry: number; tilt: number; opacity: number }
const ORBITS: Orbit[] = [
  { rx: 1060, ry: 250, tilt: -6, opacity: 0.9 }, // 바깥 — 화면 밖까지
  { rx: 780, ry: 175, tilt: 5, opacity: 0.8 },
  { rx: 480, ry: 100, tilt: -3, opacity: 0.65 }, // 안쪽 — 제목 바로 위
]

/** 궤도를 한 바퀴 도는 길 (점이 따라 움직여요). 시작점은 궤도의 오른쪽 끝 */
const orbitPath = ({ rx, ry }: Orbit) =>
  `M ${CX + rx} ${CY} A ${rx} ${ry} 0 1 1 ${CX - rx} ${CY} A ${rx} ${ry} 0 1 1 ${CX + rx} ${CY}`

type Dot = { orbit: number; r: number; glow?: boolean; seconds: number; start: number }
/** start: 한 바퀴 중 어디서 시작할지(0~1). 처음 보일 때 모두 위쪽 반에 있도록 골랐어요 */
const DOTS: Dot[] = [
  { orbit: 0, r: 8, glow: true, seconds: 140, start: 0.62 },
  { orbit: 2, r: 4, seconds: 70, start: 0.7 },
  { orbit: 1, r: 3.5, seconds: 100, start: 0.55 },
]

const prefersReducedMotion = () =>
  typeof window !== 'undefined' && window.matchMedia?.('(prefers-reduced-motion: reduce)').matches

export function OrbitBackdrop() {
  const still = prefersReducedMotion()
  return (
    <svg
      aria-hidden
      className="pointer-events-none absolute inset-0 h-full w-full"
      viewBox={`0 0 ${W} ${H}`}
      preserveAspectRatio="xMidYMid slice"
      fill="none"
    >
      <defs>
        {/* 위는 또렷하게, 제목 아래로 갈수록 사라지게 */}
        <linearGradient id="orbit-fade" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="0" y2={H}>
          <stop offset="0" stopColor="white" stopOpacity="1" />
          <stop offset="0.36" stopColor="white" stopOpacity="1" />
          <stop offset="0.56" stopColor="white" stopOpacity="0" />
        </linearGradient>
        <mask id="orbit-mask" maskUnits="userSpaceOnUse" x="0" y="0" width={W} height={H}>
          <rect width={W} height={H} fill="url(#orbit-fade)" />
        </mask>
        <radialGradient id="orbit-glow">
          <stop offset="0%" stopColor="var(--color-white)" stopOpacity="0.95" />
          <stop offset="100%" stopColor="var(--color-white)" stopOpacity="0" />
        </radialGradient>
      </defs>

      <g mask="url(#orbit-mask)">
        {ORBITS.map((o, i) => (
          <g key={i} transform={`rotate(${o.tilt} ${CX} ${CY})`}>
            <path d={orbitPath(o)} stroke="var(--color-white)" strokeWidth="1.5" opacity={o.opacity} />
            {DOTS.filter((d) => d.orbit === i).map((d, j) => (
              <g key={j}>
                {d.glow && <circle r={d.r * 2.8} fill="url(#orbit-glow)" />}
                <circle r={d.r} fill="var(--color-white)" />
                {/* 점 묶음을 궤도 위로 옮겨요. 멈춤 설정이면 시작 위치에 고정 */}
                <animateMotion
                  path={orbitPath(o)}
                  dur={`${d.seconds}s`}
                  begin={`-${d.start * d.seconds}s`}
                  repeatCount={still ? '1' : 'indefinite'}
                  {...(still ? { keyPoints: `${d.start};${d.start}`, keyTimes: '0;1', calcMode: 'linear' } : {})}
                  fill="freeze"
                />
              </g>
            ))}
          </g>
        ))}
      </g>
    </svg>
  )
}
