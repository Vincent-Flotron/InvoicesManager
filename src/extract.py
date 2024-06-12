import format
from utils import ExecuteQuery


class Extract:
    def __init__(self):
        pass

    def extract(self, input):
        pass


class ExtractDate(Extract):
    def __init__(self):
        super().__init__()

    def extract(self, input):
        output = format.format_date(input)
        return output


class ExtractAmount(Extract):
    def __init__(self):
        super().__init__()

    def extract(self, input):
        output = round(float(input), 2)
        return output


class ExtractUsingQuery(Extract, ExecuteQuery):
    def __init__(self, conn, function_query):
        Extract.__init__(self)
        ExecuteQuery.__init__(self, conn, function_query)

    def extract(self, input):
        return ExecuteQuery.execute(self, input)
