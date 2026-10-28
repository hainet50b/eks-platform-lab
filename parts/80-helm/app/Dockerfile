FROM eclipse-temurin:25.0.4.1_1-jdk-resolute AS build
WORKDIR /src
COPY .mvn/ .mvn/
COPY mvnw pom.xml ./
RUN ./mvnw -q dependency:go-offline
COPY src/ src/
RUN ./mvnw -q package -DskipTests \
 && java -Djarmode=tools -jar target/spring-boot-0.0.1.jar \
    extract --layers --launcher --destination /layers

FROM eclipse-temurin:25.0.4.1_1-jre-resolute
WORKDIR /app
COPY --from=build /layers/dependencies/ ./
COPY --from=build /layers/spring-boot-loader/ ./
COPY --from=build /layers/snapshot-dependencies/ ./
COPY --from=build /layers/application/ ./
USER 10001:10001
EXPOSE 8080 8081
ENTRYPOINT ["java", "org.springframework.boot.loader.launch.JarLauncher"]
