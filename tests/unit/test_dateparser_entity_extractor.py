import unittest

from dateparser_extended.extended_dateparser import ExtendedDateParser
from datetime import datetime, timedelta


class ExtendedDateParserTest(unittest.TestCase):

    def setUp(self) -> None:
        self.parser = ExtendedDateParser()

    def test_parse(self):
        now = datetime.now()

        result = self.parser.parse('31. 10. 1965')
        self.assertEqual(result, datetime(1965, 10, 31).date())

        result = self.parser.parse('6.1.')
        year = now.year if now <= datetime(now.year, 1, 6) else now.year + 1
        self.assertEqual(result, datetime(year, 1, 6).date())

        result = self.parser.parse('zitra')
        self.assertEqual(result, (datetime.now() + timedelta(days=1)).date())

        result = self.parser.parse('dneška')
        self.assertEqual(result, datetime.now().date())

        result = self.parser.parse('blbost')
        self.assertEqual(result, None)

    def test_search_dates(self):
        now = datetime.now()

        dates = self.parser.search_dates('chci dovcu do 12.1.2022')
        self.assertEqual(len(dates), 1)

        self.assertEqual(dates[0]['start'], 14)
        self.assertEqual(dates[0]['end'], 24)
        self.assertEqual(dates[0]['value'], '12. 1.2022')
        self.assertEqual(dates[0]['parsed_date'], datetime(2022, 1, 12).date())


        dates = self.parser.search_dates('chci dovcu od nedele do 23.12.')
        self.assertEqual(len(dates), 2)

        self.assertEqual(dates[0]['start'], 14)
        self.assertEqual(dates[0]['end'], 20)
        self.assertEqual(dates[0]['value'], 'neděle')
        sunday = [now + timedelta(i) for i in range(0, 7) if ((now + timedelta(i)).weekday() == 6)][0]
        self.assertEqual(dates[0]['parsed_date'], sunday.date())

        self.assertEqual(dates[1]['start'], 24)
        self.assertEqual(dates[1]['end'], 30)
        self.assertEqual(dates[1]['value'], '23. 12')
        year = now.year if now <= datetime(now.year, 12, 23) else now.year + 1
        self.assertEqual(dates[1]['parsed_date'], datetime(year, 12, 23).date())

    def test_find_date_range(self):
        texts = [
            "chci dovcu 23. 12. - 1. 1.",
            "chci dovcu 23. 12. — 1. 1.",
            "chci dovcu 23. 12. až 1. 1.",
            "chci dovcu od 23. 12. do 1. 1.",
            "chci dovcu od 23. 12. do 1. 1.",
            "chci dovcu začínající 23. 12. s koncem 1. 1.",
        ]

        for text in texts:
            dates = [
                {"start": text.find('23. 12.'), "end": text.find('23. 12.') + len('23. 12.')},
                {"start": text.find('1. 1.'), "end": text.find('1. 1.') + len('1. 1.')},
            ]

            self.parser._detect_date_range(dates, text)

            self.assertIn('range', dates[0], 'Not classified the 1st entity with any role in "' + text + '".')
            self.assertEqual(dates[0]['range'], 'start', 'Not classified the 1st entity with the correct role in "' + text + '".')
            self.assertIn('range', dates[1], 'Not classified the 2nd entity with any role in "' + text + '".')
            self.assertEqual(dates[1]['range'], 'end', 'Not classified the 2nd entity with the correct role "' + text + '".')

    def test_find_date_range_partial(self):
        text = "dovca od 23. 12."
        dates = [{"start": 9, "end": 16}]
        self.parser._detect_date_range(dates, text)
        self.assertIn('range', dates[0])
        self.assertEqual(dates[0]['range'], 'start')

        text = "dovca do 23. 12."
        dates = [{"start": 9, "end": 16}]
        self.parser._detect_date_range(dates, text)
        self.assertIn('range', dates[0])
        self.assertEqual(dates[0]['range'], 'end')

    def test_find_date_range_swapped(self):
        text = "dovca do 1. 1. od 23. 12."
        dates = [{"start": 9, "end": 14}, {"start": 18, "end": 25}]
        self.parser._detect_date_range(dates, text)
        self.assertIn('range', dates[0])
        self.assertEqual(dates[0]['range'], 'end')
        self.assertIn('range', dates[1])
        self.assertEqual(dates[1]['range'], 'start')

    def test_find_date_next_week(self):
        now = datetime.now()
        wednesday = [now + timedelta(i) for i in range(0, 7) if ((now + timedelta(i)).weekday() == 2)][0].date()
        next_wednesday = [wednesday + timedelta(i) for i in range(1, 8) if ((wednesday + timedelta(i)).weekday() == 2)][0]
        next_friday = [wednesday + timedelta(i) for i in range(1, 8) if ((wednesday + timedelta(i)).weekday() == 4)][0]

        text = "od středy do další středy"
        dates = self.parser.search_dates(text)

        self.assertEqual(dates[0]['parsed_date'], wednesday)
        self.assertIn('range', dates[0])
        self.assertEqual(dates[0]['range'], 'start')

        self.assertEqual(dates[1]['parsed_date'], next_wednesday)
        self.assertIn('range', dates[1])
        self.assertEqual(dates[1]['range'], 'end')

        text = "od středy do pátku"
        dates = self.parser.search_dates(text)

        self.assertEqual(dates[0]['parsed_date'], wednesday)
        self.assertIn('range', dates[0])
        self.assertEqual(dates[0]['range'], 'start')

        self.assertEqual(dates[1]['parsed_date'], next_friday)
        self.assertIn('range', dates[1])
        self.assertEqual(dates[1]['range'], 'end')

        text = "od středy do dalšího pátku"
        dates = self.parser.search_dates(text)

        self.assertEqual(dates[0]['parsed_date'], wednesday)
        self.assertIn('range', dates[0])
        self.assertEqual(dates[0]['range'], 'start')

        self.assertEqual(dates[1]['parsed_date'], next_friday)
        self.assertIn('range', dates[1])
        self.assertEqual(dates[1]['range'], 'end')


if __name__ == '__main__':
    unittest.main()
