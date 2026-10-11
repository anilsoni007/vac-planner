FROM --platform=linux/arm64 ghcr.io/astral-sh/uv:python3.11-bookworm-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN --mount=type=cache,target=/root/.cache/uv \
    uv pip install --system -r requirements.txt

COPY src/ ./src/
COPY pyproject.toml ./

ENV PYTHONPATH=/app/src
ENV MODEL=bedrock/us.amazon.nova-micro-v1:0
ENV OPENAI_API_KEY=NA

ENV OTEL_SERVICE_NAME=vacation_planner_agent
ENV OTEL_TRACES_EXPORTER=otlp
ENV OTEL_METRICS_EXPORTER=otlp
ENV OTEL_PYTHON_DISTRO=aws_distro
ENV OTEL_PYTHON_CONFIGURATOR=aws_configurator
ENV OTEL_EXPORTER_OTLP_PROTOCOL=http/protobuf
ENV AGENT_OBSERVABILITY_ENABLED=true
ENV OTEL_TRACES_SAMPLER=always_on
ENV OTEL_RESOURCE_ATTRIBUTES=service.namespace=AgentCore,service.version=1.0

EXPOSE 8080

CMD ["opentelemetry-instrument", "python", "-m", "vacation_planner.crew"]
