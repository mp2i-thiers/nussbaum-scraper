import re
import shutil
import tempfile
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin

import fitz
import requests

BASE_URL = "https://nussbaumcpge.be/classe/MP2I/"


class TableParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.current_name = ""
        self.current_table = []
        self.in_table = False
        self.in_th = False
        self.tables = []

    def handle_starttag(self, tag, attrs):
        if tag == "table":
            self.in_table = True
            self.current_table = []
        elif tag == "th":
            self.in_th = True
        elif tag == "a" and self.in_table:
            if (href := dict(attrs).get("href", "")).endswith((".pdf", ".zip")):
                self.current_table.append(href)

    def handle_data(self, data):
        if self.in_th and (name := data.strip()):
            self.current_name = name.replace("/", "-")

    def handle_endtag(self, tag):
        if tag == "table" and self.in_table:
            self.tables.append((self.current_name, self.current_table))
            self.in_table = False
        elif tag == "th":
            self.in_th = False


def clean_pdf(input_path: str, output_path: str) -> None:
    doc = fitz.open(input_path)
    if len(doc) < 8:
        shutil.copy2(input_path, output_path)
        return

    labels = [p.get_label() or str(i) for i, p in enumerate(doc)]

    doc.select([i for i in range(len(labels)) if i == len(labels) - 1 or labels[i] != labels[i + 1]])
    doc.save(output_path, garbage=4)


def scrape_files(base_url: str, output_dir: str = "nussbaum") -> list:
    resp = requests.get(base_url)
    resp.raise_for_status()

    if not (pages := re.findall(r'href="([^"]*\?classe=MP2I)"', resp.text)):
        raise RuntimeError("No nav links found, the site's structure has probably changed")

    downloaded = []

    for page in pages:
        page_resp = requests.get(urljoin(base_url, page))
        page_resp.raise_for_status()

        page_name = page.split("/")[-2]

        parser = TableParser()
        parser.feed(page_resp.text)

        for table_name, links in parser.tables:
            table_dir = Path(output_dir) / page_name / table_name
            table_dir.mkdir(parents=True, exist_ok=True)

            for link in links:
                file_path = table_dir / Path(link).name
                if download_and_clean(urljoin(base_url, link), file_path):
                    downloaded.append(str(file_path))

    return downloaded


def download_and_clean(url: str, file_path: Path) -> bool:
    try:
        resp = requests.get(url, stream=True)
        resp.raise_for_status()

        with tempfile.NamedTemporaryFile("wb", delete_on_close=False) as temp:
            # Using chunks to save some RAM in case of large files.
            # (And 2048 is a nice number)
            for chunk in resp.iter_content(2048):
                temp.write(chunk)
            temp.close()
            if url.endswith(".zip"):
                shutil.copy(temp.name, file_path)
            else:
                clean_pdf(temp.name, file_path.as_posix())

        print(f"Downloaded and cleaned {file_path}")
        return True

    except requests.exceptions.HTTPError as e:
        print(f"Failed to fetch {file_path}: {e.response.status_code}")
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
    return False


if __name__ == "__main__":
    scrape_files(BASE_URL)
