#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Print commands and their arguments as they are executed
set -x

# Navigate to the application directory
cd /app

# Clean and package the application
./mvnw clean package

# Run the application
java -jar /app/target/monitoring.service-0.0.1-SNAPSHOT.jar