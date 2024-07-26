import re


def format_date(date):
    if date != '':
        extract_YYYYMMDD = re.compile(r"(?P<year>(\d{2}|\d{4}))[-\./](?P<month>\d{2})[-\./](?P<day>\d{2})")
        matches = extract_YYYYMMDD.match(date)
        year = matches["year"]
        year = year if len(year) == 4 else f"20{year}"
        month = matches["month"]
        day = matches["day"]
        return f"{year}.{month}.{day}"
    else:
        return ''