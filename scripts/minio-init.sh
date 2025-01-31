#!/bin/sh
# minio-init.sh

# Wait for MinIO to be ready
echo "Waiting for MinIO to be ready..."
sleep 10

# Create bucket using mc (MinIO Client)
mc alias set myminio http://minio:9000 minioadmin minioadmin
mc mb myminio/logs --ignore-existing

echo "MinIO bucket 'logs' created successfully"