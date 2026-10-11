from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import SerperDevTool
from bedrock_agentcore import BedrockAgentCoreApp
from dotenv import load_dotenv
import os


load_dotenv()

serper_api_key = os.environ.get("SERPER_API_KEY")
if not serper_api_key:
	raise RuntimeError("SERPER_API_KEY must be set in the environment or a local .env file.")

serper_dev_tool = SerperDevTool(api_key=serper_api_key)
llm = LLM(model=os.environ.get("MODEL", "bedrock/us.amazon.nova-micro-v1:0"))


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
	if not isinstance(topic, str) or not topic.strip():
		raise ValueError("The 'topic' field must be a non-empty string.")

	result = VacationPlannerCrew().crew().kickoff(inputs={"topic": topic.strip()})
	return {"status": "success", "topic": topic.strip(), "report": str(result)}

if __name__ == "__main__":
	app.run()