from steps.common import *
from utils.bdd_decorator import bdd_case

@pytest.mark.key_pc
@bdd_case("key","key_pc_main_page.feature", "key_pc_main_page")
def test_pc_main_page():pass


def _wait_for_page_stable(page, interval: float = 1, stable_threshold: float = 0.0001, timeout: float = 30.0):
    """Poll screenshots until the pixel diff between two consecutive frames drops below the threshold, indicating the page has stabilized."""
    from PIL import Image, ImageChops
    import io

    deadline = time.time() + timeout
    prev_img = None
    while time.time() < deadline:
        raw = page.screenshot(type="png")
        curr_img = Image.open(io.BytesIO(raw)).convert("RGB")
        if prev_img is not None:
            diff = ImageChops.difference(prev_img, curr_img)
            diff_pixels = sum(1 for px in diff.getdata() if any(c > 10 for c in px))
            total_pixels = curr_img.width * curr_img.height
            if diff_pixels / total_pixels < stable_threshold:
                return
        prev_img = curr_img
        time.sleep(interval)


@when("login the main page")
def login_the_main_page(page):
    page.goto(os.getenv("main_url"))
    view = page.locator("flutter-view")
    view.wait_for(state="visible")
    time.sleep(1)
    _wait_for_page_stable(page)


@then("check main elements")
def check_main_elements_visible(page):
    screenshot = page.screenshot(type="png", full_page=True)
    diff_rate = compare_screenshot(baseline_name="key_pc_login_main.png", screenshot=screenshot, threshold=0.05)
    assert diff_rate <= 0.05, f"Visual diff rate {diff_rate:.2%} exceeds the 5% threshold. Please check the screenshot comparison!"
