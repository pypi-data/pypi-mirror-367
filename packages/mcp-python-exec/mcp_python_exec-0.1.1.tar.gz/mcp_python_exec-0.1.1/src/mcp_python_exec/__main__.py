import argparse
from pprint import pprint

from .executor import ChrootExecutor

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("python_code", type=str)
    parser.add_argument("--requirements", "-r", type=str, default=None)
    args = parser.parse_args()
    requirements = args.requirements.split(",") if args.requirements else None
    pprint(ChrootExecutor().exec_venv(args.python_code, requirements))

if __name__ == "__main__":
    main()
