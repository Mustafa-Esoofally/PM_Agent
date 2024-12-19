# Enhanced Product Manager Agent

An AI-powered workflow that helps manage software development teams by automating task management, workload balancing, and communication.

## Features

1. **Intelligent Meeting Summary Generation**
   - Extracts key discussion points
   - Identifies decisions made
   - Lists attendees
   - Generates structured summaries with action items

2. **Advanced Task Management**
   - Priority tracking with reasoning
   - Deadline management
   - Time estimation
   - Task dependencies tracking
   - Automatic task tagging and categorization

3. **Team Capacity Management**
   - Tracks individual team member capacity
   - Monitors current workload
   - Suggests optimal task assignments
   - Alerts on potential overallocation

4. **Multi-Platform Integration**
   - Linear for task tracking
   - GitHub for code-related tasks
   - Slack for team communication
   - Automatic issue linking between platforms

5. **Smart Notifications**
   - Meeting summaries
   - Task assignments
   - Priority updates
   - Workload alerts
   - Cross-platform issue links

## Setup

1. **Environment Variables**
   ```bash
   # Linear Configuration
   LINEAR_API_KEY=your_linear_api_key
   LINEAR_PROJECT_ID=your_project_id
   LINEAR_TEAM_ID=your_team_id

   # GitHub Configuration
   GITHUB_TOKEN=your_github_token
   GITHUB_REPO=owner/repository

   # Slack Configuration
   SLACK_BOT_TOKEN=your_slack_bot_token
   SLACK_CHANNEL=your_channel_id
   ```

2. **Database Configuration**
   The workflow uses PostgreSQL for storage. Update the database URL in the workflow initialization:
   ```python
   db_url="postgresql+psycopg://username:password@host:port/database"
   ```

3. **Dependencies**
   ```bash
   pip install phi-agent phi-tools pydantic psycopg2-binary
   ```

## Usage

```python
from projects.enhanced_pm_agent.workflow import EnhancedProductManagerWorkflow

# Initialize the workflow
workflow = EnhancedProductManagerWorkflow(
    session_id="your-session-id",
    storage=PgWorkflowStorage(
        table_name="your_workflow_table",
        db_url="your_db_url"
    )
)

# Team capacity in hours per week
team_capacity = {
    "Sarah": 40,
    "Mike": 35,
    "Emma": 40,
    "Alex": 35,
    "James": 40
}

# Linear user IDs
linear_users = {
    "Sarah": "user_uuid_1",
    "Mike": "user_uuid_2",
    "Emma": "user_uuid_3",
    "Alex": "user_uuid_4",
    "James": "user_uuid_5"
}

# Run the workflow
result = workflow.run(
    meeting_notes="Your meeting notes here",
    linear_users=linear_users,
    team_capacity=team_capacity
)
```

## Output

The workflow generates a structured output containing:
1. Meeting summary with key points and decisions
2. Task list with priorities, deadlines, and assignments
3. Linear issues with cross-platform links
4. Workload distribution report

## Error Handling

The workflow includes comprehensive error handling:
- Graceful failure recovery
- Detailed error logging
- Warning notifications for partial failures
- Automatic retries for critical operations

## Contributing

Feel free to submit issues and enhancement requests! 