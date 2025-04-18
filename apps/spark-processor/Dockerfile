# apps/spark-processor/Dockerfile
FROM bitnami/spark:3.3.0

USER root

# Set working directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ .

# Add Kafka connector JAR
ENV SPARK_EXTRA_JARS_DIR=/opt/bitnami/spark/jars/
ENV SPARK_EXTRA_CLASSPATH=/opt/bitnami/spark/jars/*

# Command to run when container starts
CMD ["spark-submit", "--packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.0", "--master", "local[*]", "processor.py"]
