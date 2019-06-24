from bs4 import BeautifulSoup
import requests
from itertools import count
from urllib.parse import urljoin
import logging
from time import sleep

logger = logging.getLogger(__name__)

_session = None
def get_session():
    global _session
    if not _session:
        _session = requests.Session()
        _session.headers['User-Agent'] = "codls fun scraper/0"
    return _session


def get_and_parse_page(n=1):
    DONATIONS_LIST = 'https://gamesdonequick.com/tracker/donations/'
    session = get_session()

    logger.info('Fetching page %s', n)
    resp = session.get(
            DONATIONS_LIST,
            params={'page': n})
    if not resp.ok:
        if resp.status_code == 404:
            logger.info('Page %s does not exist', n)
            return None
        elif resp.status_code == 429:
            logger.info('Rate limited for %s seconds', resp.headers['retry-after'])
            raise RateLimited(int(resp.headers['retry-after']))
        else:
            raise Exception(resp)
    soup = BeautifulSoup(resp.text, 'html.parser')
    rows = [row for row in soup.table.children if row.name == 'tr']
    relative_urls = filter(None, map(parse_row, rows))
    urls = map(lambda url: urljoin(DONATIONS_LIST, url), relative_urls)
    return list(urls)


def parse_row(row_soup):
    cols = row_soup('td')
    if cols[3].string.strip() == 'Yes':
        return cols[2].a['href']


def get_message(url, try_not_to_get_rate_limited=True):
    session = get_session()
    resp = session.get(url)
    if try_not_to_get_rate_limited:
        sleep(2)
    if not resp.ok:
        if resp.status_code == 429:
            logger.info('Rate limited for %s seconds', resp.headers['retry-after'])
            raise RateLimited(int(resp.headers['retry-after']))
        else:
            raise Exception(resp)
    soup = BeautifulSoup(resp.text, 'html.parser')
    message = soup.table.find('td')
    if (
            message.find('i', class_='fa-question-circle')
            or message.find('i', class_='fa-times-circle')):
        # message is pending approval or rejected
        return None
    return message.get_text().strip()


def get_donation_urls(start_at_page=1, known=None):
    if not known:
        known = frozenset()
    for page in count(start_at_page):
        logger.info('%s donations with messages found so far', len(known))
        new = get_and_parse_page(page)
        if not new:
            break
        new = frozenset(new).difference(known)
        known = known.union(new)
        for url in new:
            yield url


class RateLimited(Exception):
    def __init__(self, seconds):
        self.seconds = seconds
