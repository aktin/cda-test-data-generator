import random
from datetime import datetime, timedelta
from .generator import AbstractGenerator


class DateGenerator(AbstractGenerator):
    def __init__(self, start_date: datetime, end_date: datetime, date_format="yyyymmdd"):
        self.start_date = start_date
        self.end_date = end_date
        self.format = date_format

    def generate(self):
        while True:
            random_date = self.start_date + timedelta(
                seconds=random.randint(0, int((self.end_date - self.start_date).total_seconds()))
            )
            if self.format == 'yyyymmdd':
                yield random_date.strftime('%Y%m%d')
            elif self.format == 'yyyymmddhhmm':
                yield random_date.strftime('%Y%m%d%H%M')
            elif self.format == 'yyyymmddhhmmss':
                yield random_date.strftime('%Y%m%d%H%M%S')
            else:
                yield random_date.strftime('%Y%m%d%H%M%S')  # Default to full format
