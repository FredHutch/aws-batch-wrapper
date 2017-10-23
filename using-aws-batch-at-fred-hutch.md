<div style="display: none;">
Convert to HTML with:

pandoc using-aws-batch-at-fred-hutch.md -o using-aws-batch-at-fred-hutch.html

Then paste into the "Edit source" window at https://bit.ly/AWSBatchAtHutch .

</div>

<!-- TOC depthFrom:1 depthTo:6 withLinks:1 updateOnSave:1 orderedList:0 -->

- [What is AWS Batch?](#what-is-aws-batch)
- [Request access](#request-access)
- [For a user with HutchNet ID jblow and PI name peters-u, run:](#for-a-user-with-hutchnet-id-jblow-and-pi-name-peters-u-run)
- [Create a Docker image](#create-a-docker-image)
	- [Do you need to create your own image?](#do-you-need-to-create-your-own-image)
	- [Getting Started](#getting-started)
	- [Docker Installation Instructions](#docker-installation-instructions)
- [Deploy Docker Image](#deploy-docker-image)
	- [Create GitHub Account](#create-github-account)
	- [Create a Docker Hub Account](#create-a-docker-hub-account)
	- [Push your Dockerfile to a GitHub repository](#push-your-dockerfile-to-a-github-repository)
	- [Create an Automated Build in Docker Hub](#create-an-automated-build-in-docker-hub)
- [Create a Job Definition](#create-a-job-definition)
- [Using secrets in jobs](#using-secrets-in-jobs)
	- [Using scratch space](#using-scratch-space)
- [Submit your job](#submit-your-job)
- [Monitor job progress](#monitor-job-progress)
- [Examples](#examples)
- [References](#references)
- [Future plans](#future-plans)

<!-- /TOC -->

# What is AWS Batch?

From the [website](https://aws.amazon.com/batch/):

> AWS Batch enables developers, scientists, and engineers to easily and efficiently run hundreds of thousands of batch computing jobs on AWS. AWS Batch dynamically provisions the optimal quantity and type of compute resources (e.g., CPU or memory optimized instances) based on the volume and specific resource requirements of the batch jobs submitted. With AWS Batch, there is no need to install and manage batch computing software or server clusters that you use to run your jobs, allowing you to focus on analyzing results and solving problems. AWS Batch plans, schedules, and executes your batch computing workloads across the full range of AWS compute services and features, such as Amazon EC2 and Spot Instances.

AWS Batch uses AWS [EC2 Container Service](https://aws.amazon.com/ecs/) (ECS), meaning your job must be configured as a [Docker](https://www.docker.com/)
container.

# Request access

You don't have access to AWS Batch by default.

Request access by emailing **scicomp@fredhutch.org** with the subject
line **Request Access to AWS Batch**.

In your email, **include** the name of your PI.

SciComp will contact you when your access has been granted.


<div style="display: none;">
scicomp people:

The way to onboard a new user is to do the following:

. /app/local/aws-batch-wrapper/env/bin/activate # start virtual env
/app/local/aws-batch-wrapper/onboarding.py # show help message
# For a user with HutchNet ID jblow and PI name peters-u, run:
/app/local/aws-batch-wrapper/onboarding.py jblow peters-u

This requires some special permissions, you probably need to
authenticate your command-line session with MFA.

</div>


# Create a Docker image

## Do you need to create your own image?

## Getting Started

It's recommended (but not required) that you install
[Docker](https://www.docker.com/) on your workstation (laptop or desktop)
and develop your image on your own machine until it's ready to be deployed.

## Docker Installation Instructions

* [Windows](https://www.docker.com/docker-windows)
* [Mac](https://www.docker.com/docker-mac)
* [Ubuntu Linux](https://www.docker.com/docker-ubuntu)

# Deploy Docker Image

## Create GitHub Account

## Create a Docker Hub Account

## Push your Dockerfile to a GitHub repository

## Create an Automated Build in Docker Hub

# Create a Job Definition

# Using secrets in jobs

## Using scratch space

# Submit your job

# Monitor job progress

# Examples

# References

# Future plans
