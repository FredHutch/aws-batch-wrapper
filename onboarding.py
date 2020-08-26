#!/usr/bin/env python3

"""
Onboard a new user to AWS Batch.

This script should be run by a user in the HSE account with full IAM permissions.
You may need to authenticate your CLI session with MFA credentials.
"""

# stdlib imports
import sys
import json

# third-party imports
import boto3

# relative imports
import config



def main(): # pylint: disable=too-many-locals, too-many-statements
    "Do the work."
    if not len(sys.argv) == 3:
        print("usage: {} hutchnet-id-of-user pi_lastname-firstinitial".format(sys.argv[0]))
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
    pi_group_name = "fh-pi-{}".format(pi)
    try:
        iam.get_group(GroupName=pi_group_name)
    except iam.exceptions.NoSuchEntityException:
        div_group_name = pi_group_name.replace("fh-pi", "fh-div")
        try:
            iam.get_group(GroupName=div_group_name)
            print("This is a divisional group (not a PI group).")
            pi_group_name = div_group_name
        except iam.exceptions.NoSuchEntityException:
            print("There is no IAM group {} for this PI!".format(pi_group_name))
            sys.exit(1)

    if pi_group_name.startswith("fh-pi"):
        type_of_group = "pi"
    elif pi_group_name.startswith("fh-div"):
        type_of_group = "div"
    else:
        print("Unknown group type!")
        sys.exit(1)

    # check to see if pi batch task role exists
    pi_batch_role_name = "fh-{}-{}-batchtask".format(type_of_group, pi)
    assume_role_document = {'Statement': [{'Action': 'sts:AssumeRole',
                                           'Effect': 'Allow',
                                           'Principal': {'Service': 'ecs-tasks.amazonaws.com'},
                                           'Sid': ''}],
                            'Version': '2012-10-17'}
    assume_role_json = json.dumps(assume_role_document)
    try:

        iam.get_role(RoleName=pi_batch_role_name)
    except iam.exceptions.NoSuchEntityException:
        # if it doesn't exist, create it
        iam.create_role(RoleName=pi_batch_role_name,
                        AssumeRolePolicyDocument=assume_role_json,
                        Description="batch role granting S3 access to {} bucket"\
                                            .format(pi))
        # attach the bucket policy to it
        bucket_policy_name = "fh-{}-{}-bucket-access".format(type_of_group, pi)
        bucket_policy_arn = "arn:aws:iam::{}:policy/{}".format(config.ACCOUNT_NUMBER,
                                                               bucket_policy_name)
        iam.attach_role_policy(RoleName=pi_batch_role_name, PolicyArn=bucket_policy_arn)
        iam.attach_role_policy(RoleName=pi_batch_role_name, PolicyArn=config.BATCHIT_POLICY)

    # add user to end user batch group
    iam.add_user_to_group(GroupName=config.END_USER_BATCH_GROUP, UserName=user)
    # attach pass-role policy to user
    iam.attach_user_policy(UserName=user, PolicyArn=config.PASS_ROLE_POLICY)
    # create an fh-pi-pinam-e-passrole policy
    pi_passrole_policy_name = "fh-{}-{}-passrole".format(type_of_group, pi)
    pi_batch_role_arn = "arn:aws:iam::{}:role/{}".format(config.ACCOUNT_NUMBER,
                                                         pi_batch_role_name)
    policy = dict(Version="2012-10-17",
                  Statement=[dict(Effect="Allow",
                                  Action=["iam:PassRole"],
                                  Resource=[pi_batch_role_arn])])
    policy_json = json.dumps(policy)
    try:
        policy_result = iam.create_policy(PolicyName=pi_passrole_policy_name,
                                          PolicyDocument=policy_json,
                                          Description=\
            'Allows users in {} group to pass S3 access role.'.format(pi))
        role_policy_arn = policy_result['Policy']['Arn']
    except iam.exceptions.EntityAlreadyExistsException:
        print("Policy {} already exists....".format(pi_passrole_policy_name))
        role_policy_arn = "arn:aws:iam::064561331775:policy/" + pi_passrole_policy_name

    # add policy to user
    iam.attach_user_policy(UserName=user, PolicyArn=role_policy_arn)

    print("Done.")

if __name__ == "__main__":
    main()

# test user batch-test-user has pi atestp-i.
