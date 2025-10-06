#!/bin/bash

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
ENV=${1:-dev}
DOCKER_REGISTRY=${DOCKER_REGISTRY:-"your-dockerhub-username"}

echo -e "${GREEN}=== CLIMBR K8s Deployment Script ===${NC}"
echo ""

# Validate environment
if [[ ! "$ENV" =~ ^(dev|prod)$ ]]; then
    echo -e "${RED}Error: Environment must be 'dev' or 'prod'${NC}"
    echo "Usage: $0 <dev|prod>"
    exit 1
fi

# Check if Docker registry is set
if [ "$DOCKER_REGISTRY" == "your-dockerhub-username" ]; then
    echo -e "${YELLOW}Warning: DOCKER_REGISTRY not set. Please set it:${NC}"
    echo "  export DOCKER_REGISTRY=your-dockerhub-username"
    echo ""
    read -p "Enter your Docker Hub username: " DOCKER_REGISTRY
    if [ -z "$DOCKER_REGISTRY" ]; then
        echo -e "${RED}Error: Docker registry is required${NC}"
        exit 1
    fi
fi

echo -e "${GREEN}Deploying to: ${ENV}${NC}"
echo -e "${GREEN}Registry: ${DOCKER_REGISTRY}${NC}"
echo ""

# Ask for confirmation
read -p "Continue with deployment? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Deployment cancelled${NC}"
    exit 0
fi

# Build Docker images
echo -e "${GREEN}Step 1/4: Building Docker images...${NC}"
docker build -t $DOCKER_REGISTRY/climbr-backend:$ENV -f docker/backend.Dockerfile . || {
    echo -e "${RED}Backend build failed${NC}"
    exit 1
}
docker build -t $DOCKER_REGISTRY/climbr-frontend:$ENV -f docker/frontend.Dockerfile . || {
    echo -e "${RED}Frontend build failed${NC}"
    exit 1
}
echo -e "${GREEN}✓ Images built successfully${NC}"
echo ""

# Tag latest for convenience
if [ "$ENV" == "prod" ]; then
    docker tag $DOCKER_REGISTRY/climbr-backend:$ENV $DOCKER_REGISTRY/climbr-backend:latest
    docker tag $DOCKER_REGISTRY/climbr-frontend:$ENV $DOCKER_REGISTRY/climbr-frontend:latest
fi

# Push to registry
echo -e "${GREEN}Step 2/4: Pushing images to registry...${NC}"
docker push $DOCKER_REGISTRY/climbr-backend:$ENV || {
    echo -e "${RED}Backend push failed. Did you run 'docker login'?${NC}"
    exit 1
}
docker push $DOCKER_REGISTRY/climbr-frontend:$ENV || {
    echo -e "${RED}Frontend push failed${NC}"
    exit 1
}

if [ "$ENV" == "prod" ]; then
    docker push $DOCKER_REGISTRY/climbr-backend:latest
    docker push $DOCKER_REGISTRY/climbr-frontend:latest
fi
echo -e "${GREEN}✓ Images pushed successfully${NC}"
echo ""

# Check kubectl access
echo -e "${GREEN}Step 3/4: Verifying kubectl access...${NC}"
kubectl cluster-info > /dev/null 2>&1 || {
    echo -e "${RED}Cannot connect to Kubernetes cluster${NC}"
    echo "Make sure kubectl is configured correctly"
    exit 1
}
echo -e "${GREEN}✓ kubectl configured${NC}"
echo ""

# Apply Kubernetes manifests
echo -e "${GREEN}Step 4/4: Applying Kubernetes manifests...${NC}"
kubectl apply -k k8s/overlays/$ENV || {
    echo -e "${RED}Failed to apply manifests${NC}"
    exit 1
}
echo -e "${GREEN}✓ Manifests applied${NC}"
echo ""

# Determine namespace
if [ "$ENV" == "dev" ]; then
    NAMESPACE="climbr-viz-dev"
else
    NAMESPACE="climbr-viz"
fi

# Wait for rollout
echo -e "${GREEN}Waiting for deployment to complete...${NC}"
kubectl rollout status deployment/dev-backend -n $NAMESPACE --timeout=5m || {
    echo -e "${YELLOW}Backend rollout status check failed (may still be deploying)${NC}"
}
kubectl rollout status deployment/dev-frontend -n $NAMESPACE --timeout=5m || {
    echo -e "${YELLOW}Frontend rollout status check failed (may still be deploying)${NC}"
}
echo ""

# Show deployment info
echo -e "${GREEN}=== Deployment Complete ===${NC}"
echo ""
echo "Namespace: $NAMESPACE"
echo ""
echo "Pods:"
kubectl get pods -n $NAMESPACE
echo ""
echo "Services:"
kubectl get svc -n $NAMESPACE
echo ""

# Access instructions
if [ "$ENV" == "dev" ]; then
    echo -e "${GREEN}Access your application:${NC}"
    echo "  NodePort: http://<NODE-IP>:30080"
    echo "  Port-forward: kubectl port-forward svc/dev-frontend-service 8080:80 -n $NAMESPACE"
    echo "  Minikube: minikube service dev-frontend-service -n $NAMESPACE"
else
    echo -e "${GREEN}Access your application:${NC}"
    echo "  Run: kubectl get svc prod-frontend-service -n $NAMESPACE"
    echo "  Visit the EXTERNAL-IP shown (may take 1-2 minutes to provision)"
    echo "  Or use port-forward: kubectl port-forward svc/prod-frontend-service 8080:80 -n $NAMESPACE"
fi

echo ""
echo -e "${GREEN}Useful commands:${NC}"
echo "  View logs: kubectl logs -f deployment/$ENV-backend -n $NAMESPACE"
echo "  Scale up: kubectl scale deployment/$ENV-backend --replicas=5 -n $NAMESPACE"
echo "  Delete: kubectl delete -k k8s/overlays/$ENV"
echo ""
echo -e "${GREEN}Done! 🚀${NC}"
