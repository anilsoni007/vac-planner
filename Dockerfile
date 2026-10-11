FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml README.md ./
COPY src/ ./src/

RUN pip install --no-cache-dir .

ENV PYTHONPATH=/app/src
ENV MODEL=bedrock/us.amazon.nova-micro-v1:0
ENV OPENAI_API_KEY=NA

EXPOSE 8080

CMD ["python", "-m", "vacation_planner.crew"]
