import argparse
import csv
import logging
import sys
from time import sleep

import scrape
import model

logger = logging.getLogger('mdq')


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


def clamp(i, min_, max_):
    return max(min_, min(max_, i))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbose', action='count', default=0, help='log more info. can be used twice')

    actions = parser.add_subparsers(title='action', dest='action')
    scrape_parser = actions.add_parser('scrape')
    scrape_parser.add_argument('-s', '--start-at-page', type=int, default=1)

    build_parser = actions.add_parser('build-model')

    say_parser = actions.add_parser('say')

    args = parser.parse_args()

    loglevels = [logging.WARNING, logging.INFO, logging.DEBUG]

    logging.basicConfig(level=loglevels[clamp(args.verbose, 0, 2)])

    logger.debug(args)

    if args.action is None:
        parser.print_help()
        sys.exit(2)

    messages = load_messages()
    orig_len = len(messages)

    logger.info('Loaded %s donation messages from disk', orig_len)

    if args.action == 'scrape':
        known_urls = frozenset(message[0] for message in messages)
        try:
            for url in scrape.get_donation_urls(
                    start_at_page=args.start_at_page, known=known_urls):
                #sleep(.1)
                message = scrape.get_message(url)
                if message:
                    messages.append((url, message))
                logger.debug('url %s', url)
                logger.debug('message %s', message)
                if len(messages) % 25 == 0:
                    dump_messages(messages)
        except KeyboardInterrupt:
            logger.warning('Received interrupt. Stopping.')

        dump_messages(messages)

    elif args.action == 'build-model':
        logger.error('not implemented')

    elif args.action == 'say':
        logger.error('not implemented')
