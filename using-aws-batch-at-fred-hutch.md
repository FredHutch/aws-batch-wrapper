
<div style="display: none;">
Convert to HTML (and add TOC) with:

./convert-to-html.sh

Then paste the contents of
using-aws-batch-at-fred-hutch.html into the "Edit source" window at https://bit.ly/AWSBatchAtHutch .

</div>


# What is AWS Batch?

From the [website](https://aws.amazon.com/batch/):

> AWS Batch enables developers, scientists, and engineers to easily and efficiently run hundreds of thousands of batch computing jobs on AWS. AWS Batch dynamically provisions the optimal quantity and type of compute resources (e.g., CPU or memory optimized instances) based on the volume and specific resource requirements of the batch jobs submitted. With AWS Batch, there is no need to install and manage batch computing software or server clusters that you use to run your jobs, allowing you to focus on analyzing results and solving problems. AWS Batch plans, schedules, and executes your batch computing workloads across the full range of AWS compute services and features, such as Amazon EC2 and Spot Instances.

AWS Batch uses AWS [EC2 Container Service](https://aws.amazon.com/ecs/) (ECS), meaning your job must be configured as a [Docker](https://www.docker.com/)
container.

## How do I use AWS Batch?

SciComp provides access to AWS Batch in two ways:

* Via the [AWS Command Line Interface (CLI)](https://aws.amazon.com/cli/)
* Via programmatic interfaces such as Python's [boto3](https://boto3.readthedocs.io/en/latest/reference/core/boto3.html). The
  earlier version of this library (`boto`) is deprecated and should not be used.

Console (web/GUI) access to AWS batch is not available to end users at the Center.


# Request access

You don't have access to AWS Batch by default.

Request access by emailing **scicomp@fredhutch.org** with the subject
line **Request Access to AWS Batch**.

In your email, **include** the name of your PI.

SciComp will contact you when your access has been granted.


<div style="display: none;">
scicomp people:

The way to onboard a new user is to do the following:

```
. /app/local/aws-batch-wrapper/env/bin/activate # start virtual env
/app/local/aws-batch-wrapper/onboarding.py # show help message
# For a user with HutchNet ID jblow and PI name peters-u, run:
/app/local/aws-batch-wrapper/onboarding.py jblow peters-u
```

This requires some special permissions, you probably need to
authenticate your command-line session with MFA.

</div>


# Create a Docker image


## Do you need to create your own image?

It depends on what you want to do. If you are using software that is
readily available, there is probably already a Docker image containing
that software. Look around on [Docker Hub](https://hub.docker.com/) to see
if there's already a Docker image available.

The SciComp group is also developing Docker images that contain much
of the software you are used to finding in `/app` on the `rhino`
machines and `gizmo`/`beagle` clusters.

If you've found an existing Docker image that meets your needs, you don't
need to read the rest of this section.


## Getting Started

It's recommended (but not required) that you install
[Docker](https://www.docker.com/) on your workstation (laptop or desktop)
and develop your image on your own machine until it's ready to be deployed.

## Docker Installation Instructions

* [Windows](https://www.docker.com/docker-windows)
* [Mac](https://www.docker.com/docker-mac)
* [Ubuntu Linux](https://www.docker.com/docker-ubuntu)

## Deploy Docker Image

### Create GitHub Account

### Create a Docker Hub Account

### Push your Dockerfile to a GitHub repository

### Create an Automated Build in Docker Hub

# Create a Job Definition

[Job Definitions](https://docs.aws.amazon.com/batch/latest/userguide/job_definitions.html) specify how jobs are to be run. Some of the attributes specified in a job definition include:

* Which Docker image to use with the container in your job
* How many vCPUs and how much memory to use with the container
* The command the container should run when it is started †
* What (if any) environment variables should be passed to the container when it starts †
* Any data volumes that should be used with the container (the compute
  environments provided by SciComp include 1TB of scratch space available
  at `/scratch`).
* What (if any) IAM role your job should use for AWS permissions. This
  is important if your job requires permission to access your PIs
  [S3](https://aws.amazon.com/s3/) bucket.

† = these items can be overridden in individual job submissions.

A custom script is available to generate a job definition template with
Center-specific sections already filled in. The script is called
`get_jobdef_skeleton` and is available on the `rhino` machines.

This script requires that you supply the name of your PI in the format:
lastname + dash + first initial. So if your PI is Jane Doe, you would run
the script as follows:

```
get_jobdef_skeleton -p doe-j > jobdef.json
```

The file `jobdef.json` now contains a partial job definition with the following
information already filled in:

* Mount points and volumes necessary to make available 1TB of scratch
  space in the directory `/scratch`. You are responsible for making sure your
  scripts process all large files in this directory.
* A Job Role which grants your jobs permissions to access your PI's S3 bucket.

Before you can use this file, **you will need to edit it** to fill in
or replace the following values:

* `command`(optional) The command to run when a job starts. This
  can be overridden when submitting a job.
* `environment` (optional) A set of environment variables to pass
  to the containers running your job. Can be overridden when submitting
  a job.
* `memory` The amount of memory (in megabytes) your jobs will need. Defaults
  to 2000 (2GB).
* `vcpus` The number of CPU cores your job will need. Defaults to 1. You
  should only change this if you know that your job code is explicitly
  parallelized (that is, it uses more than one core).



# Using secrets in jobs

# Using scratch space

If you use a job definition as generated by the
[get_jobdef_skeleton](#create-a-job-definition) script, the container
running your job will have 1TB of writable scratch space available
in the `/scratch` directory. You are responsible for ensuring that all
large files generated in your job will live in this directory; if you
write them elsewhere, you'll run out of space very quickly.

Scratch space is ephemeral; any results you want to keep should be copied
to S3.

# Using S3 in jobs

The Center's policies require that all of our `S3` buckets be encrypted.
When copying files to or from `S3`, be sure to use the
`--sse AES256` flag in the AWS CLI, or pass the parameter
`ServerSideEncryption='AES256'` if using `boto3`.

If you don't set this flag, you will get cryptic, counterintuitive
error messages (such as `Access Denied`).

# Submit your job

# Monitor job progress

# Examples

## Using fetch-and-run

## Using a script baked-in to a Docker image

# References

# Future plans

# Questions or Comments

Please direct all questions and feedback to **scicomp@fredhutch.org**.
