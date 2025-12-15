# =========================
# Stage 1: build
# =========================
FROM eclipse-temurin:21-jdk AS builder
ENV LOGIN=zvirrp, PASS=LtGw23ercV12345&

WORKDIR /app

# Копируем только файлы, необходимые для резолва зависимостей
# (улучшает кеширование слоёв)
COPY gradlew ./
COPY gradle gradle
COPY build.gradle* settings.gradle* ./

# Делаем gradlew исполняемым
#USER root
#RUN chmod +x gradlew

# Прогреваем зависимости
RUN ./gradlew dependencies --no-daemon || true
# Копируем исходники
COPY src src

# Собираем fat jar
RUN ./gradlew clean build --no-daemon

# =========================
# Stage 2: runtime
# =========================
FROM eclipse-temurin:21-jdk

WORKDIR /app

COPY --from=builder /app/build/libs/*.jar app.jar

ENV JAVA_OPTS=""

EXPOSE 8081

ENTRYPOINT ["sh", "-c", "java $JAVA_OPTS -jar app.jar"]
