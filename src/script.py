"""Example sript"""

import argparse

from package.package_class import Class


def auto_int(x):
    return int(x, 0)


parser = argparse.ArgumentParser(prog="script", description="Script template with two different parameters")
parser.add_argument("-s", "--string", type=str, required=True, help="string parameter")
parser.add_argument("-i", "--int", type=int, required=True, help="integer parameter")
args = parser.parse_args()

c = Class()
print(f"Script({c.method(args.string)}, {args.int})")
