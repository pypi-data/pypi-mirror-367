import os
from datetime import datetime
from youtrack_rest_client import Connection, Issue, Project

YOUTRACK_URL = "https://r3recube.myjetbrains.com/youtrack/"

def read_token_from_file(file_path):
    try:
        with open(file_path, 'r') as file:
            return file.read().strip()
    except FileNotFoundError:
        print(f"Token file not found: {file_path}")
        exit(1)

def main():
    # Initialize the Authenticated Client
    token_file = os.path.expanduser("secrets/yt_token.txt")
    token = read_token_from_file(token_file)
    client = Connection(base_url=YOUTRACK_URL, token=token)

    # Get Projects
    has_more = True
    items_limit = 10
    skip = 0
    while has_more:
        projects = client.get_projects(limit=items_limit, skip=skip)
        if not projects:
            has_more = False
        else:
            for item in projects:
                print(f"Project {item['id']}: {item['name']} {item['shortName']} created by {item['createdBy']}")
            skip += items_limit

    # Get Details from a specific Project
    project = Project(client, 'AI')
    project_details = project.get_details()
    project_issues = project.get_issues(limit=None)
    print(f"Found {len(project_issues)} issues")
    for issue in project_issues:
        print(f"{issue['id']}: {issue['summary']}:  {issue['description']}")

    # Get Issue
    issue = Issue(client, 'AI-121')
    has_more = True
    items_limit = 10
    skip = 0
    while has_more:
        issue_work_item = issue.get_work_items(limit=items_limit, skip=skip)
        if not issue_work_item:
            has_more = False
        else:
            for item in issue_work_item:
                timestamp_ms = item['date']
                date = datetime.fromtimestamp(timestamp_ms / 1000).strftime('%Y/%m/%d')
                print(f"User {item['author']['name']} spent {item['duration']['minutes']} minutes {item['$type']} on {date} for {item['text']}")
            skip += items_limit

    # Add Work Time (uncomment to use)
    # issue.add_work_item(60, date=None, description="Test REST Paolo")
    # issue.add_work_item(60, date='05/05/2025', description="Test REST Paolo")

if __name__ == "__main__":
    main()