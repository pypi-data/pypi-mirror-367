from collections.abc import Iterator
from json import dumps
from urllib.parse import unquote
from urllib.parse import urlparse

from bs4 import BeautifulSoup
from bs4 import ResultSet
from bs4 import Tag
from click import argument
from click import command
from click import echo
from httpx import Client
from httpx import Response


@command()
@argument("words", nargs=-1)
def cli(words: list[str]) -> None:
    if not words:
        echo("No words to lookup", err=True)
        exit(1)
    with Client() as client:
        data = {word: proofread(client, word) for word in words}
        echo(dumps(data, indent=2, ensure_ascii=False))


def proofread(client: Client, word: str) -> bool:
    for address, page in search(client, word):
        correct = [address]
        correct.extend(scrap_all_tables(page))
        if word in correct or word.lower() in correct:
            return True
    return False


def search(client: Client, word: str) -> Iterator[tuple[str, bytes]]:
    response = form_search(client, word)
    if response.url.path.startswith("/wiki/"):
        yield response.url.path.removeprefix("/wiki/"), response.content
    else:
        for url in scrap_all_forms(response.content):
            response1 = page_table(client, url)
            yield response1.url.path.removeprefix("/wiki/"), response1.content


def form_search(client: Client, word: str) -> Response:
    return client.get(
        "https://ru.wiktionary.org/w/index.php",
        params={"search": word},
        follow_redirects=True,
    )


def page_table(client: Client, url: str) -> Response:
    return client.get(url, follow_redirects=True)


def scrap_all_forms(content: bytes) -> Iterator[str]:
    soup = BeautifulSoup(content, "html.parser")
    containers: ResultSet[Tag] = soup.select("div.mw-search-results-container")
    for container in containers:
        yield from scrap_single_form(container)


def scrap_single_form(container: Tag) -> Iterator[str]:
    links: ResultSet[Tag] = container.select("a")
    for a in links:  # pragma: no branch
        href = a.get("href")
        if isinstance(href, str):  # pragma: no branch
            url = urlparse(unquote(href))
            if url.path.startswith("/wiki/"):  # pragma: no branch
                yield f"https://ru.wiktionary.org{href}"


def scrap_all_tables(content: bytes) -> Iterator[str]:
    soup = BeautifulSoup(content, "html.parser")
    tables: ResultSet[Tag] = soup.select("table.morfotable")
    for table in tables:
        yield from scrap_single_table(table)


def scrap_single_table(table: Tag) -> Iterator[str]:
    cells: ResultSet[Tag] = table.select("td")
    for cell in cells:
        for text in cell.stripped_strings:
            for part in text.split():
                yield part.replace("̀", "").replace("́", "")
