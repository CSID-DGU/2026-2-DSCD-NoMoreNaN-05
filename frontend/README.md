# TRUEAD 프론트엔드

SNS 건강기능식품 광고 영상의 주장을 식약처 공개 데이터와 대조해 보여 주는 웹 화면이에요.
디자인 기준은 Figma `TRUEAD_AI-아키텍처` → 페이지 `Wed Design Fianl` → 섹션 **v5 final**
(주장 결과 카드는 섹션 `v5` 아래쪽의 컴포넌트·케이스 카탈로그 참고).

## 실행

```bash
cd frontend
npm install
npm run dev      # http://localhost:5173  (컴포넌트 미리보기: /#gallery, 한 섹션만: /?only=cards#gallery)
npm run build    # 타입 검사 + 배포용 빌드
npm run lint
```

`/api` 요청은 개발 서버가 백엔드로 넘겨줘요. 백엔드 주소는 `.env.example`을 `.env.local`로 복사해서 적어요.

## 폴더 구조

```
src/
├─ main.tsx              앱 시작점
├─ App.tsx               화면 전환 (지금은 #gallery만)
├─ index.css             Tailwind + 디자인 토큰 불러오기
├─ styles/               디자인 토큰 (Figma 변수 → Tailwind @theme)
│  ├─ fonts.css            Noto Sans KR
│  ├─ colors.css           글자·배경·선·브랜드 색
│  ├─ labels.css           라벨 6종 색
│  ├─ typography.css       글자 스타일 (text-h2, text-body …)
│  └─ geometry.css         모서리·그림자·배치
├─ assets/icons/         Figma에서 받은 SVG 아이콘 (원본 그대로)
├─ lib/                  화면과 무관한 공용 코드 (라벨 정의, 나중에 API 호출)
├─ components/
│  ├─ ui/                어디서나 쓰는 기본 부품. 화면 의미를 모름
│  │                       Button, Tag, Chip, Mark, Toggle, Tab, Switch, Checkbox
│  ├─ layout/            페이지 뼈대: Nav
│  └─ video/             영상 자리: Player (S2·S3 공용)
├─ features/             화면(단계)별 부품. 그 화면에서만 써요
│  ├─ progress/            S2 처리 중: Stage, FailDialog
│  └─ result/              S3 결과: ClaimCard, GroupCard, ProductRow …
├─ pages/                화면 단위 조립 (S1 입력, S2 처리, S3 결과) — 6단계에서 추가
└─ dev/                  개발용 미리보기 (#gallery). 배포 빌드에는 안 들어가요
```

### 규칙

- **어디에 둘지:** 두 화면 이상에서 쓰면 `components/`, 한 화면에서만 쓰면 `features/<화면>/`.
- **의존 방향:** `pages` → `features` → `components` → `lib`·`styles`. 반대 방향으로는 불러오지 않아요.
- **파일:** 컴포넌트 하나에 파일 하나(`Button.tsx`), 파일 이름 = 컴포넌트 이름. `index.ts`로 묶지 않고 직접 불러와요.
- **불러오기:** `@/`로 시작 (`import { Tag } from '@/components/ui/Tag'`).
- **스타일:** Tailwind 클래스 + 디자인 토큰만 써요. `#c8102e` 같은 색 값을 컴포넌트에 직접 쓰지 않아요.
  토큰 이름은 Figma 변수와 같아요: `text-text-primary`, `bg-label-violation-tint`.
- **라벨:** 위반·과장 등 라벨 이름과 색은 `lib/labels.ts` 한 곳에서만 정해요.
