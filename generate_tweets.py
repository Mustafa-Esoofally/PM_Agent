import os
from dotenv import load_dotenv
from tweet_workflow import TweetGeneratorWorkflow
from phi.storage.workflow.postgres import PgWorkflowStorage

# Load environment variables
load_dotenv()

def generate_tweets():
    print("\n=== Generating Project Tweets ===\n")
    
    # Initialize workflow
    workflow = TweetGeneratorWorkflow(
        session_id="tweet-session",
        storage=PgWorkflowStorage(
            table_name="workflow_sessions",
            db_url=os.getenv("DB_URL")
        ),
    )
    
    # Run the workflow
    response = workflow.run()
    
    # Print results
    if response and response.content:
        print("\n=== Generated Tweets ===")
        for i, tweet in enumerate(response.content.tweets, 1):
            print(f"\nTweet {i}:")
            print(f"Text: {tweet.text}")
            print(f"Hashtags: {' '.join(tweet.hashtags)}")
    else:
        print("No tweets were generated.")

if __name__ == "__main__":
    generate_tweets() 