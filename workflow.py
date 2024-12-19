import os
from datetime import datetime
from typing import List, Optional, Dict, Literal
from pydantic import BaseModel, Field

from phi.run.response import RunEvent, RunResponse
from phi.tools.linear_tools import LinearTool
from phi.tools.slack import SlackTools
from phi.tools.github import GithubTools
from phi.agent.agent import Agent
from phi.workflow.workflow import Workflow
from phi.storage.workflow.postgres import PgWorkflowStorage
from phi.utils.log import logger


class TaskPriority(BaseModel):
    level: Literal["Low", "Medium", "High", "Critical"] = Field(..., description="Priority level of the task")
    reason: Optional[str] = Field(None, description="Reason for the priority level")


class MeetingContext(BaseModel):
    project_phase: Optional[str] = Field(None, description="Current phase of the project")
    recurring_topics: List[str] = Field(default_factory=list, description="Topics that appear frequently")
    blockers: List[str] = Field(default_factory=list, description="Identified blockers or challenges")
    follow_ups: List[str] = Field(default_factory=list, description="Items requiring follow-up")


class MeetingSummary(BaseModel):
    date: datetime = Field(..., description="Date of the meeting")
    attendees: List[str] = Field(..., description="List of attendees")
    key_points: List[str] = Field(..., description="Key points discussed")
    action_items: List[Task] = Field(..., description="Action items from the meeting")
    decisions: List[str] = Field(..., description="Key decisions made")
    context: MeetingContext = Field(default_factory=MeetingContext, description="Additional meeting context")
    duration_minutes: Optional[int] = Field(None, description="Duration of the meeting")
    meeting_type: Optional[str] = Field(None, description="Type of meeting (standup, planning, review, etc.)")


class TaskTimeEstimate(BaseModel):
    minimum_hours: float = Field(..., description="Minimum estimated hours")
    maximum_hours: float = Field(..., description="Maximum estimated hours")
    confidence_level: Literal["Low", "Medium", "High"] = Field(..., description="Confidence in the estimate")
    factors: List[str] = Field(default_factory=list, description="Factors affecting the estimate")


class TaskDependency(BaseModel):
    task_id: str = Field(..., description="ID of the dependent task")
    dependency_type: Literal["Blocks", "Required by", "Related to"] = Field(..., description="Type of dependency")
    impact_level: Literal["Low", "Medium", "High"] = Field(..., description="Impact level of the dependency")


class Task(BaseModel):
    task_title: str = Field(..., description="The title of the task")
    task_description: Optional[str] = Field(None, description="The description of the task")
    task_assignee: Optional[str] = Field(None, description="The assignee of the task")
    priority: TaskPriority = Field(..., description="Priority of the task")
    deadline: Optional[datetime] = Field(None, description="Deadline for the task")
    time_estimate: TaskTimeEstimate = Field(..., description="Detailed time estimation")
    tags: List[str] = Field(default_factory=list, description="Tags for categorizing tasks")
    dependencies: List[TaskDependency] = Field(default_factory=list, description="Task dependencies")
    complexity: Literal["Simple", "Moderate", "Complex"] = Field(..., description="Task complexity")
    required_skills: List[str] = Field(default_factory=list, description="Required skills for the task")
    status: Literal["Not Started", "In Progress", "Blocked", "Ready for Review", "Done"] = Field(
        default="Not Started", description="Current status of the task"
    )


class TeamMember(BaseModel):
    name: str = Field(..., description="Name of the team member")
    role: str = Field(..., description="Role of the team member")
    current_tasks: int = Field(default=0, description="Number of current tasks")
    capacity: float = Field(..., description="Weekly capacity in hours")
    remaining_capacity: float = Field(..., description="Remaining capacity in hours")


class LinearIssue(BaseModel):
    issue_title: str = Field(..., description="The title of the issue")
    issue_description: Optional[str] = Field(None, description="The description of the issue")
    issue_assignee: Optional[str] = Field(None, description="The assignee of the issue")
    issue_link: Optional[str] = Field(None, description="The link to the issue")
    priority: TaskPriority = Field(..., description="Priority of the issue")
    deadline: Optional[datetime] = Field(None, description="Deadline for the issue")


class LinearIssueList(BaseModel):
    issues: List[LinearIssue] = Field(..., description="A list of issues")


class TaskList(BaseModel):
    tasks: List[Task] = Field(..., description="A list of tasks")


