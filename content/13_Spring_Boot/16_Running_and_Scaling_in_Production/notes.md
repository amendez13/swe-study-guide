# Running and Scaling in Production

Run several instances of the same image against a shared database, and let the platform probe, stop, and replace them safely.

## Key points

- Expose only the Actuator endpoints you need; Boot 4 enables the liveness and readiness probes by default.
- Graceful shutdown finishes in-flight requests; give the platform a longer grace period than Boot's timeout.
- Scale-out needs stateless instances; scheduled jobs run once per instance unless guarded.
- Manage the shared schema with Flyway (`spring-boot-starter-flyway` in Boot 4) and backward-compatible migrations.
- Docker Compose runs the app and its database together and can scale app replicas.

## Example

Build the image from the [previous topic](#13_Spring_Boot/15_Executable_Jars_and_Container_Images), save the [Compose file](#13_Spring_Boot/16_Running_and_Scaling_in_Production/concepts/run-the-stack-with-docker-compose) as `compose.yaml`, and start three replicas.

```sh
docker compose up -d --scale app=3
docker compose ps
docker compose logs app | grep Started
```
