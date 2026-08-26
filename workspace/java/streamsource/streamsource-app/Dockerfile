# Stage 1: Build
FROM maven:3.9-eclipse-temurin-21 AS builder
WORKDIR /app
COPY . .
RUN mvn clean package -DskipTests -pl streamsource-app -am

# Stage 2: Runtime (minimal JRE image)
FROM eclipse-temurin:21-jre-alpine
WORKDIR /app

RUN addgroup -S streamsource && adduser -S streamsource -G streamsource

COPY --from=builder /app/streamsource-app/target/streamsource-app-*.jar app.jar
RUN chown streamsource:streamsource app.jar

USER streamsource
EXPOSE 8080

ENTRYPOINT ["java", \
  "-XX:+UseContainerSupport", \
  "-XX:MaxRAMPercentage=75.0", \
  "-Djava.security.egd=file:/dev/./urandom", \
  "-jar", "app.jar"]
