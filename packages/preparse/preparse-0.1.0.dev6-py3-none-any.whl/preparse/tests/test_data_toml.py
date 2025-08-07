import tomllib
import unittest
from importlib import resources

from preparse.core import *

# Read URL of the Real Python feed from config file


class TestDataToml(unittest.TestCase):

    def get_data(self):
        text: str = resources.read_text("preparse.tests", "data.toml")
        data: dict = tomllib.loads(text)
        return data

    def test_0(self):
        data: dict = self.get_data()
        data = data["data"]
        for kwargs in data:
            self.parse(**kwargs)

    def parse(
        self,
        *,
        query,
        solution,
        **kwargs,
    ):
        parser = PreParser(**kwargs)
        msg: str = "parser=%r, query=%r" % (parser, query)
        answer = parser.parse_args(query)
        superanswer = parser.parse_args(answer)
        self.assertEqual(answer, superanswer, msg=msg)
        self.assertEqual(answer, solution, msg=msg)
