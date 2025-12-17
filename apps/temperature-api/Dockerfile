FROM eclipse-temurin:21-jdk AS builder

WORKDIR /app

COPY gradlew ./
COPY gradle gradle
COPY build.gradle* settings.gradle* ./

RUN ./gradlew dependencies --no-daemon || true

COPY src src

RUN ./gradlew clean build --no-daemon

FROM eclipse-temurin:21-jdk

WORKDIR /app

COPY --from=builder /app/build/libs/*.jar app.jar

ENV JAVA_OPTS=""

EXPOSE 8081

ENTRYPOINT ["sh", "-c", "java $JAVA_OPTS -jar app.jar"]
