/**
 * 영상 주소 1차 검사 (명세 I01 "URL 검사" 표). 서버도 같은 규칙으로 URL_001을 돌려줘요.
 * http/https이고, 호스트 앞의 www.·m.은 떼고 비교해요.
 *
 * YouTube   youtube.com/watch?v=<id> · youtube.com/shorts/<id> · youtu.be/<id>
 * Instagram instagram.com/reel/<id> · instagram.com/reels/<id> · instagram.com/p/<id>
 * TikTok    tiktok.com/@<user>/video/<id> · vm.tiktok.com/<id> · vt.tiktok.com/<id>
 */
export const URL_FORMAT_ERROR = '영상 주소가 아니에요. YouTube · Instagram · TikTok 영상 주소를 넣어 주세요.'

export function isSupportedVideoUrl(raw: string): boolean {
  let url: URL
  try {
    url = new URL(raw.trim())
  } catch {
    return false
  }
  if (url.protocol !== 'http:' && url.protocol !== 'https:') return false

  const host = url.hostname.toLowerCase().replace(/^(www\.|m\.)/, '')
  const parts = url.pathname.split('/').filter(Boolean)

  switch (host) {
    case 'youtube.com':
      if (parts[0] === 'watch') return Boolean(url.searchParams.get('v'))
      return parts[0] === 'shorts' && Boolean(parts[1])
    case 'youtu.be':
      return Boolean(parts[0])
    case 'instagram.com':
      return ['reel', 'reels', 'p'].includes(parts[0] ?? '') && Boolean(parts[1])
    case 'tiktok.com':
      return (parts[0] ?? '').startsWith('@') && parts[0].length > 1 && parts[1] === 'video' && Boolean(parts[2])
    case 'vm.tiktok.com':
    case 'vt.tiktok.com':
      return Boolean(parts[0])
    default:
      return false
  }
}
