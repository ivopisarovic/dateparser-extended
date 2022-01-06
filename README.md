# dateparser-extended
Built on Python dateparser library, extending it with range detection and fixing Czech dates recognition.

https://github.com/scrapinghub/dateparser

## Install

`pip install git+https://github.com/ivopisarovic/dateparser-extended.git`

## Usage

```python
from dateparser_extended import ExtendedDateParser

parser = ExtendedDateParser()

parser.parse('12.1.')
parser.search_dates('chci dovolenou od zitra do nedele')
```

## Test

`python -m unittest discover -s tests/unit`