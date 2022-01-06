from __future__ import annotations

import re
from datetime import date
from typing import List, Dict, Text, Any


from dateparser.search import search_dates
from dateparser import parse

from .utils import strip_accents


class ExtendedDateParser:

    def parse(self, text: str) -> date | None:
        """Convert the given text to machine-readable representation without time (`datetime.date`)."""

        sanitized_text = self._fix_czech_dates(text)

        date = parse(
            sanitized_text,
            languages=['cs'],
            settings={
                'PREFER_DATES_FROM': 'future',
                'PREFER_LOCALE_DATE_ORDER': False,
                'DEFAULT_LANGUAGES': ['cs'],
                'DATE_ORDER': 'DMY',
            }
        )

        return date.date() if date else None

    def search_dates(self, text: str) -> List[Dict[Text, Any]]:
        """Extract all dates from the given text.
        Returns a list of dicts containing information about the found dates and their machine-readable representation (`datetime.date`).
        """

        sanitized_text = self._fix_czech_dates(text)

        # Look for all dates in the user's message
        hits = search_dates(
            sanitized_text,
            languages=['cs'],
            settings={
                'PREFER_DATES_FROM': 'future',
                'PREFER_LOCALE_DATE_ORDER': False,
                'DEFAULT_LANGUAGES': ['cs'],
                'DATE_ORDER': 'DMY',
            },
        ) or []

        # Convert the found dates to the result objects
        dates = []
        index = 0

        for substr, timestamp in hits:
            start = index + sanitized_text[index:].find(substr)
            index = start + len(substr)
            dates.append(
                {
                    'start': start,
                    'end': start + len(substr),
                    'value': sanitized_text[start:start + len(substr)],
                    "parsed_date": timestamp.date(),
                }
            )

        self._detect_date_range(dates, sanitized_text)

        return dates

    def _fix_czech_dates(self, text: str) -> str:
        """ Sanitize Czech dates to be able to extract them using dateparser. """

        # Remove accents to lower the number of possible combinations
        text = strip_accents(text)

        # Replace inflections with the basic form to improve extraction of date using the dateparser library
        replacements = [
            (['dneska'], 'dnes'),
            (['pondeli', 'pondelka'], 'pondělí'),
            (['utery', 'uterka'], 'úterý'),
            (['streda', 'stredy', 'stredu'], 'středa'),
            (['ctvrtek', 'ctvrtku', 'ctvrtka'], 'čtvrtek'),
            (['patek', 'patky', 'patku'], 'pátek'),
            (['sobota', 'soboty', 'sobotu', 'vikend', 'vikendu'], 'sobota'),
            (['nedele', 'nedeli'], 'neděle'),
        ]

        for replacement in replacements:
            # start with the longest pattern to prevent replacing only a part of the word
            patterns = sorted(replacement[0], key=lambda x: -len(x))
            # replace all patterns in the text
            for pattern in patterns:
                text = text.replace(pattern, replacement[1])

        # Hotfix: dateparser does not extract some Czech dates without a space correctly
        # e.g., "23.12." is extracted as a time (23:12 PM) instead of 23rd December
        # https://github.com/scrapinghub/dateparser/issues/1029
        text = re.sub(r'\b([1-3][0-9]|[1-9])\.([1-9]|12)(\.|\b)', r'\1. \2.', text)

        return text

    @classmethod
    def _detect_date_range(cls, dates: List[dict], text: str):
        start_keywords = '\\b(od|začátek|začínající|začátkem)\\b'
        end_keywords = '\\b(do|až|konec|končící|koncem)\\b|\\-|–|—'

        for i, date in enumerate(dates):
            # Get the text preceding and following the extracted date.
            # Use only text till the first other date. The previous and following texts end where another date occurs.
            # E.g. "12th April to the end of April" -> "to the end of" id the previous text for date "April".
            previous_text_start = 0 if i == 0 else dates[i - 1]['end']
            previous_text = text[previous_text_start:date['start']]
            following_text_end = None if i == len(dates) - 1 else dates[i + 1]['start']
            following_text = text[date['end']:following_text_end]

            # if some keywords appear before or after the extracted date, then it is the start of the range
            if (
                    re.search(r'(' + start_keywords + ')(\s+\w+)?\s*$', previous_text) or
                    re.search(r'^\s*(' + end_keywords + ')', following_text)
            ):
                date['range'] = 'start'

            # if some keywords appear before the extracted date, then it is the end of the range
            elif re.search(r'(' + end_keywords + ')(\s+\w+)?\s*$', previous_text):
                date['range'] = 'end'
