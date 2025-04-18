# Real-Time Data Streaming Pipeline

A scalable, containerized data streaming pipeline built with Apache Kafka, Apache Spark, and deployed with Docker. This project demonstrates a complete end-to-end data processing workflow from data generation to real-time processing and analytics.

## Architecture

The pipeline consists of the following components:

- **Data Producer**: Generates simulated sales data and sends it to Kafka
- **Apache Kafka**: Message broker that handles the data streams
- **Spark Processor**: Processes the data streams in real-time using Spark Structured Streaming
- **Data Consumer**: Consumes the processed data (optional component)
- **Kafka UI**: Web interface for monitoring Kafka topics and messages

## Prerequisites

- Docker and Docker Compose
- Make (for using the Makefile commands)
- Git
- Python 3.9+ (for local development)

## Getting Started

### Clone the Repository

```bash
git clone https://github.com/fjasensi/data-streaming-pipeline.git
cd data-streaming-pipeline
```

### Setup Options

You have two options to run this project:

1. **Using Docker (recommended)**: Run all components in containers
2. **Local Development**: Run Kafka in Docker, but the applications locally

### Option 1: Running with Docker

Build and start all services with Docker:

```bash
# Build all Docker images
make docker-build

# Start all services
make docker-up

# Follow the logs (optional)
make docker-logs
```

### Option 2: Local Development

1. Set up a virtual environment and install dependencies:

```bash
# Create virtual environment and install dependencies
make setup
```

2. Start Kafka and Zookeeper:

```bash
# Start Kafka, Zookeeper, and Kafka UI
make kafka
```

3. Run the components:

```bash
# In separate terminal windows:

# Run the data producer
make producer

# Run the Spark processor
make spark

# Run the data consumer (optional)
make consumer
```

## Data Flow

1. The data producer generates simulated sales events and sends them to the `events-raw` Kafka topic
2. The Spark processor consumes from `events-raw`, processes the data (aggregations, transformations, etc.), and outputs to the `events-aggregated` topic
3. The data consumer reads from the `events-aggregated` topic (optional)

## Available Make Commands

### Docker Commands

- `make docker-build` - Build all Docker images
- `make docker-up` - Start all Docker containers
- `make docker-down` - Stop all Docker containers
- `make docker-logs` - Follow logs from all containers

### Local Development Commands

- `make setup` - Set up virtual environment and install dependencies
- `make venv` - Create only the virtual environment
- `make kafka` - Start Kafka and Zookeeper
- `make kafka-stop` - Stop Kafka and Zookeeper
- `make producer` - Run the data producer locally
- `make spark` - Run the Spark processor locally
- `make consumer` - Run the data consumer locally
- `make clean` - Remove virtual environment and temporary files

## Monitoring and Management

- **Kafka UI**: Access the web interface at http://localhost:8080
  - View topics and messages
  - Monitor broker status
  - Create topics and more

## Extending the Project

### Scaling with Kubernetes

For production deployment, the next step would be to:

1. Create Kubernetes manifests for each service
2. Use Terraform to provision the infrastructure
3. Set up a CI/CD pipeline with GitHub Actions

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Apache Kafka and Apache Spark communities
- Confluent for Kafka Docker images
- Bitnami for Spark Docker images
