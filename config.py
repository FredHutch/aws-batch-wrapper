#!/usr/bin/env python3

"""config info"""

import boto3

SCICOMP_ACCOUNT_NUMBER = "344850189907"
HSE_ACCOUNT_NUMBER = "064561331775"

# Allows full access to the batch service as well as the ability to pass the
# following roles/instance profile: ADMIN_ROLE, ADMIN_INSTANCE_PROFILE
ADMIN_BATCH_GROUP = "Fh-batch-fullaccess"

ACCOUNT_NUMBER = boto3.client('sts').get_caller_identity()['Account']

ADMIN_ROLE = "arn:aws:iam::{}:role/fh-pi-universal-batchservice".format(ACCOUNT_NUMBER)

ADMIN_INSTANCE_PROFILE = \
    "arn:aws:iam::{}:instance-profile/fh-pi-universal-batchrole".format(ACCOUNT_NUMBER)

BATCH_ROLE = "arn:aws:iam::{}:role/fh-pi-universal-batchrole".format(ACCOUNT_NUMBER)

BATCH_SERVICE = "arn:aws:iam::{}:role/fh-pi-universal-batchservice".format(ACCOUNT_NUMBER)

BUCKET_ACCESS_POLICY = "arn:aws:iam::{account}:policy/fh-pi{pi}-bucket-access"

END_USER_BATCH_GROUP = "fh-pi-end-user-batch-access"
PASS_ROLE_POLICY = "arn:aws:iam::{}:policy/fh_allow_passrole".format(ACCOUNT_NUMBER)

BATCHIT_POLICY = "arn:aws:iam::{}:policy/batchit-instance-permissions".format(ACCOUNT_NUMBER)


if ACCOUNT_NUMBER == SCICOMP_ACCOUNT_NUMBER:
    BUCKET_PREFIX = "fh-pi-sc-"
elif ACCOUNT_NUMBER == HSE_ACCOUNT_NUMBER:
    BUCKET_PREFIX = "fh-pi-"
else:
    raise ValueError('Unknown AWS account number.')
