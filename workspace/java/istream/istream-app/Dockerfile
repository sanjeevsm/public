# Stage 1: Build
FROM maven:3.9-eclipse-temurin-21 AS builder
WORKDIR /app
COPY . .
RUN mvn clean package -DskipTests -pl istream-app -am

# Stage 2: Runtime (minimal JRE image)
FROM eclipse-temurin:21-jre-alpine
WORKDIR /app

RUN addgroup -S istream && adduser -S istream -G istream

COPY --from=builder /app/istream-app/target/istream-app-*.jar app.jar
RUN chown istream:istream app.jar

USER istream
EXPOSE 8080

ENTRYPOINT ["java", \
  "-XX:+UseContainerSupport", \
  "-XX:MaxRAMPercentage=75.0", \
  "-Djava.security.egd=file:/dev/./urandom", \
  "-jar", "app.jar"]
