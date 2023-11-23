"""Pull a user's 17lands event history"""

from pandas import DataFrame
from requests_html import HTMLSession
from bs4 import BeautifulSoup


def _parse_row(tr):
    """Parse an individual row from the event history"""

    soup = BeautifulSoup(tr.html)
    cells = soup.find_all("td")

    data = [cell.get_text() for cell in cells]
    data[2] = "x" if cells[2].find("span") else ""  # Trophy status

    colors = cells[3].find("span")
    color = colors.get("title")
    color = colors.get("class") if not color else color
    data[3] = color
    # TODO: get the links

    return data


def get_event_history(url: str = None):
    """Pulls a user's 17lands event history based on their shared link."""

    session = HTMLSession()
    r = session.get(url)
    r.html.render(sleep=5, keep_page=True)  # Wait for JS to load
    d = r.html.find(
        "#app > div > div:nth-child(2) > div.scrolling-table > table", first=True
    )

    # Table Headers
    th = d.find("thead", first=True).find("th")
    headers = [el.text for el in th]
    headers[2] = "Trophy"

    # Data
    rows = d.find("tr")[1:]  # Ignore the headers
    data = [_parse_row(row) for row in rows]

    return DataFrame(data, columns=headers)
