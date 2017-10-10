#!/usr/bin/env python3

"""
A script to create a new AMI based on the latest ECS-compliant AMI
from Amazon, but with additional scratch space for use with AWS Batch.
Based on https://amzn.to/2zdqoNT .

This script should probably be run monthly, or whenever there is a new
ECS-compliant AMI in our region.

This script is intended to run under the SciComp AWS account.
The resulting AMI is made public so it can be used by the HSE account.

End users who want to take advantage of the scratch space are
responsible for setting up their job definitions to mount
it at /scratch (as described in the link above). Our wrapper
script should help with this.

Run me like this:

./make_new_ami.py -k dtenenba -p ~/.ssh/id_rsa -g dtenenba
"""

#stdlib imports
import time
import datetime
import argparse
import os
import sys

# third party imports
import boto3
import fabric
from fabric.api import run, env
from fabric.tasks import execute

# relative imports
import utils




def launch_instance(args):
    "Launch an instance with the specified scratch space attached."
    response = EC2.run_instances(ImageId=BASE_AMI_ID, InstanceType='t2.micro',
                                 MaxCount=1, MinCount=1, SecurityGroups=[args.security_group_name],
                                 BlockDeviceMappings=[
                                     {
                                         'DeviceName': '/dev/sdb',
                                         'Ebs': {
                                             'Encrypted': False,
                                             'VolumeSize': args.scratch_size
                                         }
                                     }
                                 ],
                                 TagSpecifications=[
                                     {'ResourceType': 'instance',
                                      'Tags': [
                                          {'Key': 'Name',
                                           'Value': 'To create a new AMI for use with Batch'},
                                          {'Key': 'ParentAMI',
                                           'Value': BASE_AMI_ID},
                                          {'Key': 'Creator',
                                           'Value': os.getenv('USER')}]}],
                                 KeyName=args.key_pair_name)
    instance_id = response['Instances'][0]['InstanceId']
    return instance_id


def run_commands_on_instance():
    """Run commands on instance using Fabric."""
    while True:
        try:
            run("echo hello")
            break
        except fabric.exceptions.NetworkError:
            print("Waiting 5 seconds for ssh to work...")
            time.sleep(5)


    run("sudo yum -y update")
    run("sudo mkfs -t ext4 /dev/xvdb")
    run("sudo mkdir /docker_scratch")
    run("sudo echo -e '/dev/xvdb\t/docker_scratch\text4\tdefaults\t0\t0' | sudo tee -a /etc/fstab")
    run("sudo mount /docker_scratch")
    run("sudo stop ecs")
    run("sudo rm -rf /var/lib/ecs/data/ecs_agent_data.json")

def tweak_instance(instance_id, args):
    """Set up instance to for modification."""
    while True:
        print("Waiting for host to be up....")
        time.sleep(5)
        desc = EC2.describe_instances(InstanceIds=[instance_id])['Reservations'][0]['Instances'][0]
        state = desc['State']['Name']
        if state == 'running':
            break
    # time.sleep(10)
    host = desc['PublicIpAddress']
    env.hosts = [host]
    env.user = 'ec2-user'
    env.key_filename = args.private_key_file
    execute(run_commands_on_instance)


def make_ami_from_instance(instance_id):
    """Create new AMI from instance."""
    EC2.stop_instances(InstanceIds=[instance_id])
    while True:
        desc = EC2.describe_instances(InstanceIds=[instance_id])['Reservations'][0]['Instances'][0]
        state = desc['State']['Name']
        if state == 'stopped':
            break
        print("Waiting for instance to stop...")
        time.sleep(15)
    now = datetime.datetime.now()
    timestamp = now.strftime("%Y%m%d%H%M%S")
    imgname = 'ECS image with 1TB non-encrypted scratch at /scratch. Created at {}.'.\
        format(timestamp)
    response = EC2.create_image(InstanceId=instance_id,
                                Name=imgname,
                                Description='based on {}, created by {}'.format(BASE_AMI_ID,
                                                                                os.getenv('USER')))
    ami_id = response['ImageId']
    EC2.create_tags(Resources=[ami_id],
                    Tags=[
                        dict(Key='Name', Value=imgname),
                        dict(Key='Type', Value='FredHutchBatchAMI')
                    ])
    print("Waiting for image creation to be complete", end="")
    while True:
        desc = EC2.describe_images(ImageIds=[ami_id])['Images'][0]
        state = desc['State']
        if state == 'available':
            break
        print(".", end="")
        sys.stdout.flush()
        time.sleep(10)
    print()
    # make it public:
    print("Making image public....")
    EC2.modify_image_attribute(ImageId=ami_id,
                               Attribute='launchPermission',
                               LaunchPermission=dict(Add=[dict(Group='all')]))
    print("Terminating instance....")
    EC2.terminate_instances(InstanceIds=[instance_id])
    return ami_id

def remove_old_amis(new_ami_id):
    """Remove old AMIs and associated snapshots"""
    print("Removing old AMIs and associated snapshots....")
    images = utils.get_latest_scratch_ami(True) # get all
    # Filter out the one we just created:
    images = [x for x in images if not x['ImageId'] == new_ami_id]
    for image in images:
        print("Deleting OLD image {}...".format(image['ImageId']))
        EC2.deregister_image(ImageId=image['ImageId'])
        for device in image['BlockDeviceMappings']:
            snapshot_id = device['Ebs']['SnapshotId']
            print("Deleting OLD snapshot {}...".format(snapshot_id))
            EC2.delete_snapshot(SnapshotId=snapshot_id)

def main():
    """Do the work."""
    parser = argparse.ArgumentParser(description="Create an AMI for use with AWS Batch.",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-s', '--scratch_size', type=int, default=1000, help="scratch size in GB")
    parser.add_argument('-g', '--security-group-name', required=True,
                        help='a security group that can SSH to the instance.')
    parser.add_argument('-k', '--key-pair-name', required=True)
    parser.add_argument('-p', '--private-key-file', required=True)

    args = parser.parse_args()


    instance_id = launch_instance(args)
    tweak_instance(instance_id, args)
    ami_id = make_ami_from_instance(instance_id)
    # TODO FIXME remove old amis and snapshots?
    remove_old_amis(ami_id)
    # return new ami id
    print("\n\nCreated new ami:\n{}".format(ami_id))
    return ami_id

if __name__ == "__main__":
    EC2 = boto3.client("ec2", region_name="us-west-2")
    BASE_AMI_ID = utils.get_latest_ecs_ami()

    main()
