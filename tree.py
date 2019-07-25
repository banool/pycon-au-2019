#!/usr/bin/env python3

import logging
import sys
from argparse import ArgumentParser, RawDescriptionHelpFormatter



LOG = logging.getLogger(__name__)
LOG.setLevel("INFO")
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
ch = logging.StreamHandler()
ch.setFormatter(formatter)
LOG.addHandler(ch)


class Node:
    def __init__(self, *, module_name, import_time, indentation):
        self.module_name = module_name
        self.import_time = import_time
        self.indentation = indentation
        self.children = []

    def get_children_from_lines(self, lines):
        """
        This function relies on the input being structured like this:
        a
          b
            c
        not like this:
            a
          b
        c

        lines: The lines produced by running a program with PYTHONPROFILEIMPORTTIME=1
               but given in reverse (since it's easier to build a tree from the root).
               See above for an example.
        """
        nodes = []
        for i, l in enumerate(lines):
            indentation = (l.split("|")[-1].count(" ") - 1) // 2 + 1
            # Ensure that we only look at nodes directly underneath us.
            if indentation == self.indentation:
                break
            if indentation != self.indentation + 1:
                continue
            module_name = l.split("|")[-1].lstrip().rstrip()
            import_time = int(l.split("|")[0].split()[-1])
            new = Node(
                module_name=module_name, import_time=import_time, indentation=indentation
            )
            new.get_children_from_lines(lines[i + 1 :])
            nodes.append(new)
        self.children = nodes[::-1]  # We have to reverse the nodes again.

    def get_import_time_of_subtree(self):
        """ This includes itself. """
        children = sum(c.get_import_time_of_subtree() for c in self.children)
        return self.import_time + children

    def __str__(self):
        return "{} {} {}".format(
            self.indentation * " ", self.module_name, self.import_time
        )

    def print_tree(self):
        print(self.__str__())
        for child in self.children:
            child.print_tree()

    def _get_flamegraph_output(self):
        """ Returns a list of lines of flamegraph output. """
        out = []
        out.append("{} {}".format(self.module_name, self.import_time))
        for c in self.children:
            for a in c._get_flamegraph_output():
                o = "{};{}".format(self.module_name, a)
                out.append(o)
        return out

    def get_flamegraph_output(self):
        """
        The flamegraph script doesn't need an explicit root. As such, this public
        method purposely exludes the root (itself) from the output.
        """
        out = []
        for c in self.children:
            out += c._get_flamegraph_output()
        return out


def parse_args():
    parser = ArgumentParser(
        description=(
            "Script that converts the output of the Python 3.7 import profiler to\n"
            "a format that is understood by the flamegraph.pl script. Credit for the\n"
            "flamegraph script to https://github.com/brendangregg/FlameGraph.\n\n"
            "Use it like this:\n\n"
            "  PYTHONPROFILEIMPORTTIME=1 python my_program.py 2> my_program.stderr\n"
            "  python {}.py my_program.stderr > my_program.profile\n"
            "  ./flamegraph.pl my_program.profile > my_program.svg"
            .format(sys.argv[0])
        ),
        formatter_class=RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "filename",
        nargs="?",
        help=(
            "File containing the stderr of your Python 3.7 program that was run with "
            "-X importtime or PYTHONPROFILEIMPORTTIME=1. It doesn't need to be "
            "completely clean, this script will filter out stuff it doesn't need."
        ),
    )
    parser.add_argument(
        "--print-tree",
        action="store_true",
        help="Instead of printing output for flamegraph, just print the import tree",
    )
    return parser.parse_args()


def _get_tree(lines):
    lines = [c for c in lines if c.startswith("import time: ")]
    lines = [c for c in lines if "cumulative" not in c]
    lines = lines[::-1]  # Very important, see get_children_from_lines.

    # We don't know the total cost from the start so just set it to 0.
    root = Node(module_name="everything", import_time=0, indentation=0)
    root.get_children_from_lines(lines)
    root.import_time = root.get_import_time_of_subtree()

    return root


def main():
    args = parse_args()
    if args.filename:
        LOG.debug("Reading from {}".format(args.filename))
        with open(args.filename, "r") as f:
            lines = f.read().splitlines()
    else:
        LOG.debug("Reading from stdin because no filename was given")
        lines = list(sys.stdin)

    tree = _get_tree(lines)

    if args.print_tree:
        tree.print_tree()
        return

    for i in tree.get_flamegraph_output():
        print(i)


# Janky unit testing.
test = """
import time:       552 |        552 | encodings.latin_1
import time:         5 |          5 |     _xyz
import time:        10 |         15 |   xyz
import time:        49 |         49 |     _abc
import time:       557 |        605 |   abc
import time:       543 |       1163 | io
import time:        81 |         81 |   _locale
import time:       400 |        481 | _bootlocale
"""
test = [t for t in test.splitlines() if t]
expected = """
encodings.latin_1 552
io 543
io;xyz 10
io;xyz;_xyz 5
io;abc 557
io;abc;_abc 49
_bootlocale 400
_bootlocale;_locale 81
"""
expected = [t for t in expected.splitlines() if t]
assert _get_tree(test).get_flamegraph_output() == expected


if __name__ == "__main__":
    main()
