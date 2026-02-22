import sys
from brios.cli import Application

parser = Application.setup_parser()
args = parser.parse_args(sys.argv[1:])
print(args)
