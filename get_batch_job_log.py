#!/usr/bin/env python3

"Print out log output from a job"

import sys

import boto3

def main():
    "do the work"
    if not len(sys.argv) == 2:
        print("Please supply a job ID or log stream name!")
        sys.exit(1)
    identifier = sys.argv[1]
    log_group_name = "/aws/batch/job"
    logs = boto3.client('logs')
    if "/" in identifier: # it's a log stream name
        log_stream_name = identifier
    else:
        job_id = identifier
        batch = boto3.client('batch')
        job_descs = batch.describe_jobs(jobs=[job_id])['jobs']
        if not job_descs:
            print("No such job!")
            sys.exit(1)
        job = job_descs[0]
        if not job['status'] in ['RUNNING', 'SUCCEEDED', 'FAILED']:
            msg = "".join(["Job has no log output yet (status {}), ",
                           "try again when it's RUNNING."])
            print(msg.format(job['status']))
            sys.exit(1)
        # FIXME add a cmdline option to get a specific attempt, for now default to attempt #0
        attempt_index = 0
        attempt = job['attempts'][attempt_index]
        log_stream_name = attempt['container']['logStreamName']
    args = dict(logGroupName=log_group_name, logStreamName=log_stream_name,
                startFromHead=True)
    while True:
        # TODO take arguments constraining log output by time range/limit
        # TODO add an option like tail -f to continually look for new log info
        result = logs.get_log_events(**args)
        if not result['events']:
            break
        next_token = result['nextForwardToken']
        args['nextToken'] = next_token
        # FIXME add option to show timestamp in a human-readable way
        for event in result['events']:
            print(event['message'])

if __name__ == "__main__":
    main()
