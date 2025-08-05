import logging
import time

from django.core.management.base import BaseCommand
from django.db import connections
from django.db.utils import DatabaseError

log = logging.getLogger(__name__)


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('-t', '--timeout', default=60)
        parser.add_argument('-c', '--connection', default='default')
        parser.add_argument('-s', '--sleep', default=1)

    def handle(self, *args, **options):
        connection_name = options.get('connection')
        timeout = options.get('timeout')
        sleep = options.get('sleep')
        log.info(f'wait for db "{connection_name}" up to {timeout}s')

        try:
            connection = connections[connection_name]
        except KeyError:
            log.error(f'Connection "{connection_name}" not defined')
            raise SystemExit(1)

        t0 = time.time()
        while True:
            seconds_passed = int(time.time() - t0)
            try:
                connection.ensure_connection()
                log.info(f'db up after {seconds_passed}[s]')
                break
            except DatabaseError as e:
                log.debug(f'waited {seconds_passed}s. exception: {e}')
                if time.time() > t0 + timeout:
                    raise Exception('timeout reached')
                time.sleep(sleep)
