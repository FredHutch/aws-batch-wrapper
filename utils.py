#!/usr/bin/env python3
"""
Various utilities for use with AWS batch.
"""


import boto3

def get_latest_ecs_ami():
    """Get the ID of the latest official AWS AMI in this region that is
       suitable for use with ECS and AWS Batch."""
    ec2 = boto3.client("ec2", region_name="us-west-2")
    filters = [dict(Name='manifest-location', Values=['amazon/amzn-ami-*-amazon-ecs-optimized'])]
    got = ec2.describe_images(Filters=filters)
    sorted_amis = sorted(got['Images'], key=lambda k: k['CreationDate'])
    return sorted_amis[-1]['ImageId']

def get_latest_scratch_ami(get_all=False):
    """
    Get the ID of the latest AMI created by SciComp which is based on
    official ECS-compliant AMIs but has 1TB of scratch space on it.
    These AMIs will always be owned by the SciComp account and
    have the Type: FredHutchBatchAMI tag.
    """
    ec2 = boto3.client("ec2", region_name="us-west-2")
    scicomp_account_number = '344850189907'
    filters = [{'Name': 'owner-id', 'Values': [scicomp_account_number]},
               {'Name': 'tag:Type', 'Values': ['FredHutchBatchAMI']}]
    got = ec2.describe_images(Filters=filters)
    sorted_amis = sorted(got['Images'], key=lambda k: k['CreationDate'])
    if get_all:
        return sorted_amis
    return sorted_amis[-1]['ImageId']
