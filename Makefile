.PHONY: setup venv clean kafka kafka-stop producer spark consumer docker-build docker-up docker-down docker-logs help

# Directory and environment definitions
VENV_DIR := venv
PYTHON := python3
APP_DIRS := apps/data-producer apps/spark-processor apps/data-consumer

# Colors for messages
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[0;33m
NC := \033[0m # No Color

# Help
help:
	@echo "${BLUE}Available commands:${NC}"
	@echo "  ${BLUE}Development Environment:${NC}"
	@echo "  ${GREEN}make setup${NC}        - Set up virtual environment and install all dependencies"
	@echo "  ${GREEN}make venv${NC}         - Create only the virtual environment without installing dependencies"
	@echo "  ${GREEN}make kafka${NC}        - Start Kafka and Zookeeper with Docker Compose"
	@echo "  ${GREEN}make kafka-stop${NC}   - Stop Kafka and Zookeeper containers"
	@echo "  ${GREEN}make producer${NC}     - Run the data producer locally"
	@echo "  ${GREEN}make spark${NC}        - Run the Spark processor locally"
	@echo "  ${GREEN}make consumer${NC}     - Run kafka consumer locally (events-aggregated)"
	@echo "  ${GREEN}make clean${NC}        - Remove virtual environment and temporary files"
	@echo ""
	@echo "  ${BLUE}Docker Commands:${NC}"
	@echo "  ${GREEN}make docker-build${NC} - Build all Docker images for the project"
	@echo "  ${GREEN}make docker-up${NC}    - Start all Docker containers"
	@echo "  ${GREEN}make docker-down${NC}  - Stop all Docker containers"
	@echo "  ${GREEN}make docker-logs${NC}  - Follow logs from all containers"

# Complete setup: virtual environment + dependencies
setup: venv
	@echo "${BLUE}Installing dependencies...${NC}"
	@for dir in $(APP_DIRS); do \
		echo "${YELLOW}Installing dependencies from $${dir}...${NC}"; \
		$(VENV_DIR)/bin/pip install -r $${dir}/requirements.txt; \
	done
	@echo "${GREEN}Environment successfully configured!${NC}"

# Create virtual environment if it doesn't exist
venv:
	@if [ ! -d "$(VENV_DIR)" ]; then \
		echo "${BLUE}Creating virtual environment...${NC}"; \
		$(PYTHON) -m venv $(VENV_DIR); \
		$(VENV_DIR)/bin/pip install --upgrade pip; \
		echo "${GREEN}Virtual environment created in $(VENV_DIR)${NC}"; \
	else \
		echo "${YELLOW}Virtual environment already exists${NC}"; \
	fi

# Start Kafka and Zookeeper
kafka:
	@echo "${BLUE}Starting Kafka and Zookeeper...${NC}"
	docker compose up -d zookeeper kafka kafka-ui
	@echo "${GREEN}Services started. Kafka UI available at http://localhost:8080${NC}"

# Stop Kafka and Zookeeper
kafka-stop:
	@echo "${BLUE}Stopping Kafka and Zookeeper...${NC}"
	docker compose down
	@echo "${GREEN}Services stopped${NC}"

# Run the data producer
producer:
	@echo "${BLUE}Starting the data producer...${NC}"
	@if [ ! -d "$(VENV_DIR)" ]; then \
		echo "${YELLOW}Virtual environment not found. Run 'make setup' first${NC}"; \
		exit 1; \
	fi
	KAFKA_BOOTSTRAP_SERVERS=localhost:29092 \
	KAFKA_TOPIC=events-raw \
	INTERVAL_SECONDS=1 \
	$(VENV_DIR)/bin/python apps/data-producer/src/producer.py

# Run the Spark processor
spark:
	@echo "${BLUE}Starting the Spark processor...${NC}"
	@if [ ! -d "$(VENV_DIR)" ]; then \
		echo "${YELLOW}Virtual environment not found. Run 'make setup' first${NC}"; \
		exit 1; \
	fi
	KAFKA_BOOTSTRAP_SERVERS=localhost:29092 \
	KAFKA_TOPIC_INPUT=events-raw \
	KAFKA_TOPIC_OUTPUT=events-aggregated \
	CHECKPOINT_LOCATION=/tmp/checkpoint \
	$(VENV_DIR)/bin/python apps/spark-processor/src/processor.py

# Run the consumer, read spark processed data from events-aggregated topic
consumer:
	@echo "${BLUE}Starting the kafka consumer...${NC}"
	@if [ ! -d "$(VENV_DIR)" ]; then \
		echo "${YELLOW}Virtual environment not found. Run 'make setup' first${NC}"; \
		exit 1; \
	fi
	KAFKA_BOOTSTRAP_SERVERS=localhost:29092 \
	KAFKA_TOPIC=events-aggregated \
	$(VENV_DIR)/bin/python apps/data-consumer/src/consumer.py

# Build Docker images
docker-build:
	@echo "${BLUE}Building Docker images...${NC}"
	docker compose build
	@echo "${GREEN}Docker images built successfully${NC}"

# Start all services
docker-up:
	@echo "${BLUE}Starting all services...${NC}"
	docker compose up -d
	@echo "${GREEN}All services started. Kafka UI available at http://localhost:8080${NC}"

# Stop all services
docker-down:
	@echo "${BLUE}Stopping all services...${NC}"
	docker compose down
	@echo "${GREEN}All services stopped${NC}"

# Follow logs from all containers
docker-logs:
	@echo "${BLUE}Following logs from all containers...${NC}"
	docker compose logs -f

# Clean environment
clean:
	@echo "${BLUE}Cleaning environment...${NC}"
	@rm -rf $(VENV_DIR)
	@find . -type d -name "__pycache__" -exec rm -rf {} +
	@find . -type f -name "*.pyc" -delete
	@echo "${GREEN}Environment cleaned${NC}"
