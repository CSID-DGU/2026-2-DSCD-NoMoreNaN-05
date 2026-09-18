from playwright.sync_api import sync_playwright
import csv
import re
import time


# ============================================================
# 설정
# ============================================================

START_URL = (
    "https://ads.tiktok.com/business/creativecenter/"
    "inspiration/topads/pc/en"
)

TARGET_COUNT = 20

# 최종적으로 원하는 파일
SUCCESS_FILE = "tiktok_direct_video_urls.csv"

# 실패/제외 이유까지 확인하기 위한 로그
LOG_FILE = "tiktok_collect_log.csv"


# ============================================================
# 기본 함수
# ============================================================

def get_ad_id(url):
    match = re.search(r"/topads/(\d+)", url)
    return match.group(1) if match else ""


def is_detail_page(url):
    return re.search(r"/topads/\d+", url) is not None


def contains_korean(text):
    return re.search(r"[가-힣]", text) is not None


# ============================================================
# 1. 필터링된 Top Ads 목록에서 상세페이지 URL 수집
# ============================================================

def collect_ad_pages(page):

    collected = set()

    page.goto(
        START_URL,
        wait_until="domcontentloaded",
        timeout=60000
    )

    print("\n" + "=" * 70)
    print("TikTok Creative Center가 열렸습니다.")
    print("=" * 70)

    print("""
브라우저에서 직접 필터를 설정하세요.

Region      : South Korea
Industry    : Dietary Supplements
Ad Language : Korean
Ad Format   : Video

설정이 끝나면 PowerShell에서 Enter를 누르세요.
""")

    input(">>> 준비되면 Enter: ")

    previous_count = 0
    no_change_count = 0

    while len(collected) < TARGET_COUNT:

        links = page.locator('a[href*="/topads/"]')

        try:
            count = links.count()
        except:
            count = 0

        for i in range(count):

            try:

                href = links.nth(i).get_attribute("href")

                if not href:
                    continue

                if href.startswith("/"):
                    href = "https://ads.tiktok.com" + href

                href = href.split("?")[0]

                if is_detail_page(href):
                    collected.add(href)

            except:
                pass

        print(
            f"광고 상세페이지 수집: "
            f"{len(collected)} / {TARGET_COUNT}"
        )

        if len(collected) >= TARGET_COUNT:
            break

        if len(collected) == previous_count:
            no_change_count += 1
        else:
            no_change_count = 0

        previous_count = len(collected)

        if no_change_count >= 8:
            print("더 이상 새로운 광고가 로드되지 않습니다.")
            break

        page.evaluate(
            "window.scrollTo(0, document.body.scrollHeight)"
        )

        time.sleep(3)

    return list(collected)


# ============================================================
# 2. 실제 광고 영상 요청인지 검사
# ============================================================

def is_video_candidate(url, content_type):

    url_lower = url.lower()
    content_type = (content_type or "").lower()

    if "tiktokcdn.com" not in url_lower:
        return False

    # Creative Center 자체 홍보영상 제외
    if "seedance" in url_lower:
        return False

    if "creative-factory" in url_lower:
        return False

    # 우리가 직접 확인했던 실제 광고 영상 형태
    if "mime_type=video_mp4" in url_lower:
        return True

    if "video/mp4" in content_type:
        return True

    return False


def choose_video(video_urls):

    if not video_urls:
        return ""

    # 가장 원하는 형태 우선
    for url in video_urls:

        lower = url.lower()

        if (
            "v16m-default.tiktokcdn.com" in lower
            and "mime_type=video_mp4" in lower
        ):
            return url

    for url in video_urls:

        if "mime_type=video_mp4" in url.lower():
            return url

    return video_urls[0]


# ============================================================
# 3. 광고 상세페이지 검증 + video URL 추출
# ============================================================

