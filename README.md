# VacationPlanner Crew

Welcome to the VacationPlanner Crew project, powered by [crewAI](https://crewai.com). This template is designed to help you set up a multi-agent AI system with ease, leveraging the powerful and flexible framework provided by crewAI. Our goal is to enable your agents to collaborate effectively on complex tasks, maximizing their collective intelligence and capabilities.

## Installation

Ensure you have Python >=3.10 <=3.13 installed on your system. This project uses [Poetry](https://python-poetry.org/) for dependency management and package handling, offering a seamless setup and execution experience.

First, if you haven't already, install Poetry:

```bash
pip install poetry
```

Next, navigate to your project directory and install the dependencies:

1. First lock the dependencies and then install them:
```bash
poetry lock
```
```bash
poetry install
```
### Customizing

**Add your `OPENAI_API_KEY` into the `.env` file**

- Modify `src/vacation_planner/config/agents.yaml` to define your agents
- Modify `src/vacation_planner/config/tasks.yaml` to define your tasks
- Modify `src/vacation_planner/crew.py` to add your own logic, tools and specific args
- Modify `src/vacation_planner/main.py` to add custom inputs for your agents and tasks

## Running the Project

To kickstart your crew of AI agents and begin task execution, run this from the root folder of your project:

```bash
poetry run vacation_planner
```

This command initializes the vacation_planner Crew, assembling the agents and assigning them tasks as defined in your configuration.

This example, unmodified, will run the create a `report.md` file with the output of a research on LLMs in the root folder.

## Running and testing the AgentCore container

The container exposes the AgentCore invocation API on port `8080`. It does not serve a website at `/`; send a `POST` request to `/invocations` to run the vacation planner. Docker requires a Serper API key and AWS credentials that can invoke Amazon Bedrock. Keep the Serper key in a local `.env` file; `.dockerignore` prevents that file from being included in the image build.

```env
SERPER_API_KEY=your-serper-api-key
AWS_DEFAULT_REGION=us-west-2
```

### Test locally

From the `vacation_planner` project directory, build the image:

```powershell
docker build -t vacation-planner:latest .
```

Run the container. For AWS SSO credentials in Windows PowerShell, sign in first and mount your AWS config:

```powershell
aws sso login --profile default
docker run --rm --name vacation-planner -p 8080:8080 --env-file .env -v "$HOME\.aws:/root/.aws:ro" -e AWS_PROFILE=default vacation-planner:latest
```

Alternatively, provide credentials through environment variables or another standard AWS credential source, and omit the profile mount and `AWS_PROFILE` setting. Do not bake AWS credentials into the image.

In a second terminal, invoke the local endpoint with `curl`:

```bash
curl -X POST http://localhost:8080/invocations \
  -H "Content-Type: application/json" \
  -d '{"topic":"Paris"}'
```

### Build and test on an EC2 instance

Pull the code and, from the project directory on EC2, build and run the container. The Dockerfile targets ARM64 for AgentCore. On an ARM64 EC2 instance, use the commands below; on an x86_64 host, use the Buildx cross-build instructions in the next section. The EC2 instance should have an IAM role with permission to invoke the configured Bedrock model. Put the Serper key and region in `.env`; do not put AWS credentials there when using the instance role.

```bash
git pull
docker build -t vacation-planner:latest .
docker run --rm --name vacation-planner -p 8080:8080 --env-file .env vacation-planner:latest
```

From the EC2 instance, test with:

```bash
curl -X POST http://localhost:8080/invocations \
  -H "Content-Type: application/json" \
  -d '{"topic":"Paris"}'
```

To send the request from your own computer, allow inbound TCP port `8080` in the EC2 security group, preferably restricted to your IP, then use the EC2 public IP:

```bash
curl -X POST http://EC2_PUBLIC_IP:8080/invocations \
  -H "Content-Type: application/json" \
  -d '{"topic":"Paris"}'
```

The request requires working AWS Bedrock access and a valid Serper key. For a deployed AgentCore runtime, attach an execution role with the required Bedrock permissions and configure `SERPER_API_KEY` as a runtime secret/environment variable.

The Docker image installs the pinned runtime dependencies in `requirements.txt` and starts the AgentCore app with AWS OpenTelemetry auto-instrumentation. CrewAI is pinned to `1.15.27`, matching `pyproject.toml` and the AWS CrewAI instrumentation's supported `>=1.10,<2` range; older CrewAI releases can emit incompatible event shapes and break invocations. The image sets `AGENT_OBSERVABILITY_ENABLED=true`, exports traces and metrics over OTLP HTTP/protobuf, and identifies the service as `vacation_planner_agent`. It also disables CrewAI's own telemetry to avoid duplicate instrumentation and redacts prompt, response, and tool content from exported spans. Configure the AgentCore runtime's observability destination and execution-role permissions in AWS so the runtime can receive and publish telemetry.

### Build and push an ARM64 image for AgentCore

AgentCore requires an ARM64 container image. Build and push the image for `linux/arm64`, even if your Docker host is an x86_64 machine. Set `ECR_IMAGE` to your ECR repository URI and ensure the repository exists:

On an x86_64 EC2 host, first register ARM64 emulation and create a Buildx builder that can use it. These setup commands require permission to run a privileged container. If you already created the builder, use `docker buildx use vacation-planner-arm64` instead of creating it again.

```bash
docker run --privileged --rm tonistiigi/binfmt --install arm64
docker buildx create --name vacation-planner-arm64 --driver docker-container --use
docker buildx inspect --bootstrap
```

Check that the builder reports `linux/arm64` under its supported platforms. Then log in to ECR and build/push:

```bash
export AWS_REGION=us-west-2
export ECR_IMAGE=211125418300.dkr.ecr.us-west-2.amazonaws.com/vacation-planner:latest

aws ecr get-login-password --region "$AWS_REGION" \
  | docker login --username AWS --password-stdin 211125418300.dkr.ecr.us-west-2.amazonaws.com

docker buildx build --platform linux/arm64 \
  -t "$ECR_IMAGE" \
  --push .
```

Confirm the image published to ECR supports ARM64 before using that URI when creating the AgentCore runtime:

```bash
docker buildx imagetools inspect "$ECR_IMAGE"
```

The output should list `linux/arm64`. Rebuild and push the image after code changes; AgentCore must be configured with the ECR URI of that ARM64 image.

## Understanding Your Crew

The vacation_planner Crew is composed of multiple AI agents, each with unique roles, goals, and tools. These agents collaborate on a series of tasks, defined in `config/tasks.yaml`, leveraging their collective skills to achieve complex objectives. The `config/agents.yaml` file outlines the capabilities and configurations of each agent in your crew.

## Support

For support, questions, or feedback regarding the VacationPlanner Crew or crewAI.
- Visit our [documentation](https://docs.crewai.com)
- Reach out to us through our [GitHub repository](https://github.com/joaomdmoura/crewai)
- [Join our Discord](https://discord.com/invite/X4JWnZnxPb)
- [Chat with our docs](https://chatg.pt/DWjSBZn)

Let's create wonders together with the power and simplicity of crewAI.
