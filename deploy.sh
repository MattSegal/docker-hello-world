#!/bin/bash
set -e
. ~/venv/bin/activate
if [[ $# -ne 1 ]]; then
    echo "ERROR: Expecting 1 command line argument."
    exit 1
fi

echo "Attempting to retag $1 with deploy..."
MANIFEST=$(aws ecr batch-get-image \
    --profile personal \
    --region ap-southeast-2 \
    --repository-name reddit \
    --image-ids imageTag=$1 \
    --query images[].imageManifest \
    --output text)

aws ecr put-image \
    --profile personal \
    --region ap-southeast-2 \
    --repository-name reddit \
    --image-tag deploy \
    --image-manifest "$MANIFEST" \
    1> /dev/null

aws ecr describe-images \
    --profile personal \
    --region ap-southeast-2 \
    --repository-name reddit \
    --image-ids imageTag=deploy

CLUSTER_NAME='matt-ecs'
SERVICE_NAME='reddit'

echo "Deploying... [cluster:$CLUSTER_NAME] [service:$SERVICE_NAME]"
ecs deploy \
    --profile personal \
    --region ap-southeast-2 \
    --diff \
    --timeout 600 \
    $CLUSTER_NAME $SERVICE_NAME

deactivate