def process_ad(browser, ad_page_url):

    # 광고 하나마다 context 새로 생성
    # → 하나가 죽어도 다음 광고에 영향 없음
    context = browser.new_context(
        viewport={
            "width": 1400,
            "height": 900
        }
    )

    page = context.new_page()

    video_urls = []

    def capture_response(response):

        try:

            url = response.url

            content_type = response.headers.get(
                "content-type",
                ""
            )

            if is_video_candidate(
                url,
                content_type
            ):

                if url not in video_urls:

                    video_urls.append(url)

                    print("    VIDEO 후보 발견")

        except:
            pass

    page.on("response", capture_response)

    try:

        page.goto(
            ad_page_url,
            wait_until="domcontentloaded",
            timeout=60000
        )

        time.sleep(4)

        # ----------------------------------------------------
        # 상세페이지 내용 읽기
        # ----------------------------------------------------

        body_text = page.locator("body").inner_text()

        body_normalized = re.sub(
            r"\s+",
            " ",
            body_text
        )

        # ----------------------------------------------------
        # South Korea 검증
        # ----------------------------------------------------

        is_korea = (
            "Region South Korea"
            in body_normalized
        )

        # ----------------------------------------------------
        # Dietary Supplements 검증
        # ----------------------------------------------------

        is_supplement = (
            "Industry Dietary Supplements"
            in body_normalized
        )

        # ----------------------------------------------------
        # 한국어가 있는지도 보조 확인
        # ----------------------------------------------------

        is_korean_text = contains_korean(
            body_text
        )

        print(
            f"    Korea={is_korea}, "
            f"Dietary Supplements={is_supplement}, "
            f"Korean={is_korean_text}"
        )

        # 조건 안 맞으면 저장하지 않음
        if not is_korea:

            return {
                "video_url": "",
                "status": "excluded_region",
                "error": "Region is not exactly South Korea"
            }

        if not is_supplement:

            return {
                "video_url": "",
                "status": "excluded_industry",
                "error": "Industry is not Dietary Supplements"
            }

        if not is_korean_text:

            return {
                "video_url": "",
                "status": "excluded_language",
                "error": "No Korean text found"
            }

        # ----------------------------------------------------
        # video 태그 재생
        # ----------------------------------------------------

        try:

            videos = page.locator("video")
            video_count = videos.count()

            for i in range(video_count):

                try:

                    videos.nth(i).evaluate(
                        """
                        (v) => {
                            v.muted = true;
                            v.currentTime = 0;
                            return v.play();
                        }
                        """
                    )

                except:
                    pass

        except:
            pass

        # ----------------------------------------------------
        # TikTok CDN 요청 기다리기
        # ----------------------------------------------------

        max_wait = 15
        start = time.time()

        while time.time() - start < max_wait:

            selected = choose_video(
                video_urls
            )

            if selected:
                return {
                    "video_url": selected,
                    "status": "success",
                    "error": ""
                }

            time.sleep(1)

        return {
            "video_url": "",
            "status": "video_not_found",
            "error": "Video request was not detected"
        }

    except Exception as e:

        return {
            "video_url": "",
            "status": "failed",
            "error": str(e)
        }

    finally:

        # 광고 하나 끝나면 해당 context만 폐기
        # 다음 광고에는 영향 없음
        try:
            context.close()
        except:
            pass


# ============================================================
# 4. CSV 저장
# ============================================================

def save_success(success_rows):

    with open(
        SUCCESS_FILE,
        "w",
        newline="",
        encoding="utf-8-sig"
    ) as f:

        writer = csv.DictWriter(
            f,
            fieldnames=[
                "ad_id",
                "video_url"
            ]
        )

        writer.writeheader()
        writer.writerows(success_rows)


def save_log(log_rows):

    with open(
        LOG_FILE,
        "w",
        newline="",
        encoding="utf-8-sig"
    ) as f:

        writer = csv.DictWriter(
            f,
            fieldnames=[
                "ad_id",
                "page_url",
                "video_url",
                "status",
                "error"
            ]
        )

        writer.writeheader()
        writer.writerows(log_rows)


# ============================================================
# 메인
# ============================================================

def main():

    success_rows = []
    log_rows = []

    with sync_playwright() as p:

        # ----------------------------------------------------
        # 목록 수집용 브라우저
        # ----------------------------------------------------

        browser = p.chromium.launch(
            headless=False
        )

        list_context = browser.new_context(
            viewport={
                "width": 1400,
                "height": 900
            }
        )

        list_page = list_context.new_page()

        # ----------------------------------------------------
        # 1단계: 필터된 광고 상세페이지 수집
        # ----------------------------------------------------

        ad_pages = collect_ad_pages(
            list_page
        )

        print()
        print("=" * 70)
        print(
            f"상세페이지 {len(ad_pages)}개 수집 완료"
        )
        print("=" * 70)

        # 목록 context는 이제 필요 없음
        list_context.close()

        # ----------------------------------------------------
        # 2단계: 각각 검증 + 실제 video URL 추출
        # ----------------------------------------------------

        total = len(ad_pages)

        for index, ad_page_url in enumerate(
            ad_pages,
            start=1
        ):

            ad_id = get_ad_id(
                ad_page_url
            )

            print()
            print("-" * 70)
            print(
                f"[{index}/{total}] "
                f"Ad ID: {ad_id}"
            )

            # 혹시 브라우저 자체가 죽었다면 재실행
            if not browser.is_connected():

                print(
                    "브라우저가 종료되어 재실행합니다."
                )

                browser = p.chromium.launch(
                    headless=False
                )

            result = process_ad(
                browser,
                ad_page_url
            )

            video_url = result[
                "video_url"
            ]

            status = result[
                "status"
            ]

            error = result[
                "error"
            ]

            if status == "success":

                print()
                print(
                    "✅ 실제 동영상 URL:"
                )

                print(
                    video_url
                )

                success_rows.append({
                    "ad_id":
                        ad_id,

                    "video_url":
                        video_url
                })

            else:

                print(
                    f"❌ 제외/실패: "
                    f"{status}"
                )

                if error:
                    print(error)

            log_rows.append({
                "ad_id":
                    ad_id,

                "page_url":
                    ad_page_url,

                "video_url":
                    video_url,

                "status":
                    status,

                "error":
                    error
            })

            # 한 건 처리할 때마다 저장
            save_success(
                success_rows
            )

            save_log(
                log_rows
            )

            time.sleep(2)

        browser.close()

    print()
    print("=" * 70)
    print("완료")
    print("=" * 70)

    print(
        f"실제 영상 URL: "
        f"{len(success_rows)}개"
    )

    print(
        f"성공 파일: {SUCCESS_FILE}"
    )

    print(
        f"전체 로그: {LOG_FILE}"
    )


if __name__ == "__main__":
    main()