import symcalc

# Script to start a default calculator on the command line


def main():
    symcalc.DefaultCalculator().register_default_plugins().interact()


if __name__ == "__main__":
    main()
