# Use a base image with OpenJDK 17
FROM openjdk:17-jdk-slim AS build

# Set the working directory inside the container
WORKDIR /app

# Copy the Gradle wrapper and necessary files
COPY . .

# Build the project with Gradle (use Gradle wrapper)
RUN ./gradlew build -x test

# Final runtime image
FROM openjdk:17-jdk-slim

# Set the working directory inside the container
WORKDIR /app

# Ensure the JAR is built at runtime
CMD ["./gradlew", "bootRun"]
