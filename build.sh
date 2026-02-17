#!/bin/bash
# Fabric Docker Build Script
# Builds all Docker images for Fabric services

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

print_header() {
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}  Fabric Docker Build${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

print_step() {
    echo -e "\n${GREEN}➜${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

# Validate Dockerfiles exist
validate_dockerfiles() {
    print_step "Validating Dockerfiles..."
    
    local files=(
        "Dockerfile.api"
        "Dockerfile.svelte"
        "../fabric-streamlit/Dockerfile"
    )
    
    for file in "${files[@]}"; do
        if [ ! -f "$file" ]; then
            print_error "Missing: $file"
            exit 1
        else
            print_success "Found: $file"
        fi
    done
}

# Check if .env file exists
check_env_file() {
    print_step "Checking environment configuration..."
    
    if [ ! -f ".env" ]; then
        print_warning ".env file not found"
        echo "  Creating from .env.example..."
        if [ -f ".env.example" ]; then
            cp .env.example .env
            print_success "Created .env from template"
            print_warning "⚠ Please edit .env and add your API keys before starting services!"
        else
            print_error ".env.example not found"
            exit 1
        fi
    else
        print_success ".env file exists"
    fi
}

# Build images
build_images() {
    print_step "Building Docker images..."
    
    echo -e "\n${YELLOW}Building Fabric API...${NC}"
    docker build -t fabric-api:latest -f Dockerfile.api . || {
        print_error "Failed to build fabric-api"
        exit 1
    }
    print_success "fabric-api built successfully"
    
    echo -e "\n${YELLOW}Building Svelte UI...${NC}"
    docker build -t fabric-web-svelte:latest -f Dockerfile.svelte . || {
        print_error "Failed to build fabric-web-svelte"
        exit 1
    }
    print_success "fabric-web-svelte built successfully"
    
    echo -e "\n${YELLOW}Building Streamlit UI...${NC}"
    docker build -t fabric-web-streamlit:latest -f Dockerfile ../fabric-streamlit || {
        print_error "Failed to build fabric-web-streamlit"
        exit 1
    }
    print_success "fabric-web-streamlit built successfully"
}

# List built images
list_images() {
    print_step "Built images:"
    docker images | grep -E "fabric-(api|web-svelte|web-streamlit)" || echo "No images found"
}

# Main execution
main() {
    print_header
    
    # Change to script directory
    cd "$(dirname "$0")"
    
    # Run validation steps
    validate_dockerfiles
    check_env_file
    
    # Build images
    build_images
    
    # Show results
    list_images
    
    echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    print_success "Build completed successfully!"
    echo -e "\n${YELLOW}Next steps:${NC}"
    echo "  1. Edit .env file with your API keys (if not done already)"
    echo "  2. Run: docker-compose up -d"
    echo "  3. Access services:"
    echo "     • Svelte UI:    http://localhost:5173"
    echo "     • Streamlit UI: http://localhost:8501"
    echo "     • API:          http://localhost:8080"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"
}

# Run main function
main
