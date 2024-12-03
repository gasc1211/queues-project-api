#! /bin/bash

# If not done before, log into azure cli and into your container registry 
# az login
# az acr login --name acraccountingsystemdev

AZURE_CONTAINER_REGISTRY="acraccountingsystemdev"
AZURE_CONTAINER_NAME="api-accountingsystem"
CURRENT_VERSION="0.0.3"

docker buildx build --platform linux/amd64 -t $AZURE_CONTAINER_NAME-dev:latest . --load

docker tag $AZURE_CONTAINER_NAME-dev:latest $AZURE_CONTAINER_REGISTRY.azurecr.io/$AZURE_CONTAINER_NAME-dev:latest
docker tag $AZURE_CONTAINER_NAME-dev:latest $AZURE_CONTAINER_REGISTRY.azurecr.io/$AZURE_CONTAINER_NAME-dev:$CURRENT_VERSION

docker push $AZURE_CONTAINER_REGISTRY.azurecr.io/$AZURE_CONTAINER_NAME-dev:latest
docker push $AZURE_CONTAINER_REGISTRY.azurecr.io/$AZURE_CONTAINER_NAME-dev:$CURRENT_VERSION