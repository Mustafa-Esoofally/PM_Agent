from datetime import datetime
from phi.run.response import RunEvent

# Import from local module
from workflow import EnhancedProductManagerWorkflow

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

Sarah (Tech Lead):
"Good morning everyone! Let's go through our updates and new assignments for today. Mike, would you like to start?"

Mike (Backend Developer):
"Sure. I'll be working on implementing the new authentication service we discussed last week. The main tasks include setting up JWT token management and integrating with the user service. Estimated completion time is about 3-4 days."

Emma (Frontend Developer):
"I'm picking up the user dashboard redesign today. This includes implementing the new analytics widgets and improving the mobile responsiveness. I should have a preliminary version ready for review by Thursday."

Alex (DevOps Engineer):
"I'm focusing on setting up the new monitoring system. Will be configuring Prometheus and Grafana for better observability. Also need to update our CI/CD pipeline to include the new security scanning tools."

James (QA Engineer):
"I'll be creating automated test cases for Mike's authentication service once it's ready. In the meantime, I'm updating our end-to-end test suite and documenting the new test procedures for the dashboard features."

Sarah (Tech Lead):
"Great updates, everyone. Remember we have the architecture review meeting tomorrow at 2 PM. Please prepare your components documentation. Let me know if anyone needs any help or runs into blockers. Let's have a productive day!"

Meeting ended at 9:45 AM
'''

def test_workflow():
    # Initialize workflow with memory storage
    workflow = EnhancedProductManagerWorkflow(
        session_id="test-session",
        storage=MemoryWorkflowStorage(),
    )

    # Team capacity (hours per week)
    team_capacity = {
        "Sarah": 40,
        "Mike": 35,
        "Emma": 40,
        "Alex": 35,
        "James": 40
    }

    # Mock Linear user IDs
    linear_users = {
        "Sarah": "user_uuid_1",
        "Mike": "user_uuid_2",
        "Emma": "user_uuid_3",
        "Alex": "user_uuid_4",
        "James": "user_uuid_5"
    }

    # Run the workflow
    print("\n=== Starting Workflow Test ===\n")
    
    result = workflow.run(
        meeting_notes=SAMPLE_MEETING_NOTES,
        linear_users=linear_users,
        team_capacity=team_capacity
    )

    # Print results
    if result.event == RunEvent.workflow_completed:
        print("\n=== Workflow Completed Successfully ===")
        
        # Print Meeting Summary
        meeting_summary = result.content["meeting_summary"]
        print("\nMeeting Summary:")
        print(f"Date: {meeting_summary['date']}")
        print(f"Type: {meeting_summary['meeting_type']}")
        print(f"Duration: {meeting_summary['duration_minutes']} minutes")
        print("\nKey Points:")
        for point in meeting_summary["key_points"]:
            print(f"- {point}")
        
        # Print Tasks
        tasks = result.content["tasks"]
        print("\nGenerated Tasks:")
        for task in tasks["tasks"]:
            print(f"\nTask: {task['task_title']}")
            print(f"Assignee: {task['task_assignee']}")
            print(f"Priority: {task['priority']['level']} ({task['priority']['reason']})")
            print(f"Complexity: {task['complexity']}")
            print(f"Time Estimate: {task['time_estimate']['minimum_hours']}-{task['time_estimate']['maximum_hours']} hours")
            print(f"Confidence: {task['time_estimate']['confidence_level']}")
            if task['dependencies']:
                print("Dependencies:")
                for dep in task['dependencies']:
                    print(f"- {dep['dependency_type']}: {dep['task_id']} (Impact: {dep['impact_level']})")
        
        # Print Linear Issues
        linear_issues = result.content["linear_issues"]
        print("\nCreated Linear Issues:")
        for issue in linear_issues["issues"]:
            print(f"\nIssue: {issue['issue_title']}")
            print(f"Assignee: {issue['issue_assignee']}")
            print(f"Priority: {issue['priority']['level']}")
            if issue['issue_link']:
                print(f"Link: {issue['issue_link']}")
    else:
        print("\n=== Workflow Failed ===")
        print(f"Error: {result.content}")

if __name__ == "__main__":
    test_workflow() 