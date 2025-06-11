#!/bin/bash

set -e

# CONFIG
PROJECT_ID="journey-ai-462518"
ZONE="us-central1-b"
VM_NAME="journeyai-prod"
REMOTE_PATH="~/journeyai"
ARCHIVE_NAME="journeyai.tar.gz"

echo "📦 Compressing project directory..."
tar --exclude="$ARCHIVE_NAME" -czf $ARCHIVE_NAME .

echo "🚀 Uploading $ARCHIVE_NAME to $VM_NAME..."
gcloud compute scp $ARCHIVE_NAME $VM_NAME:~ \
  --project=$PROJECT_ID \
  --zone=$ZONE

echo "🧹 Cleaning up local archive..."
rm $ARCHIVE_NAME

echo "✅ Done. Now SSH into the VM and run 'deploy_on_vm.sh'"
