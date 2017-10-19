#!/usr/bin/env python3

"""
Onboard a new user to AWS Batch.
"""

# stdlib imports
import sys
import json

# third-party imports
import boto3

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
    # end user needs:
    # access to the end user batch role (add to group)
    # ability to pass the following roles/instance profile:
    # role/fh-pi-universal-batchservice
    # instance-profile/fh-pi-universal-batchrole

    iam = boto3.client("iam")

    # check to see if PI group exists
    pi_group_name = "fi-pi-{}".format(pi)
    try:
        pi_group = iam.get_group(GroupName=pi_group_name)
    except iam.exceptions.NoSuchEntityException:
        print("There is no IAM group {} for this PI!".format(pi_group_name))
        sys.exit(1)

    # check to see if pi batch task role exists
    pi_batch_role_name = "fh-pi-{}-batchtask".format(pi)
    assume_role_document = {'Statement': [{'Action': 'sts:AssumeRole',
                                           'Effect': 'Allow',
                                           'Principal': {'Service': 'ecs-tasks.amazonaws.com'},
                                           'Sid': ''}],
                            'Version': '2012-10-17'}
    assume_role_json = json.dumps(assume_role_document)
    try:

        pi_batch_role = iam.get_role(RoleName=pi_batch_role_name)
    except iam.exceptions.NoSuchEntityException:
        # if it doesn't exist, create it
        pi_batch_role = iam.create_role(RoleName=pi_batch_role_name,
                                        AssumeRolePolicyDocument=assume_role_json,
                                        Description="batch role granting S3 access to {} bucket"\
                                            .format(pi))

if __name__ == "__main__":
    main()

# test user batch-test-user has pi atestp-i.
