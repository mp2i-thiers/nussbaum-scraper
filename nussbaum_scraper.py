import os
from html.parser import HTMLParser
import requests
from pdf_cleaner.pdf_cleaner import clean_pdf
import tempfile

BASE_URL = "https://nussbaumcpge.be/public_html/Sup/MP2I/"


class NussbaumScraper(HTMLParser):
    base_url: str
    in_menu = False

    def __init__(self, base_url):
        super().__init__()
        self.base_url = base_url

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)

        if tag == "ul" and attrs_dict.get("id") == "onglets":
            self.in_menu = True
        elif tag == "a" and self.in_menu and attrs_dict.get("href") != "index.php":
            tab_parser = self._TabParser(self.base_url, attrs_dict["href"])
            tab_parser.parse()

    def handle_endtag(self, tag):
        if tag == "ul" and self.in_menu:
            self.in_menu = False

    def parse(self):
        data = _make_request(self.base_url + "index.php")
        self.feed(data)

    class _TabParser(HTMLParser):
        base_url: str
        tab_name: str

        in_lessons_list = False

        def __init__(self, base_url, tab_name):
            super().__init__()
            self.base_url = base_url
            self.tab_name = tab_name

        def handle_starttag(self, tag, attrs):
            attrs_dict = dict(attrs)

            if tag == "div" and attrs_dict.get("class") == "column1":
                self.in_lessons_list = True
            elif tag == "a" and self.in_lessons_list and attrs_dict["href"].endswith(".pdf"):
                _download_and_clean_pdf(
                    self.base_url + attrs_dict["href"],
                    self.tab_name.removesuffix(".php"),
                    attrs_dict["href"]
                )

        def handle_endtag(self, tag):
            if tag == "div" and self.in_lessons_list:
                self.in_lessons_list = False

        def parse(self):
            data = _make_request(self.base_url + self.tab_name)

            print(f"Parsing '{self.tab_name}'")

            self.feed(data)


def _make_request(url: str) -> str:
    r = requests.get(url)
    if r.status_code != 200:
        raise requests.RequestException()

    return r.text


def _download_and_clean_pdf(url: str, directory: str, file_name: str):
    print(f"Starting to download {directory}/{file_name}")

    abs_dir = os.path.join(os.getcwd(), f"nussbaum/{directory}")
    if not os.path.exists(abs_dir):
        os.makedirs(abs_dir)

    r = requests.get(url, stream=True)

    file_path = os.path.join(abs_dir, file_name)

    with tempfile.NamedTemporaryFile("wb", delete=False) as temp:
        # Using chunks to save some RAM in case of large files.
        # (And 2048 is a nice number)
        for chunk in r.iter_content(2048):
            temp.write(chunk)
        temp.close()

        print(f"Cleaning {directory}/{file_name}")
        try:
            clean_pdf(temp.name, file_path)
        except RuntimeError as err:
            print(f"Error ({directory}/{file_name}): {err}")

    print(f"Done with {directory}/{file_name}\n")


if __name__ == "__main__":
    NussbaumScraper(BASE_URL).parse()
