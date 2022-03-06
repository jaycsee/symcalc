from sympycalc import *

# Script to start a default calculator on the command line


def main():
    Calculator().register_default_plugins().interact()


if __name__ == "__main__":
    main()
