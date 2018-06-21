from bs4 import BeautifulSoup
import requests
from itertools import count
from urllib.parse import urljoin
from time import sleep
import logging
import csv
import argparse

logger = logging.getLogger('mdq')

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


def get_message(url):
    session = get_session()
    resp = session.get(url)
    if not resp.ok:
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
        sleep(.1)
        new = get_and_parse_page(page)
        if not new:
            break
        new = frozenset(new).difference(known)
        known = known.union(new)
        for url in new:
            yield url


def load_messages():
    try:
        with open('messages.csv', 'r') as f:
            reader = csv.reader(f, dialect='unix')
            return [row for row in reader]
    except OSError:
        return list()


def dump_messages(messages):
    with open('messages.csv', 'w') as f:
        writer = csv.writer(f, dialect='unix')
        writer.writerows(messages)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbose', action="store_true")

    actions = parser.add_subparsers(title='action')
    scrape_parser = actions.add_parser('scrape')
    #parser.add_argument('action', choices=('scrape', 'build', 'say'))
    scrape_parser.add_argument('-s', '--start-at-page', type=int, default=1)
    scrape_parser.set_defaults(action='scrape')

    args = parser.parse_args()

    loglevel = logging.INFO
    if args.verbose:
        loglevel = logging.DEBUG

    logging.basicConfig(level=loglevel)

    messages = load_messages()
    orig_len = len(messages)

    logger.info('Loaded %s donation messages from disk', orig_len)

    if args.action == 'scrape':
        known_urls = frozenset(message[0] for message in messages)
        try:
            for url in get_donation_urls(
                    start_at_page=args.start_at_page, known=known_urls):
                sleep(.1)
                message = get_message(url)
                if message:
                    messages.append((url, message))
                logger.debug('url %s', url)
                logger.debug('message %s', message)
                if len(messages) % 25 == 0:
                    dump_messages(messages)
        except KeyboardInterrupt:
            logger.warning('Received interrupt. Stopping.')

        dump_messages(messages)
