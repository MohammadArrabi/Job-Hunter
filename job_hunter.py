from take_screenshot import take_screenshot, SCREENSHOTS_DIR
from compare import compare_screenshots
from notifier import send_message, send_photo
from ai_vision import read_jobs
from companies import COMPANIES

SENIOR_WORDS = ["senior", "sr.", "staff", "principal", "lead", "manager", "director", "architect", "head of"]


def is_junior_friendly(title):
    title = title.lower()
    return not any(word in title for word in SENIOR_WORDS)


def run_check(company, url):
    new_file = SCREENSHOTS_DIR / f"{company}_new.png"
    current_file = SCREENSHOTS_DIR / f"{company}_current.png"
    previous_file = SCREENSHOTS_DIR / f"{company}_previous.png"
    diff_file = SCREENSHOTS_DIR / f"{company}_diff.png"

    try:
        take_screenshot(url, new_file)
    except Exception as e:
        print(f"[{company}] Screenshot failed, keeping the old files: {e}")
        return "error"

    if current_file.exists():
        current_file.replace(previous_file)
    new_file.replace(current_file)

    if not previous_file.exists():
        print(f"[{company}] First run: baseline saved")
        return "baseline"

    diff_file.unlink(missing_ok=True)
    result = compare_screenshots(previous_file, current_file, diff_file)

    if not result["changed"]:
        print(f"[{company}] No change ({result['change_percentage']}% of pixels changed)")
        return "unchanged"

    print(f"[{company}] Pixels changed ({result['change_percentage']}%), asking the AI to read the jobs...")
    jobs = read_jobs(company, previous_file, current_file)

    if jobs is None:
        notify(company, url, diff_file, f"⚠️ {company.upper()} page changed, but the AI check failed. Please check manually.")
        return "changed (no AI)"

    print(f"[{company}] AI read {len(jobs.jobs_before)} jobs before, {len(jobs.jobs_after)} jobs after")
    new_jobs = [title for title in jobs.jobs_after if title not in jobs.jobs_before]
    junior_jobs = [title for title in new_jobs if is_junior_friendly(title)]

    for title in new_jobs:
        print(f"  new: {title}{'' if title in junior_jobs else '  (skipped: senior)'}")

    if not junior_jobs:
        print(f"[{company}] No new junior jobs (no message sent)")
        return "no new junior jobs"

    job_lines = "\n".join(f"• {title}" for title in junior_jobs[:10])
    notify(company, url, diff_file, f"🔔 New junior jobs at {company.upper()}!\n{job_lines}")
    return "new jobs"


def notify(company, url, diff_file, text):
    message = f"{text}\n{url}"
    if diff_file.exists():
        send_photo(diff_file, caption=message)
    else:
        send_message(message)


def main():
    SCREENSHOTS_DIR.mkdir(exist_ok=True)
    statuses = {}

    for company in COMPANIES:
        name = company["name"]
        try:
            statuses[name] = run_check(name, company["url"])
        except Exception as e:
            print(f"[{name}] Unexpected error: {e}")
            statuses[name] = "error"

    print("\nSummary:")
    for name, status in statuses.items():
        print(f"  {name:<10} {status}")


if __name__ == "__main__":
    main()