# Use a base image with OpenJDK 17
FROM openjdk:17-jdk-slim AS build

# Set the working directory inside the container
WORKDIR /app

# Copy the Gradle wrapper and necessary files
COPY . .

# Build the project with Gradle (use Gradle wrapper)
RUN ./gradlew build -x test

# Use a smaller image to run the application
FROM openjdk:17-jdk-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the compiled jar from the build stage
COPY --from=build /app/build/libs/*.jar app.jar

# Expose the port the app runs on
EXPOSE 8080

# Set the entrypoint to run the Spring Boot application
# ENTRYPOINT ["java", "-jar", "/app/app.jar"]

CMD [ "sleep", "infinity" ]
