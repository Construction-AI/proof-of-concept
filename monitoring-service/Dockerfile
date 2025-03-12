FROM openjdk:17-jdk-slim
WORKDIR /app

# Copy maven executable to the image
COPY . .

# Build all the dependencies in preparation to go offline. 
# This is a separate step so the dependencies will be cached unless 
# the pom.xml file has changed.
# RUN ./mvnw dependency:go-offline -B

# RUN ./mvnw package -DskipTests

# RUN mkdir -p target/dependency && (cd target/dependency; jar -xf ../*.jar)

CMD [ "sleep", "infinity" ]