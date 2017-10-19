<!--
Convert to HTML with:

pandoc using-aws-batch-at-fred-hutch.md -o using-aws-batch-at-fred-hutch.html

-->

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

# Create a Docker image

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

## Using scratch space

# Submit your job

# Monitor job progress

# Examples

# References

# Future plans
