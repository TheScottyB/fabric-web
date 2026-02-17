#!/bin/bash
# Fabric Web Services Startup Script
# Manages all three Fabric interfaces

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_header() {
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}  Fabric Web Services Manager${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

print_service() {
    echo -e "\n${GREEN}➜${NC} $1"
    echo -e "  ${YELLOW}$2${NC}"
}

check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo -e "  ${YELLOW}⚠ Port $1 already in use${NC}"
        return 1
    fi
    return 0
}

print_header

echo -e "\n${YELLOW}Checking ports...${NC}"
check_port 8080 && echo "  ✓ Port 8080 (API) available"
check_port 5173 && echo "  ✓ Port 5173 (Svelte) available"
check_port 8501 && echo "  ✓ Port 8501 (Streamlit) available"

echo -e "\n${YELLOW}Choose startup mode:${NC}"
echo "  1) Docker Compose (all services)"
echo "  2) Docker Compose with rebuild"
echo "  3) Manual - API + Svelte UI"
echo "  4) Manual - API + Streamlit UI"
echo "  5) Manual - All three services"
echo "  6) Stop all services"
read -p "Enter choice [1-6]: " choice

case $choice in
    1)
        print_service "Starting Docker Compose" "All services in containers"
        cd ~/workspace/fabric-web
        if [ ! -f ".env" ]; then
            echo -e "${YELLOW}⚠ No .env file found. Creating from template...${NC}"
            cp .env.example .env
            echo -e "${YELLOW}⚠ Please edit .env with your API keys before proceeding!${NC}"
            read -p "Press Enter after editing .env to continue..."
        fi
        docker-compose up -d
        echo -e "\n${GREEN}✓ Services started!${NC}"
        echo "  • Svelte UI:    http://localhost:5173"
        echo "  • Streamlit UI: http://localhost:8501"
        echo "  • API:          http://localhost:8080"
        echo -e "\n${YELLOW}View logs:${NC} docker-compose logs -f"
        ;;
    2)
        print_service "Building and Starting Docker Compose" "Rebuild + start all services"
        cd ~/workspace/fabric-web
        if [ ! -f ".env" ]; then
            echo -e "${YELLOW}⚠ No .env file found. Creating from template...${NC}"
            cp .env.example .env
            echo -e "${YELLOW}⚠ Please edit .env with your API keys before proceeding!${NC}"
            read -p "Press Enter after editing .env to continue..."
        fi
        ./build.sh
        docker-compose up -d
        echo -e "\n${GREEN}✓ Services started!${NC}"
        echo "  • Svelte UI:    http://localhost:5173"
        echo "  • Streamlit UI: http://localhost:8501"
        echo "  • API:          http://localhost:8080"
        echo -e "\n${YELLOW}View logs:${NC} docker-compose logs -f"
        ;;
    3)
        print_service "Starting Fabric API" "Backend on port 8080"
        fabric --serve --address :8080 > /tmp/fabric-api.log 2>&1 &
        echo "  PID: $!"
        sleep 2
        
        print_service "Starting Svelte UI" "Frontend on port 5173"
        cd ~/workspace/fabric-web
        npm run dev > /tmp/fabric-svelte.log 2>&1 &
        echo "  PID: $!"
        
        echo -e "\n${GREEN}✓ Services started!${NC}"
        echo "  • Svelte UI: http://localhost:5173"
        echo "  • API:       http://localhost:8080"
        ;;
    4)
        print_service "Starting Fabric API" "Backend on port 8080"
        fabric --serve --address :8080 > /tmp/fabric-api.log 2>&1 &
        echo "  PID: $!"
        sleep 2
        
        print_service "Starting Streamlit UI" "Data viz on port 8501"
        cd ~/workspace/fabric-streamlit
        streamlit run streamlit.py > /tmp/fabric-streamlit.log 2>&1 &
        echo "  PID: $!"
        
        echo -e "\n${GREEN}✓ Services started!${NC}"
        echo "  • Streamlit UI: http://localhost:8501"
        echo "  • API:          http://localhost:8080"
        ;;
    5)
        print_service "Starting Fabric API" "Backend on port 8080"
        fabric --serve --address :8080 > /tmp/fabric-api.log 2>&1 &
        echo "  PID: $!"
        sleep 2
        
        print_service "Starting Svelte UI" "Frontend on port 5173"
        cd ~/workspace/fabric-web
        npm run dev > /tmp/fabric-svelte.log 2>&1 &
        echo "  PID: $!"
        
        print_service "Starting Streamlit UI" "Data viz on port 8501"
        cd ~/workspace/fabric-streamlit
        streamlit run streamlit.py > /tmp/fabric-streamlit.log 2>&1 &
        echo "  PID: $!"
        
        echo -e "\n${GREEN}✓ All services started!${NC}"
        echo "  • Svelte UI:    http://localhost:5173"
        echo "  • Streamlit UI: http://localhost:8501"
        echo "  • API:          http://localhost:8080"
        ;;
    6)
        print_service "Stopping services" "Killing all Fabric processes"
        cd ~/workspace/fabric-web
        docker-compose down 2>/dev/null && echo "  ✓ Stopped Docker containers"
        pkill -f "fabric --serve" 2>/dev/null && echo "  ✓ Stopped API"
        pkill -f "vite dev" 2>/dev/null && echo "  ✓ Stopped Svelte"
        pkill -f "streamlit run" 2>/dev/null && echo "  ✓ Stopped Streamlit"
        echo -e "\n${GREEN}✓ All services stopped${NC}"
        ;;
    *)
        echo -e "${YELLOW}Invalid choice${NC}"
        exit 1
        ;;
esac

echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
