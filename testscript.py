#!/usr/bin/env python3

"""
An example of a custom function to use with the `run_batch_jobs` utility.
See its full documentation at:
https://fredhutch.github.io/aws-batch-at-hutch-docs/#submitting-with-the-run_batch_jobs-utility
"""

import json


def testfunc(obj, job_num):
    """A function that customizes job input.
    Args:
        obj (dict):    An object containing all information about the job, which may
                       be partially filled in by the command-line options passed
                       to `run_batch_jobs`.
        job_num (int): A number representing this job's index. For example, if you
                       told `run_batch_jobs` to start 10 jobs, this number
                       will be 1 the first time this function is called, and 10 the last time.
    Returns:
        dict: `obj` modified by your custom logic.
    """

    # In this example, we will tell our job to print out a custom message
    # that includes the job iteration number.

    # Let's print out the input object we receive, just to see what it looks like:
    print("Before:")
    print(obj)
    print()

    command_object = ["echo", "hello from iteration {}".format(job_num)]
    obj['containerOverrides']['command'] = command_object

    # Let's print out the job object again to see what it looks like after our
    # change:
    print("After:")
    print(obj)
    print()

    # Here we could make any other changes we want to the job object,
    # based on the job iteration number (job_num). For example,
    # if 10 jobs are started, you could do some processing on
    # one of 10 files in S3.

    # now that we have transformed `obj` to our heart's content, we
    # return the modified version:

    return obj
