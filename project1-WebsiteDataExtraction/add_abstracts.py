import csv
import time
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed

INPUT_CSV = "cvpr2024_papers.csv"
OUTPUT_CSV = "cvpr2024_papers_with_abstracts.csv"
MAX_WORKERS = 20
TIMEOUT = 30

session = requests.Session()
session.headers.update({"User-Agent": "Mozilla/5.0 (research scraper)"})


def fetch_abstract(row):
    url = row.get("paper_page", "")
    if not url:
        return row, ""
    try:
        resp = session.get(url, timeout=TIMEOUT)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        div = soup.find("div", id="abstract")
        abstract = div.get_text(strip=True) if div else ""
        return row, abstract
    except Exception as e:
        return row, f"ERROR: {e}"


def main():
    with open(INPUT_CSV, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        papers = list(reader)

    total = len(papers)
    print(f"Loaded {total} papers from {INPUT_CSV}")
    print(f"Fetching abstracts with {MAX_WORKERS} concurrent workers...")

    results = [None] * total
    done_count = 0
    start = time.time()

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        future_to_idx = {
            pool.submit(fetch_abstract, papers[i]): i for i in range(total)
        }
        for future in as_completed(future_to_idx):
            idx = future_to_idx[future]
            row, abstract = future.result()
            row["abstract"] = abstract
            results[idx] = row
            done_count += 1
            if done_count % 100 == 0 or done_count == total:
                elapsed = time.time() - start
                rate = done_count / elapsed
                eta = (total - done_count) / rate if rate > 0 else 0
                print(f"  [{done_count}/{total}] {rate:.1f} papers/sec, ETA {eta:.0f}s")

    fieldnames = list(papers[0].keys()) + ["abstract"]
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    errors = sum(1 for r in results if r["abstract"].startswith("ERROR"))
    print(f"\nDone. Saved to {OUTPUT_CSV}")
    print(f"  Successful: {total - errors}, Errors: {errors}")


if __name__ == "__main__":
    main()
