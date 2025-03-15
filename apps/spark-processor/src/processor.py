import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, window, sum, avg, count, lit
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, IntegerType, TimestampType


KAFKA_BOOTSTRAP_SERVERS = os.environ.get('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
KAFKA_TOPIC_INPUT = os.environ.get('KAFKA_TOPIC_INPUT', 'events-raw')
KAFKA_TOPIC_OUTPUT = os.environ.get('KAFKA_TOPIC_OUTPUT', 'events-aggregated') 
INTERVAL_SECONDS = int(os.environ.get('INTERVAL_SECONDS', '1'))
CHECKPOINT_LOCATION = os.environ.get('CHECKPOINT_LOCATION', '/tmp/checkpoint')


spark = SparkSession \
        .builder \
        .appName('KafkaStreamProcessor') \
        .config('spark.jars.packages', 'org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0') \
        .config('spark.sql.streaming.checkpointLocation', CHECKPOINT_LOCATION) \
        .getOrCreate()

schema = StructType([
    StructField('timestamp', StringType(), True),
    StructField('product', StringType(), True),
    StructField('price', DoubleType(), True),
    StructField('quantity', IntegerType(), True),
    StructField('country', StringType(), True),
    StructField('transaction_id', StringType(), True),
    ])


def process_stream():
    print(f"Spark reading from Kafka: {KAFKA_BOOTSTRAP_SERVERS} - Topic: {KAFKA_TOPIC_INPUT}")

    # Read from Kafka
    df = spark \
            .readStream \
            .format('kafka') \
            .option('kafka.bootstrap.servers', KAFKA_BOOTSTRAP_SERVERS) \
            .option('subscribe', KAFKA_TOPIC_INPUT) \
            .option('startingOffsets', 'latest') \
            .option('kafka.group.id', 'spark-processor') \
            .option('kafka.auto.commit', 'false') \
            .option('failOnDataLoss', 'false') \
            .load()

    # Parse json value
    parsed_df = df \
            .selectExpr('CAST(VALUE AS STRING)') \
            .select(from_json(col('value'), schema).alias('data')) \
            .select('data.*')

    parsed_df.writeStream \
            .foreachBatch(process_batch) \
            .option('checkpoingLocation', CHECKPOINT_LOCATION) \
            .trigger(processingTime='5 seconds') \
            .start()

    spark.streams.awaitAnyTermination()

def process_batch(batch_df, batch_id):
    print(f"Processing batch: {batch_id}")

    events = batch_df \
            .withColumn('event_timestamp', col('timestamp').cast(TimestampType()))

    aggregated = events \
            .withWatermark('event_timestamp', '10 minutes') \
            .groupBy(
                        window(col('event_timestamp'), '5 minutes'),
                        col('product'),
                        col('country')
            ) \
            .agg(
                    sum('price').alias('total_sales'),
                    avg('price').alias('avg_price'),
                    sum('quantity').alias('total_quantity'),
                    count('transaction_id').alias('num_transactions')
            )

    # Wirte results to Kafka
    write_kafka(aggregated)

def write_kafka(df):
    print(f"Writing results to Kafka: {KAFKA_BOOTSTRAP_SERVERS} - Topic: {KAFKA_TOPIC_OUTPUT}")
    
    result_df = df.selectExpr(
            "CAST(window.start AS STRING) AS window_start",
            "CAST(window.end AS STRING) AS window_end",
            "product",
            "country",
            "total_sales",
            "avg_price",
            "total_quantity",
            "num_transactions",
            "to_json(struct(*)) as value"
        )

    result_df.write \
        .format('kafka') \
        .option('kafka.bootstrap.servers', KAFKA_BOOTSTRAP_SERVERS) \
        .option("topic", KAFKA_TOPIC_OUTPUT) \
        .save()


if __name__ == "__main__":
    process_stream()
    
    
