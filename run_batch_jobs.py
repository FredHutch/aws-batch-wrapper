#!/usr/bin/env python3

" A utility for launching groups of AWS Batch Jobs"

# stdlib imports
import argparse
import os
import sys
import json

# third-party imports
import boto3



def main():
    "do the work"

    user = os.getenv("USER")
    batch = boto3.client("batch")
    description = ["Start a set of AWS Batch jobs.",
                   "See full documentation at",
                   "http://bit.ly/HutchBatchDocs/#submitting-with-the-run_batch_jobs-utility"]


    # Handle command-line arguments
    parser = argparse.ArgumentParser(description="\n".join(description),
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.prog = parser.prog.replace(".py", "")

    parser.add_argument("-q", "--queue", default="small",
                        help="Queue Name")
    parser.add_argument("-d", "--jobdef", default="hello:2",
                        help="Job definition name:version.")
    parser.add_argument("-n", "--numjobs", default=1, type=int,
                        help="Number of jobs to run.")
    parser.add_argument("--name", default="sample_job",
                        help="Name of job group (your username and job number will be injected).")
    parser.add_argument("-f", "--func",
                        help="\n".join(["Python path to a function to customize job,",
                                        "see link above for full docs. Example: myscript.myfunc"]))
    parser.add_argument("-j", "--json",
                        help="\n".join(["Output JSON instead of running jobs. JSON can be used",
                                        "with `aws batch submit-job --cli-input-json`."]))
    parser.add_argument("-x", "--cpus",
                        help="Number of CPUs, if overridding value in job defnition.")
    parser.add_argument("-m", "--memory",
                        help="GB of memory, if overridding value in job definition.")
    parser.add_argument("-p", "--parameters",
                        help="\n".join(["Parameters to replace placeholders in job definition.",
                                        "Format as a single-quoted JSON list of",
                                        "objects/dictionaries."]))
    parser.add_argument("-a", "--attempts",
                        help="Number of retry attempts, if overridding job definition.")
    parser.add_argument("-c", "--command",
                        help="\n".join(["Command, if overridding job definition. Example:",
                                        '["echo", "hello", "world"]'])) # TODO some kind of interpolation here?
    parser.add_argument("-e", "--environment",
                        help="\n".join(["Environment to replace placeholders in job definition.",
                                        "Format as a single-quoted JSON object/dictionary."]))
    args = parser.parse_args()


    # Fill in job template
    container_overrides = {}
    # is all this necessary if we use argument groups?
    if args.cpus:
        container_overrides['vcpus'] = args.cpus
    if args.memory:
        container_overrides['memory'] = args.memory
    if args.command:
        container_overrides['command'] = args.command
    if args.environment:
        try:
            env = json.loads(args.environment)
        except json.JSONDecodeError:
            print("Environment argument is not properly formatted JSON!")
            sys.exit(1)
        if not env.__class__ == list: # could do further checking here....
            print("Environment argument is not a JSON list!")
            sys.exit(1)
        container_overrides['environment'] = env
    # TODO make sure job name is valid length & has no invalid characters
    template = dict(jobName=args.name, jobQueue=args.queue, jobDefinition=args.jobdef,
                    containerOverrides=container_overrides)
    if args.attempts:
        template['retryStrategy'] = {'attempts': args.attempts}
    if args.parameters:
        try:
            params = json.loads(args.parameters)
        except json.JSONDecodeError:
            print("Parameters argument is not properly formatted JSON!")
            sys.exit(1)
        if not params.__class__ == dict:
            print("Parameters object is not a JSON object/dictionary!")
            sys.exit(1)
        template['parameters'] = params
    # print(args)
    func = None
    if args.func:
        module_dir = os.path.abspath(os.path.dirname(args.func))
        segs = os.path.basename(args.func).replace(".py", "").split(".")
        module_name = segs[0]
        func_name = segs[1]

        sys.path.append(module_dir)
        module = __import__(module_name)
        func = getattr(module, func_name)
    jobs = []
    for iteration in range(1, args.numjobs+1):
        job_template = template
        job_template['jobName'] = "{}-{}-{}".format(user, args.name, iteration)
        if func:
            job_template = func(job_template, iteration)
        if args.json:
            print(json.dumps(job_template), indent=4)
            print("\n\n")
        else:
            job = batch.submit_job(**job_template)
            del job['ResponseMetadata']
            jobs.append(job)
    print(json.dumps(jobs, indent=4))

if __name__ == "__main__":
    main()
