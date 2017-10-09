#!/usr/bin/env python3

import sys
import time

import boto3


def cleanup():
    batch = boto3.client('batch')
    # first delete jobdef
    jobdefs = batch.describe_job_definitions(jobDefinitionName='dans-jobdef')['jobDefinitions']
    if len(jobdefs):
        batch.deregister_job_definition(jobDefinition=jobdefs[0]['jobDefinitionArn'])
    queues = batch.describe_job_queues(jobQueues=['dans-test-queue'])['jobQueues']
    if len(queues):
        batch.update_job_queue(jobQueue=queues[0]['jobQueueArn'], state='DISABLED')
        time.sleep(3)
        batch.delete_job_queue(jobQueue=queues[0]['jobQueueArn'])
    envs = batch.describe_compute_environments(computeEnvironments=['myenv'])['computeEnvironments']
    if len(envs):
        batch.update_compute_environment(computeEnvironment=envs[0]['computeEnvironmentArn'],
                                         state='DISABLED')
        time.sleep(3)
        batch.delete_compute_environment(computeEnvironment=envs[0]['computeEnvironmentArn'])

def doit():
    batch = boto3.client('batch')
    subnet = 'subnet-d2ba0cb4'
    securitygroup = 'sg-6c8e7911'
    tags = dict(Name='Dan test env', billing_contact="dtenenba@fredhutch.org")
    compute_resources = dict(type='EC2', minvCpus=0, maxvCpus=1000,
                             instanceTypes=['optimal'], subnets=[subnet],
                             securityGroupIds=[securitygroup],
                             instanceRole='arn:aws:iam::064561331775:instance-profile/fh-pi-universal-batchrole',
                             tags=tags)

    envdict = dict(computeEnvironmentName='myenv', type='MANAGED', state='ENABLED',
                   computeResources=compute_resources,
                   serviceRole='arn:aws:iam::064561331775:role/fh-pi-universal-batchservice')
    env_resp = batch.create_compute_environment(**envdict)
    while True:
        desc = batch.describe_compute_environments(computeEnvironments=['myenv'])['computeEnvironments']
        if desc[0]['status'] == 'CREATING':
            time.sleep(2)
        else:
            break
    # env_resp contains keys computeEnvironmentName and computeEnvironmentArn
    q_resp = batch.create_job_queue(jobQueueName="dans-test-queue",
                                    state='ENABLED', priority=100,
                                    computeEnvironmentOrder=[
                                        {
                                            "order": 0,
                                            "computeEnvironment": 'myenv'
                                        }
                                    ])
    while True:
        desc = batch.describe_job_queues(jobQueues=['dans-test-queue'])['jobQueues']
        if not desc[0]['status'] == 'VALID':
            time.sleep(2)
        else:
            break
    # q_resp contains keys jobQueueName and jobQueueArn
    def_resp = batch.register_job_definition(jobDefinitionName="dans-jobdef",
                                             type='container',
                                             containerProperties=dict(image='ubuntu:16.04',
                                                                      vcpus=1, memory=500,
                                                                      command=['/bin/bash', '-c', 'echo hello world'],
                                                                    #   jobRoleArn="arn:aws:iam::064561331775:role/fh-pi-fredricks-d-batchrole"))
                                                                      jobRoleArn="arn:aws:iam::064561331775:role/fh-pi-fredricks-d-batchtask"))
    # def_resp contains keys jobDefinitionName, jobDefinitionArn, and revision
    job_resp = batch.submit_job(jobName="dans-test-job", jobQueue="dans-test-queue",
                                jobDefinition=def_resp['jobDefinitionArn'])
    return job_resp


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "clean":
        print("cleaning...")
        cleanup()
    else:
        print(doit())
