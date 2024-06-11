import format


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


class ExtractUsingQuery(Extract):
    def __init__(self, conn, function_query):
        super().__init__()
        self.conn = conn
        self.function_query = function_query

    def extract(self, input):
        output = self.function_query(self.conn, input)
        return output
