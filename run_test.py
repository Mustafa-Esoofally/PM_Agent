import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get DB_URL and modify protocol if needed
db_url = os.getenv("DB_URL", "").replace("postgresql+psycopg://", "postgresql://")
print(f"Using DB_URL: {db_url}")

# Add the current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

# Import the simplified workflow
from simple_workflow import SimpleProductManagerWorkflow
from phi.storage.workflow.postgres import PgWorkflowStorage

# Sample meeting notes
SAMPLE_MEETING_NOTES = '''
Daily Standup Meeting - Technical Team
Date: 2024-01-15
Time: 9:30 AM - 9:45 AM

Attendees:
- Sarah (Tech Lead)
- Mike (Backend Developer) 
- Emma (Frontend Developer)
- Alex (DevOps Engineer)
- James (QA Engineer)

Updates:
1. Mike will implement new authentication service with JWT token management (3-4 days)
2. Emma is working on user dashboard redesign with analytics widgets (due Thursday)
3. Alex is setting up Prometheus and Grafana monitoring
4. James will create automated tests for the auth service

Next Steps:
- Architecture review meeting tomorrow at 2 PM
- Everyone should prepare component documentation
'''

# Team capacity in hours per week
team_capacity = {
    "Sarah": 40,
    "Mike": 35,
    "Emma": 40,
    "Alex": 35,
    "James": 40
}

def test_workflow():
    print("\n=== Starting Simple Workflow Test ===\n")
    
    # Initialize workflow
    workflow = SimpleProductManagerWorkflow(
        session_id="test-session",
        storage=PgWorkflowStorage(
            table_name="workflow_sessions",
            db_url=os.getenv("DB_URL")
        ),
    )
    
    # Run the workflow
    response = workflow.run(
        meeting_notes=SAMPLE_MEETING_NOTES,
        team_capacity=team_capacity
    )
    
    # Print results
    if response and response.content:
        print("\n=== Generated Tasks ===")
        for task in response.content.tasks:
            print(f"\nTask: {task.task_title}")
            if task.task_assignee:
                print(f"Assignee: {task.task_assignee}")
            print(f"Priority: {task.priority.level}")
            if task.priority.reason:
                print(f"Priority Reason: {task.priority.reason}")
            print(f"Complexity: {task.complexity}")
            print(f"Time Estimate: {task.time_estimate.minimum_hours}-{task.time_estimate.maximum_hours} hours")
            print(f"Confidence: {task.time_estimate.confidence_level}")
    else:
        print("No tasks were generated.")

if __name__ == "__main__":
    test_workflow() 