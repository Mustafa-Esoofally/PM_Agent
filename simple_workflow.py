from datetime import datetime
from typing import List, Optional, Dict, Literal
from pydantic import BaseModel, Field
from phi.workflow.workflow import Workflow
from phi.agent.agent import Agent
from phi.run.response import RunResponse

# Reuse the models from the main workflow
class TaskPriority(BaseModel):
    level: Literal["Low", "Medium", "High", "Critical"]
    reason: Optional[str] = None

class TaskTimeEstimate(BaseModel):
    minimum_hours: float
    maximum_hours: float
    confidence_level: Literal["Low", "Medium", "High"]
    factors: List[str] = []

class Task(BaseModel):
    task_title: str
    task_description: Optional[str] = None
    task_assignee: Optional[str] = None
    priority: TaskPriority
    time_estimate: TaskTimeEstimate
    complexity: Literal["Simple", "Moderate", "Complex"]
    status: Literal["Not Started", "In Progress", "Blocked", "Ready for Review", "Done"] = "Not Started"

class TaskList(BaseModel):
    tasks: List[Task]

class SimpleProductManagerWorkflow(Workflow):
    description: str = "Simplified workflow for testing task management capabilities"

    task_agent: Agent = Agent(
        name="Task Agent",
        instructions=[
            "Given meeting notes:",
            "1. Generate detailed tasks with clear titles and descriptions",
            "2. Set priorities based on impact and urgency",
            "3. Create time estimates considering task complexity",
            "4. Assign tasks to team members based on their roles",
        ],
        response_model=TaskList,
    )

    def run(self, meeting_notes: str, team_capacity: Dict[str, int]) -> RunResponse:
        """Run the simplified workflow to generate tasks from meeting notes"""
        try:
            # Process meeting notes and generate tasks
            response = self.task_agent.run(
                f"""
                Meeting Notes:
                {meeting_notes}
                
                Team Capacity (hours/week):
                {team_capacity}
                
                Please analyze the meeting notes and generate tasks based on the updates and next steps.
                Consider team capacity when assigning and estimating tasks.
                """
            )
            
            if response and response.content:
                return response
            return RunResponse(content=TaskList(tasks=[]))
            
        except Exception as e:
            print(f"Error in workflow: {e}")
            return RunResponse(content=TaskList(tasks=[])) 