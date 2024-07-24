""""""

from datetime import datetime, date
import os
import json
from models import storage
import regex as re
from bs4 import BeautifulSoup
from concurrent.futures import as_completed
from requests_futures.sessions import FuturesSession


class DaySelection:
    """"""

    _cache_dir = "/tmp/wordaday/"
    _earliest = date.fromisoformat("2024-01-01")

    def __init__(self, day):
        os.makedirs(self._cache_dir, exist_ok=True)
        if isinstance(day, str):
            try:
                self.date = datetime.strptime(day, "%Y-%m-%d").date()
            except ValueError:
                raise
        else:
            self.date = day

        filename = f'{self.date.strftime("%Y_%m_%d")}-wordlist.json'
        self.file = os.path.join(self._cache_dir, filename)
        self.words = []
        if os.path.exists(self.file):
            self.load_json_file()
        else:
            self.load_history_db()

        if not self.words:
            self.make_selection()

    def load_json_file(self):
        """"""
        with open(self.file, "r") as f:
            content = json.load(f)
        if content:
            self.definitions = content
            self.words = [word for word in content.keys()]

    def load_history_db(self):
        """"""
        words = storage.load_day_words(self.date)
        if words:
            self.words = words

    def make_selection(self):
        if self.date < self._earliest:
            return

        words = storage.select_day_words(self.date)
        self.words = words
        self.fetch_definitions()

        with open(self.file, "w") as f:
            json.dump(self.definitions, f)

    def fetch_definitions(self):
        session = FuturesSession(max_workers=40)

        session.headers.update(
            {
                "User-Agent": "word-a-day/v1 johnnieqaym@gmail.com python3/requests",
            }
        )

        html_futures = []
        json_futures = []

        for word in self.words:
            html_futures.append(make_request(word["title"], "html", session))
            json_futures.append(make_request(word["title"], "json", session))

        wordlist = {}
        for future in as_completed(html_futures):
            wordlist[future.word] = parse_html(future.result().text)

        for future in as_completed(json_futures):
            resp = future.result()
            wordlist[future.word]["definitions"] = parse_json(resp.json())

        self.definitions = wordlist

    def get_word(self, idx):
        """"""
        idx = int(idx)
        if self.words:
            word = self.words[idx]
            if isinstance(word, dict):
                word = word["title"]
            return self.definitions[word]


def make_request(word, api, session):
    urls = {
        "html": "https://en.wiktionary.org/w/rest.php/v1/page/{0}/html",
        "json": "https://en.wiktionary.org/api/rest_v1/page/definition/{0}?redirect=false",
    }
    url = urls.get(api)
    if url:
        future = session.get(url.format(word))
        future.word = word
        return future


def soupify(html):
    return BeautifulSoup(html, "lxml")


def get_section(tag, name):
    section = tag.find(id=name)
    if section:
        return section.parent


def pronunciation(html):
    pronunciation = {}
    sect = get_section(html, "Pronunciation")
    if sect:
        pronunciation["ipa"] = [
            i.get_text() for i in sect.find_all(class_="IPA") if i.parent.name != "a"
        ]

        for aud in sect.find_all("source", type="audio/wav"):
            pronunciation["audio_link"] = f"https:{aud.get('src')}"

    return pronunciation


def etymology(html):
    etymology = {}
    sect = get_section(html, "Etymology")
    if sect:
        tag = sect.p or sect.li
        raw = tag.get_text()
        etymology["origin"] = sanitise_html(raw)

    return etymology


def sanitise_html(html):
    encoded = html.encode("ascii", "ignore")
    return encoded.decode()


def parse_html(html):
    word = {}

    soup = soupify(html)
    word["title"] = soup.title.string

    english_h2 = soup.find(id=re.compile("English|Translingual"))
    if english_h2:
        english = english_h2.parent
        word["pronunciation"] = pronunciation(english)
        word["etymology"] = etymology(english)

    return word


def parse_json(json):
    definitions = []

    definition = json.get("en")

    if definition:
        for pos in definition:
            part_of_speech = pos.get("partOfSpeech")
            for defi in pos.get("definitions"):
                if defi.get("definition"):
                    definition = {}
                    definition["part_of_speech"] = part_of_speech
                    html_def = soupify(defi.get("definition"))
                    if html_def.find(class_=re.compile(r"math")):
                        # TODO: Implement something for math equations
                        continue
                    else:
                        definition["definition"] = sanitise_html(
                            html_def.get_text()
                        ).strip()

                    examples = defi.get("parsedExamples")
                    definition["examples"] = []
                    if examples:
                        for ex in examples:
                            example = soupify(ex.get("example"))
                            if example.find(class_=re.compile(r"math")):
                                continue
                            example = sanitise_html(example.get_text())
                            if ex.get("translation"):
                                example = f"{example} - {ex.get('translation')}"
                            definition["examples"].append(example.strip())
                    definitions.append(definition)

    return definitions
