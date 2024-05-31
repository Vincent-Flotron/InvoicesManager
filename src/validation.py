import re


DATE_PATTERN = r"([0-3]\d{3}|\d{2})[-\./](0\d|1[0-2])[-\./][0-3]\d"
DATE_RE = re.compile(DATE_PATTERN)


def date_is_valid(date):
    return DATE_RE.match(date)