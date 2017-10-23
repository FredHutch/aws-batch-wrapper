#!/usr/bin/env python3

"""
Script to generate a partially-filled-in template for job definitions.

It will automatically fill in the following parts of a job definition JSON:

- Job role ARN (based on name of PI passed in by user) to allow S3 access to PI bucket
- Image (if user does not specify it)
- Volumes and mount points, so that /scratch can be used as scratch space.
- placeholders for stuff the end user needs to edit (?)

"""

# stdlib imports
import argparse
import json
import re

# third-party imports

# local imports
import config
import utils


def pi_validate(piname, pat=re.compile(r'^[a-z]{1,20}-[a-z]{1}$', re.UNICODE)):
    """Ensure pi-name matches regex."""
    if not pat.match(piname):
        errmsg = ["",
                  "PI name should be lowercase last name, dash, and first initial.",
                  "example: doe-j"]
        raise argparse.ArgumentTypeError("\n".join(errmsg))
    return piname


def main():
    "do the work"
    description = ["Create a partially-filled-in job definition template.",
                   "See full documentation at",
                   "https://bit.ly/AWSBatchAtHutch#create-a-job-definition"]
    parser = argparse.ArgumentParser(description="\n".join(description),
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-p", "--pi-name", required=True, type=pi_validate,
                        help="Your PI's last name, a dash, and first initial. Example: doe-j")
    args = parser.parse_args()
    job_role_arn = "arn:aws:iam::{}:role/fh-pi-{}-batchtask".format(config.ACCOUNT_NUMBER,
                                                                    args.pi_name)
    image = utils.get_latest_docker_image()
    template = dict(jobDefinitionName="", type="container",
                    parameters=dict(KeyName=""),
                    retryStrategy=dict(attempts=1),
                    containerProperties=dict(image=image, vcpus=1, memory=2000,
                                             command=[""],
                                             jobRoleArn=job_role_arn,
                                             volumes=[dict(host=dict(sourcePath="/docker_scratch"),
                                                           name="docker_scratch")],
                                             environment=[],
                                             mountPoints=[dict(containerPath="/scratch",
                                                               readOnly=False,
                                                               sourceVolume="docker_scratch")],
                                             ulimits=[]))
    print(json.dumps(template, indent=4))

if __name__ == "__main__":
    main()
