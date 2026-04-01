#!/bin/bash
# CyberTeam V4 - Deployment Script
# Supports deployment to staging and production environments

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
ENV="${1:-staging}"
VERSION="${2:-latest}"

# Functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

usage() {
    echo "Usage: $0 <environment> [version]"
    echo ""
    echo "Arguments:"
    echo "  environment    Target environment (staging|production)"
    echo "  version        Docker image version (default: latest)"
    echo ""
    echo "Examples:"
    echo "  $0 staging"
    echo "  $0 staging v4.0.0"
    echo "  $0 production v4.0.1"
    exit 1
}

validate_env() {
    if [[ ! "$ENV" =~ ^(staging|production)$ ]]; then
        log_error "Invalid environment: $ENV"
        usage
    fi
}

check_dependencies() {
    log_info "Checking dependencies..."

    local deps=("kubectl" "docker" "jq")
    for dep in "${deps[@]}"; do
        if ! command -v "$dep" &> /dev/null; then
            log_error "Missing dependency: $dep"
            exit 1
        fi
    done
}

load_env_config() {
    log_info "Loading environment configuration for: $ENV"

    local env_file="$PROJECT_ROOT/config/environments/$ENV.yaml"
    if [[ ! -f "$env_file" ]]; then
        log_error "Environment config not found: $env_file"
        exit 1
    fi

    export CYBERTEAM_ENV="$ENV"
    export CYBERTEAM_VERSION="$VERSION"
}

build_image() {
    log_info "Building Docker image..."

    cd "$PROJECT_ROOT"

    docker build -t "cyberteam:$VERSION" \
        --build-arg "VERSION=$VERSION" \
        --build-arg "BUILD_DATE=$(date -u +'%Y-%m-%dT%H:%M:%SZ')" \
        --build-arg "VCS_REF=$(git rev-parse --short HEAD)" \
        .

    log_info "Image built: cyberteam:$VERSION"
}

tag_image() {
    local registry="${1:-ghcr.io/your-org}"
    local image_name="cyberteam"

    log_info "Tagging image for registry: $registry"

    docker tag "cyberteam:$VERSION" "$registry/$image_name:$VERSION"
    docker tag "cyberteam:$VERSION" "$registry/$image_name:latest"

    if [[ "$ENV" == "production" ]]; then
        docker tag "cyberteam:$VERSION" "$registry/$image_name:prod"
    else
        docker tag "cyberteam:$VERSION" "$registry/$image_name:staging"
    fi
}

push_image() {
    local registry="${1:-ghcr.io/your-org}"
    local image_name="cyberteam"

    log_info "Pushing image to registry..."

    docker push "$registry/$image_name:$VERSION"
    docker push "$registry/$image_name:latest"
    docker push "$registry/$image_name:$ENV"
}

deploy_kubernetes() {
    log_info "Deploying to Kubernetes: $ENV"

    local namespace="cyberteam-$ENV"
    local k8s_dir="$PROJECT_ROOT/k8s"

    # Create namespace if not exists
    kubectl create namespace "$namespace" --dry-run=client -o yaml | kubectl apply -f -

    # Apply ConfigMaps and Secrets
    kubectl apply -f "$k8s_dir/configmap.yaml" -n "$namespace"
    kubectl apply -f "$k8s_dir/secret.yaml" -n "$namespace"

    # Update deployment image
    kubectl set image deployment/cyberteam \
        cyberteam="ghcr.io/your-org/cyberteam:$VERSION" \
        -n "$namespace"

    # Wait for rollout
    kubectl rollout status deployment/cyberteam -n "$namespace" --timeout=300s
}

health_check() {
    log_info "Running health checks..."

    local namespace="cyberteam-$ENV"
    local max_retries=30
    local retry=0

    while [[ $retry -lt $max_retries ]]; do
        local ready=$(kubectl get pods -n "$namespace" -l app=cyberteam -o json | jq '.items[].status.conditions[] | select(.type=="Ready") | .status' | grep True | wc -l)

        if [[ $ready -ge 1 ]]; then
            log_info "Health check passed!"
            return 0
        fi

        log_warn "Waiting for pods to be ready... ($((retry + 1))/$max_retries)"
        sleep 5
        ((retry++))
    done

    log_error "Health check failed!"
    return 1
}

rollback() {
    log_warn "Rolling back deployment..."

    local namespace="cyberteam-$ENV"

    kubectl rollout undo deployment/cyberteam -n "$namespace"
    kubectl rollout status deployment/cyberteam -n "$namespace"
}

main() {
    log_info "Starting CyberTeam V4 deployment..."
    log_info "Environment: $ENV"
    log_info "Version: $VERSION"

    validate_env
    check_dependencies
    load_env_config

    # Build workflow
    if [[ "${SKIP_BUILD:-false}" != "true" ]]; then
        build_image
        tag_image
        push_image
    fi

    # Deploy workflow
    deploy_kubernetes

    # Health check
    if ! health_check; then
        rollback
        log_error "Deployment failed and rolled back!"
        exit 1
    fi

    log_info "Deployment completed successfully!"
    log_info "Image: cyberteam:$VERSION"
    log_info "Environment: $ENV"
}

# Run main function
main "$@"
