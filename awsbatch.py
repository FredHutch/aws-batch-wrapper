#!/usr/bin/env python3

"""
Wrapper for AWS Batch.
"""

import argparse
import sys

# Constants
DEFAULT_COMPUTE_ENVIRONMENT = "default"
DEFAULT_COMPUTE_ENVIRONMENT_WITH_SCRATCH = "default-with-scratch"
DEFAULT_QUEUE = "default"


def submit(args):
    "submit a job"
    print("hello from the submit function!")

def list_jobs(args):
    "list jobs"
    pass

def no_subcommand(args): # pylint: disable=unused-argument
    "if user did not specify a subcommand"
    print("You did not specify a subcommand.")
    print("Try `awsbatch --help` for help.")
    sys.exit(1)


def main():
    "Do the work."
    description = ["Interact with the AWS Batch Service",
                   "See full documentation at https://bit.ly/AWSBatchAtHutch"]
    parser = argparse.ArgumentParser("\n".join(description))
    parser.set_defaults(func=no_subcommand)
    # subcommands: submit, list, log, create-def, terminate
    subparsers = parser.add_subparsers(help='additional help',
                                       title='subcommands',
                                       description='submit, list, log create-def, terminate')

    parser_submit = subparsers.add_parser('submit', help='submit help')
    parser_submit.set_defaults(func=submit)

    # add arguments---
    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()
