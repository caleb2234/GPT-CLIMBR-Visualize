#!/bin/bash

set -e

ENV=${1:-dev}

echo "Deploying to $ENV environment..."

# Validate environment
if [[ ! "$ENV" =~ ^(dev|prod)$ ]]; then
    echo "Error: Environment must be 'dev' or 'prod'"
    exit 1
fi

# Build and push images
echo "Building Docker images..."
docker build -t climbr-backend:$ENV -f docker/backend.Dockerfile .
docker build -t climbr-frontend:$ENV -f docker/frontend.Dockerfile .

# Tag and push
if [ -n "$DOCKER_REGISTRY" ]; then
    docker tag climbr-backend:$ENV $DOCKER_REGISTRY/climbr-backend:$ENV
    docker tag climbr-frontend:$ENV $DOCKER_REGISTRY/climbr-frontend:$ENV
    docker push $DOCKER_REGISTRY/climbr-backend:$ENV
    docker push $DOCKER_REGISTRY/climbr-frontend:$ENV
fi

# Apply Kubernetes manifests
echo "Applying Kubernetes manifests..."
kubectl apply -k k8s/overlays/$ENV

# Wait for rollout
echo "Waiting for deployment to complete..."
kubectl rollout status deployment/backend -n climbr-viz-$ENV
kubectl rollout status deployment/frontend -n climbr-viz-$ENV

echo "Deployment complete!"
echo "Run 'kubectl get pods -n climbr-viz-$ENV' to check status"