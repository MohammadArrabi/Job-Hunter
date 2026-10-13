from take_screenshot import take_screenshot, URL, SCREENSHOTS_DIR
from compare import compare_screenshots

COMPANY = "nvidia"


def run_check(company, url):
    new_file = SCREENSHOTS_DIR / f"{company}_new.png"
    current_file = SCREENSHOTS_DIR / f"{company}_current.png"
    previous_file = SCREENSHOTS_DIR / f"{company}_previous.png"
    diff_file = SCREENSHOTS_DIR / f"{company}_diff.png"

    try:
        take_screenshot(url, new_file)
    except Exception as e:
        print(f"Screenshot failed, keeping the old files: {e}")
        return

    if current_file.exists():
        current_file.replace(previous_file)
    new_file.replace(current_file)

    if not previous_file.exists():
        print("First run: baseline saved. Run again to get a 'before' screenshot.")
        return

    diff_file.unlink(missing_ok=True)
    result = compare_screenshots(previous_file, current_file, diff_file)

    if result["changed"]:
        print(f"CHANGE DETECTED: {result['change_percentage']}% of pixels changed")
        print(f"  Page size changed: {result['size_changed']}")
        print(f"  Changed area (left, top, right, bottom): {result['changed_area']}")
        print(f"  See {diff_file} for the changes marked in red")
    else:
        print(f"No change ({result['change_percentage']}% of pixels changed)")


if __name__ == "__main__":
    SCREENSHOTS_DIR.mkdir(exist_ok=True)
    run_check(COMPANY, URL)