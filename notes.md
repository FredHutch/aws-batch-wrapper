## notes on how batch permissions are set up and how to re-create them going forward


### old system:

#### group:

fh-fredricks-d-batch (members: dtenenba, sminot)

has two policies:

* AWSBatchFullAccess (aws) - replace this with fh-pi-end-user-batch-access
* fh-pi-fredricks-d-passrole (custom) this allows iam:PassRole on the following roles:
  *  fh-fredricks-d-batch
  *  fh-pi-fredricks-d-batchrole
  *  fh-pi-fredricks-d-batchservice
  *  fh-pi-fredricks-d-batchtask


#### roles:

 fh-fredricks-d-batch

  has 2 policies:

*    fh_ECS_forBatch (custom)
*    AWSOpsWorksCloudWatchLogs (aws)

  fh-pi-fredricks-d-batchrole

  has 2 policies:

  *    fh-pi-fredricks-d-ecs-access
  *    fh-pi-fredricks-d-bucket-access

   fh-pi-fredricks-d-batchservice
    has 1 policy:

*      fh-pi-fredricks-d-ecs-access

   fh-pi-fredricks-d-batchtask
    has 1 policy:

*      fh-pi-fredricks-d-bucket-access




### New system

given username and pinam-e, assert that username is in pinam-e group.


end user needs
*      limited set of aws batch permissions

make sure pi has a role called

  fh-pi-pinam-e-batchtask

with policy (which should already exist):

  fh-pi-pinam-e-bucket-access

if this role does not exist, create it
