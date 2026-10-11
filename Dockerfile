FROM python:3.11-slim

WORKDIR /app

COPY src/ ./src/

RUN pip install --no-cache-dir \
    crewai \
    boto3 \
    bedrock-agentcore \
    python-dotenv \
    google-search-results \
    && pip install --no-cache-dir --no-deps crewai-tools

ENV PYTHONPATH=/app/src
ENV MODEL=bedrock/us.amazon.nova-micro-v1:0
ENV OPENAI_API_KEY=NA

ENTRYPOINT ["python", "src/vacation_planner/crew.py"]
