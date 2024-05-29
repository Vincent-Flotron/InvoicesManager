import re


DATE_PATTERN = r"\d{4}[-\.]\d{1,2}[-\.]\d{1,2}|\d{2}[-\.]\d{1}[-\.]\d{1}"
DATE_RE = re.compile(DATE_PATTERN)


def date_is_valid(date):
    return DATE_RE.match(date)