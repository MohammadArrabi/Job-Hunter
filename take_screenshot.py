import time
from pathlib import Path

from selenium import webdriver # controls the browser
from selenium.webdriver.chrome.options import Options # Chrome settings

URL = "https://nvidia.wd5.myworkdayjobs.com/NVIDIAExternalCareerSite?q=Junior&locationHierarchy1=2fcb99c455831013ea52bbe14cf9326c"
SCREENSHOTS_DIR = Path("screenshots")


def create_driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    return webdriver.Chrome(options=options)


def take_screenshot(url, output_file):
    driver = create_driver()
    try:
        print(f"Opening {url} ...")
        driver.get(url)
        time.sleep(5)

        height = driver.execute_script("return document.body.scrollHeight")
        driver.execute_cdp_cmd("Emulation.setDeviceMetricsOverride", {
            "width": 1920, "height": height, "deviceScaleFactor": 1, "mobile": False
        })
        time.sleep(1)

        driver.save_screenshot(str(output_file))
        print(f"Saved screenshot to {output_file} (page height: {height}px)")
    finally:
        driver.quit()


if __name__ == "__main__":
    SCREENSHOTS_DIR.mkdir(exist_ok=True)
    take_screenshot(URL, SCREENSHOTS_DIR / "nvidia.png")