import unittest

from preparse.core import Group, Order, PreParser


class TestGroupMaximize(unittest.TestCase):

    def parse(self, *, solution, query, **kwargs):
        parser = PreParser(**kwargs)
        msg: str = "parser=%r, query=%r" % (parser, query)
        answer = parser.parse_args(query)
        superanswer = parser.parse_args(answer)
        self.assertEqual(answer, superanswer, msg=msg)
        self.assertEqual(answer, solution, msg=msg)

    def test_basic_maximize_grouping(self):
        self.parse(
            order=Order.GIVEN,
            group=Group.MAXIMIZE,
            optdict={"-a": 0, "-b": 0, "-c": 0},
            query=["-a", "-b", "-c"],
            solution=["-abc"],
        )

    def test_mixed_with_non_groupable_due_to_argument(self):
        self.parse(
            order=Order.GIVEN,
            group=Group.MAXIMIZE,
            optdict={"-a": 0, "-b": 1, "-c": 0},
            query=["-a", "-b", "val", "-c"],
            solution=["-ab", "val", "-c"],
        )

    def test_grouping_across_permuted_positionals(self):
        self.parse(
            group=Group.MAXIMIZE,
            order=Order.PERMUTE,
            optdict={"-x": 0, "-y": 0, "-z": 0},
            query=["arg1", "-x", "-y", "arg2", "-z"],
            solution=["-xyz", "arg1", "arg2"],
        )

    def test_grouping_stops_due_to_optional_arg(self):
        self.parse(
            order=Order.GIVEN,
            group=Group.MAXIMIZE,
            optdict={"-a": 0, "-b": 2, "-c": 0},
            query=["-a", "-b", "-c"],
            solution=["-ab", "-c"],  # b has optional arg, cannot group
        )

    def test_grouping_preserved_if_possible(self):
        self.parse(
            order=Order.GIVEN,
            group=Group.MAXIMIZE,
            optdict={"-f": 0, "-g": 0, "-h": 0},
            query=["-f", "-g"],
            solution=["-fg"],  # compacted
        )

    def test_grouping_multiple_clusters(self):
        self.parse(
            group=Group.MAXIMIZE,
            order=Order.PERMUTE,
            optdict={"-a": 0, "-b": 0, "-c": 0, "-x": 0, "-y": 0},
            query=["-a", "-b", "-c", "arg", "-x", "-y"],
            solution=["-abcxy", "arg"],
        )

    def test_grouping_multiple_clusters_given(self):
        self.parse(
            optdict={"-a": 0, "-b": 0, "-c": 0, "-x": 0, "-y": 0},
            query=["-a", "-b", "-c", "arg", "-x", "-y"],
            solution=["-abc", "arg", "-xy"],
            group=Group.MAXIMIZE,
            order=Order.GIVEN,
        )

    def test_grouping_multiple_clusters_posix(self):
        self.parse(
            optdict={"-a": 0, "-b": 0, "-c": 0, "-x": 0, "-y": 0},
            query=["-a", "-b", "-c", "arg", "-x", "-y"],
            solution=["-abc", "arg", "-x", "-y"],
            group=Group.MAXIMIZE,
            order=Order.POSIX,
        )

    def test_cannot_group_across_required_arg(self):
        self.parse(
            optdict={"-m": 0, "-n": 1, "-o": 0},
            query=["-m", "-n", "data", "-o"],
            solution=["-mn", "data", "-o"],  # -n prevents grouping
            order=Order.GIVEN,
            group=Group.MAXIMIZE,
        )

    def test_grouping_with_double_dash(self):
        self.parse(
            order=Order.GIVEN,
            group=Group.MAXIMIZE,
            optdict={"-a": 0, "-b": 0},
            query=["-a", "--", "-b"],
            solution=["-a", "--", "-b"],  # grouping not done past "--"
        )

    def test_preserve_original_if_only_one(self):
        self.parse(
            order=Order.GIVEN,
            group=Group.MAXIMIZE,
            optdict={"-q": 0},
            query=["-q"],
            solution=["-q"],
        )


if __name__ == "__main__":
    unittest.main()
