import csv
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://openaccess.thecvf.com"
PAGE_URL = f"{BASE_URL}/CVPR2024?day=all"

def scrape_cvpr2024():
    print("Fetching CVPR 2024 open access page...")
    resp = requests.get(PAGE_URL, timeout=60)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    dts = soup.find_all("dt", class_="ptitle")
    print(f"Found {len(dts)} papers. Extracting data...")

    papers = []
    for dt in dts:
        title_tag = dt.find("a")
        title = title_tag.get_text(strip=True) if title_tag else ""
        paper_page = title_tag["href"] if title_tag and title_tag.has_attr("href") else ""
        if paper_page and not paper_page.startswith("http"):
            paper_page = BASE_URL + paper_page

        dd_authors = dt.find_next_sibling("dd")
        authors = []
        if dd_authors:
            for inp in dd_authors.find_all("input", {"name": "query_author"}):
                authors.append(inp["value"])

        dd_links = dd_authors.find_next_sibling("dd") if dd_authors else None
        pdf_link = supp_link = arxiv_link = ""
        if dd_links:
            for a in dd_links.find_all("a"):
                text = a.get_text(strip=True).lower()
                href = a.get("href", "")
                if text == "pdf":
                    pdf_link = href if href.startswith("http") else BASE_URL + href
                elif text == "supp":
                    supp_link = href if href.startswith("http") else BASE_URL + href
                elif text == "arxiv":
                    arxiv_link = href

        papers.append({
            "title": title,
            "authors": "; ".join(authors),
            "paper_page": paper_page,
            "pdf_link": pdf_link,
            "supplementary_link": supp_link,
            "arxiv_link": arxiv_link,
        })

    return papers


def save_csv(papers, filename="cvpr2024_papers.csv"):
    fieldnames = ["title", "authors", "paper_page", "pdf_link", "supplementary_link", "arxiv_link"]
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(papers)
    print(f"Saved {len(papers)} papers to {filename}")


if __name__ == "__main__":
    papers = scrape_cvpr2024()
    save_csv(papers)
