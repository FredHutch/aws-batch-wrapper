#!/usr/bin/env python3
"""
Various utilities for use with AWS batch.
"""

import time

import boto3
import paramiko

def get_latest_ecs_ami():
    """Get the ID of the latest official AWS AMI in this region that is
       suitable for use with ECS and AWS Batch."""
    ec2 = boto3.client("ec2", region_name="us-west-2")
    filters = [dict(Name='manifest-location', Values=['amazon/amzn-ami-*-amazon-ecs-optimized'])]
    got = ec2.describe_images(Filters=filters)
    sorted_amis = sorted(got['Images'], key=lambda k: k['CreationDate'])
    return sorted_amis[-1]['ImageId']

def get_latest_scratch_ami():
    """
    Get the ID of the latest AMI created by SciComp which is based on
    official ECS-compliant AMIs but has 1TB of scratch space on it.
    """
    ec2 = boto3.client("ec2", region_name="us-west-2")
    scicomp_account_number = '344850189907'
    filters = [dict(Name='owner-id', Values=[scicomp_account_number]),
               # NOTE we need to make sure we always name our AMIs like this, in order to find them:
               dict(Name='name', Values=['ECS image with 1TB non-encrypted scratch at /scratch'])]
    got = ec2.describe_images(Filters=filters)
    sorted_amis = sorted(got['Images'], key=lambda k: k['CreationDate'])
    return sorted_amis[-1]['ImageId']

def build_scratch_ami(key_name, security_group_name, scratch_size=1000):
    "Based on https://aws.amazon.com/blogs/compute/building-high-throughput-genomic-batch-workflows-on-aws-batch-layer-part-3-of-4/" # pylint: disable=line-too-long
    ec2 = boto3.client("ec2", region_name="us-west-2")
    base_ami_id = get_latest_ecs_ami()
    response = ec2.run_instances(ImageId=base_ami_id, InstanceType='t2.micro',
                                 MaxCount=1, MinCount=1, SecurityGroups=[security_group_name],
                                 BlockDeviceMappings=[
                                     {
                                         'DeviceName': '/dev/sdb',
                                         'Ebs': {
                                             'Encrypted': False,
                                             'VolumeSize': scratch_size
                                         }
                                     }
                                 ],
                                 TagSpecifications=[
                                     {'ResourceType': 'instance',
                                      'Tags': [{'Key': 'Name',
                                                'Value': 'To create a new AMI for use with Batch'}]}
                                 ],
                                 KeyName=key_name)
    print(response) # FIXME remove
    instance_id = response['Instances'][0]['InstanceId']
    while True:
        time.sleep(5)
        desc = ec2.describe_instances(InstanceIds=[instance_id])['Reservations'][0]['Instances'][0]
        state = desc['State']['Name']
        if state == 'running':
            break
    time.sleep(10)
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    host = desc['PublicIpAddress']
    ssh.connect(host, username='ec2-user')
    stdin, stdout, stderr = ssh.exec_command('ls')
    stdin.close()
    stdout.read().splitlines()
    command = """
sudo yum -y update && \
sudo mkfs -t ext4 /dev/xvdb && \
sudo mkdir /docker_scratch && \
sudo echo -e '/dev/xvdb\t/docker_scratch\text4\tdefaults\t0\t0' | sudo tee -a /etc/fstab && \
sudo mount –a && \
sudo stop ecs && \
sudo rm -rf /var/lib/ecs/data/ecs_agent_data.json
"""
