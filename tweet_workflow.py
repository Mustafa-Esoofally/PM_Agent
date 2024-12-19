from typing import List
from pydantic import BaseModel
from phi.workflow.workflow import Workflow
from phi.agent.agent import Agent
from phi.run.response import RunResponse

class Tweet(BaseModel):
    text: str
    hashtags: List[str]

class TweetList(BaseModel):
    tweets: List[Tweet]

class TweetGeneratorWorkflow(Workflow):
    description: str = "Workflow for generating engaging tweets about the project"

    tweet_agent: Agent = Agent(
        name="Tweet Generator",
        instructions=[
            "Generate engaging tweets about our AI-powered project management tool that:",
            "1. Highlights key features and benefits",
            "2. Uses a professional but engaging tone",
            "3. Includes relevant hashtags",
            "4. Stays within Twitter's character limit",
            "5. Makes the content appealing to both technical and business audiences",
        ],
        response_model=TweetList,
    )

    def run(self) -> RunResponse:
        """Generate tweets about the project"""
        try:
            project_description = """
            Our AI-powered Project Management Assistant:
            - Automatically converts meeting notes into structured tasks
            - Assigns tasks to team members based on their roles and capacity
            - Estimates task complexity and time requirements
            - Sets priorities with clear reasoning
            - Integrates with PostgreSQL for persistent storage
            - Built using phidata framework and OpenAI
            
            Key Benefits:
            - Saves time in task management
            - Ensures nothing from meetings is missed
            - Provides data-driven task estimates
            - Helps balance team workload
            - Makes project planning more efficient
            """

            response = self.tweet_agent.run(
                f"""
                Project Description:
                {project_description}
                
                Please generate 3 engaging tweets about this project.
                Each tweet should focus on different aspects and benefits.
                Include relevant hashtags for tech and business audiences.
                """
            )
            
            if response and response.content:
                return response
            return RunResponse(content=TweetList(tweets=[]))
            
        except Exception as e:
            print(f"Error in workflow: {e}")
            return RunResponse(content=TweetList(tweets=[])) 