class EnhancedProductManagerWorkflow(Workflow):
    description: str = "Enhanced workflow for managing tasks, team capacity, and project progress with integrations."

    meeting_summary_agent: Agent = Agent(
        name="Meeting Summary Agent",
        instructions=[
            "Given meeting notes:",
            "1. Extract key discussion points and categorize them by topic",
            "2. Identify and classify decisions based on impact and urgency",
            "3. List all attendees and their roles if mentioned",
            "4. Generate structured summary with action items",
            "5. Identify project phase and recurring topics",
            "6. Note any blockers or challenges mentioned",
            "7. Tag items requiring follow-up",
            "8. Determine meeting type and extract duration if mentioned"
        ],
        response_model=MeetingSummary,
    )

    task_agent: Agent = Agent(
        name="Task Agent",
        instructions=[
            "Given a meeting summary:",
            "1. Generate detailed tasks with clear titles and descriptions",
            "2. Set priorities based on:",
            "   - Impact on project goals",
            "   - Urgency and deadlines",
            "   - Dependencies on other tasks",
            "   - Resource availability",
            "3. Create detailed time estimates considering:",
            "   - Task complexity",
            "   - Required skills",
            "   - Similar past tasks",
            "   - Potential risks",
            "4. Identify and classify dependencies:",
            "   - Technical dependencies",
            "   - Resource dependencies",
            "   - Timeline dependencies",
            "5. Add relevant tags based on:",
            "   - Technical domain",
            "   - Project phase",
            "   - Required expertise",
            "   - Business impact"
        ],
        response_model=TaskList,
    )

    workload_agent: Agent = Agent(
        name="Workload Agent",
        instructions=[
            "Given team capacity and new tasks:",
            "1. Analyze current team workload",
            "2. Suggest task assignments based on capacity",
            "3. Flag potential overallocation",
            "4. Recommend task redistribution if needed"
        ],
        response_model=List[TeamMember],
    )

    linear_agent: Agent = Agent(
        name="Linear Agent",
        instructions=[
            "Given a list of tasks:",
            "1. Create detailed issues in Linear",
            "2. Set appropriate priorities and deadlines",
            "3. Link related issues",
            "4. Add relevant labels"
        ],
        tools=[LinearTool()],
        response_model=LinearIssueList,
    )

    github_agent: Agent = Agent(
        name="Github Agent",
        instructions=[
            "For code-related tasks:",
            "1. Create GitHub issues",
            "2. Link with Linear issues",
            "3. Add appropriate labels",
            "4. Set milestones if applicable"
        ],
        tools=[GithubTools()],
    )

    slack_agent: Agent = Agent(
        name="Slack Agent",
        instructions=[
            "Send detailed slack notifications including:",
            "1. Meeting summary",
            "2. New tasks and assignments",
            "3. Priority updates",
            "4. Workload alerts",
            "5. Links to Linear and GitHub issues"
        ],
        tools=[SlackTools()],
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.team_capacity = {}  # Store team capacity data

    def update_team_capacity(self, team_member: str, hours: float):
        """Update available capacity for a team member"""
        if team_member not in self.team_capacity:
            self.team_capacity[team_member] = hours
        else:
            self.team_capacity[team_member] -= hours

    def get_meeting_summary(self, meeting_notes: str) -> Optional[MeetingSummary]:
        """Generate a detailed structured summary from meeting notes"""
        try:
            # Add context from previous meetings if available
            previous_context = self.session_state.get("meeting_context", {})
            
            # Enhance meeting notes with previous context
            enhanced_notes = {
                "current_notes": meeting_notes,
                "previous_context": previous_context
            }
            
            response: RunResponse = self.meeting_summary_agent.run(enhanced_notes)
            if response and response.content:
                # Store context for future meetings
                self.session_state["meeting_context"] = response.content.context.model_dump()
                return response.content
            return None
        except Exception as e:
            logger.error(f"Error generating meeting summary: {e}")
            return None

    def generate_tasks(self, meeting_summary: MeetingSummary) -> Optional[TaskList]:
        """Generate detailed tasks from meeting summary with smart estimation"""
        try:
            # Enhance task generation with historical data
            historical_data = self.session_state.get("task_history", [])
            
            enhanced_input = {
                "meeting_summary": meeting_summary.model_dump_json(),
                "historical_data": historical_data,
                "team_capacity": self.team_capacity
            }
            
            response: RunResponse = self.task_agent.run(enhanced_input)
            if response and response.content:
                # Store task data for future reference
                if "task_history" not in self.session_state:
                    self.session_state["task_history"] = []
                self.session_state["task_history"].append(response.content.model_dump())
                return response.content
            return None
        except Exception as e:
            logger.error(f"Error generating tasks: {e}")
            return None

    def balance_workload(self, tasks: TaskList) -> bool:
        """Balance workload across team members"""
        try:
            team_data = [
                TeamMember(
                    name=member,
                    capacity=capacity,
                    remaining_capacity=capacity,
                    role="Team Member"
                )
                for member, capacity in self.team_capacity.items()
            ]
            response: RunResponse = self.workload_agent.run({
                "team": team_data,
                "tasks": tasks.model_dump_json()
            })
            return bool(response and response.content)
        except Exception as e:
            logger.error(f"Error balancing workload: {e}")
            return False

    def create_linear_issues(self, tasks: TaskList, linear_users: Dict[str, str]) -> Optional[LinearIssueList]:
        """Create issues in Linear with enhanced metadata"""
        try:
            project_id = os.getenv("LINEAR_PROJECT_ID")
            team_id = os.getenv("LINEAR_TEAM_ID")
            if not all([project_id, team_id]):
                raise ValueError("Missing Linear configuration")

            response: RunResponse = self.linear_agent.run({
                "project_id": project_id,
                "team_id": team_id,
                "tasks": tasks.model_dump_json(),
                "users": linear_users
            })
            return response.content if response and response.content else None
        except Exception as e:
            logger.error(f"Error creating Linear issues: {e}")
            return None

    def create_github_issues(self, tasks: TaskList) -> bool:
        """Create GitHub issues for code-related tasks"""
        try:
            code_tasks = [task for task in tasks.tasks if "code" in task.tags]
            if not code_tasks:
                return True

            response: RunResponse = self.github_agent.run({
                "tasks": code_tasks,
                "repo": os.getenv("GITHUB_REPO")
            })
            return bool(response and response.content)
        except Exception as e:
            logger.error(f"Error creating GitHub issues: {e}")
            return False

    def send_notifications(self, meeting_summary: MeetingSummary, tasks: TaskList, linear_issues: LinearIssueList) -> bool:
        """Send comprehensive notifications"""
        try:
            notification_data = {
                "summary": meeting_summary.model_dump_json(),
                "tasks": tasks.model_dump_json(),
                "issues": linear_issues.model_dump_json() if linear_issues else None,
                "workload_alerts": [
                    f"{member}: {capacity}hrs remaining"
                    for member, capacity in self.team_capacity.items()
                    if capacity < 10  # Alert for low capacity
                ]
            }
            response: RunResponse = self.slack_agent.run(notification_data)
            return bool(response and response.content)
        except Exception as e:
            logger.error(f"Error sending notifications: {e}")
            return False

    def run(
        self,
        meeting_notes: str,
        linear_users: Dict[str, str],
        team_capacity: Dict[str, float]
    ) -> RunResponse:
        """Execute the enhanced workflow"""
        logger.info("Starting enhanced product manager workflow")
        
        # Initialize team capacity
        self.team_capacity = team_capacity.copy()

        # Generate meeting summary
        meeting_summary = self.get_meeting_summary(meeting_notes)
        if not meeting_summary:
            return RunResponse(
                run_id=self.run_id,
                event=RunEvent.workflow_failed,
                content="Failed to generate meeting summary"
            )

        # Generate tasks
        tasks = self.generate_tasks(meeting_summary)
        if not tasks:
            return RunResponse(
                run_id=self.run_id,
                event=RunEvent.workflow_failed,
                content="Failed to generate tasks"
            )

        # Balance workload
        if not self.balance_workload(tasks):
            logger.warning("Workload balancing failed, proceeding with original assignments")

        # Create Linear issues
        linear_issues = self.create_linear_issues(tasks, linear_users)
        if not linear_issues:
            return RunResponse(
                run_id=self.run_id,
                event=RunEvent.workflow_failed,
                content="Failed to create Linear issues"
            )

        # Create GitHub issues for code-related tasks
        if not self.create_github_issues(tasks):
            logger.warning("Failed to create some GitHub issues")

        # Send notifications
        if not self.send_notifications(meeting_summary, tasks, linear_issues):
            logger.warning("Failed to send some notifications")

        return RunResponse(
            run_id=self.run_id,
            event=RunEvent.workflow_completed,
            content={
                "meeting_summary": meeting_summary.model_dump_json(),
                "tasks": tasks.model_dump_json(),
                "linear_issues": linear_issues.model_dump_json()
            }
        )


# Create the workflow
enhanced_pm = EnhancedProductManagerWorkflow(
    session_id="enhanced-product-manager",
    storage=PgWorkflowStorage(
        table_name="enhanced_pm_workflows",
        db_url="postgresql+psycopg://ai:ai@localhost:5532/ai",
    ),
) 