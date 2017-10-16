#!/usr/bin/env python3

"""
Onboard a new user to AWS Batch.
"""

# stdlib imports
import sys

# relative imports
import config

def main():
    "Do the work."
    if not len(sys.argv) == 3:
        print("usage: {} hutchnet-id-of-user pi_lastname_firstinitial".format(sys.argv[0]))
        print("Example: {} jdoe smith-b".format(sys.argv[0]))
        sys.exit(1)
    user = sys.argv[1]
    pi = sys.argv[2] # pylint: disable=invalid-name
    # steps:
    #

if __name__ == "__main__":
    main()

# test user batch-test-user has pi atestp-i.
