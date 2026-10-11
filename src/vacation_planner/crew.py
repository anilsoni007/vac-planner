from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import SerperDevTool
from bedrock_agentcore import BedrockAgentCoreApp
import os
import boto3


# Use SSO profile credentials directly
_session = boto3.Session(profile_name="default")
_creds = _session.get_credentials().get_frozen_credentials()
os.environ["AWS_ACCESS_KEY_ID"] = _creds.access_key
os.environ["AWS_SECRET_ACCESS_KEY"] = _creds.secret_key
os.environ["AWS_SESSION_TOKEN"] = _creds.token or ""
os.environ["AWS_DEFAULT_REGION"] = "us-west-2"

serper_dev_tool = SerperDevTool(api_key=os.environ.get("SERPER_API_KEY"))
llm = LLM(model=os.environ.get("MODEL"))


# Uncomment the following line to use an example of a custom tool
# from vacation_planner.tools.custom_tool import MyCustomTool

# Check our tools documentations for more information on how to use them
# from crewai_tools import SerperDevTool

@CrewBase
class VacationPlannerCrew():
	"""VacationPlanner crew"""
	agents_config = 'config/agents.yaml'
	tasks_config = 'config/tasks.yaml'

	@agent
	def vacation_researcher(self) -> Agent:
		return Agent(
			config=self.agents_config['vacation_researcher'],
			tools=[serper_dev_tool],
			llm=llm,
			verbose=True
		)

	@agent
	def itinerary_planner(self) -> Agent:
		return Agent(
			config=self.agents_config['itinerary_planner'],
			llm=llm,
			verbose=True
		)

	@task
	def research_task(self) -> Task:
		return Task(
			config=self.tasks_config['research_task'],
			agent=self.vacation_researcher()
		)

	@task
	def reporting_task(self) -> Task:
		return Task(
			config=self.tasks_config['reporting_task'],
			agent=self.itinerary_planner(),
			output_file='report.md'
		)

	@crew
	def crew(self) -> Crew:
		"""Creates the VacationPlanner crew"""
		return Crew(
			agents=self.agents,
			tasks=self.tasks,
			process=Process.sequential,
			verbose=True,
		)


# AgentCore runtime - invoke via Bedrock AgentCore API with {"topic": "Paris"}
app = BedrockAgentCoreApp()

@app.entrypoint
def invoke(payload: dict) -> dict:
	topic = payload.get("topic", "Paris")
	VacationPlannerCrew().crew().kickoff(inputs={"topic": topic})
	report_content = ""
	if os.path.exists("report.md"):
		with open("report.md", "r", encoding="utf-8") as f:
			report_content = f.read()
	return {"status": "success", "topic": topic, "report": report_content}

if __name__ == "__main__":
	app.run()