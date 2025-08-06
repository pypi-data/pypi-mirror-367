#!/usr/bin/env python3
"""GitHub Project MCP Server - Manage GitHub projects and issues via GraphQL API"""

import asyncio
import json
import os
from typing import Any, Dict, List, Optional
from datetime import datetime

import httpx
from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
import mcp.server.stdio
import mcp.types as types

class GitHubGraphQLClient:
    """Client for GitHub GraphQL API"""
    
    def __init__(self, token: str):
        self.token = token
        self.endpoint = "https://api.github.com/graphql"
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
    
    async def execute_query(self, query: str, variables: Optional[Dict] = None) -> Dict:
        """Execute a GraphQL query"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.endpoint,
                json={"query": query, "variables": variables or {}},
                headers=self.headers,
                timeout=30.0
            )
            response.raise_for_status()
            result = response.json()
            
            if "errors" in result:
                raise Exception(f"GraphQL errors: {result['errors']}")
            
            return result.get("data", {})
    
    async def list_issues(self, owner: str, repo: str, state: str = "OPEN") -> List[Dict]:
        """List issues in a repository"""
        query = """
        query ListIssues($owner: String!, $repo: String!, $state: IssueState!) {
            repository(owner: $owner, name: $repo) {
                issues(first: 100, states: [$state], orderBy: {field: CREATED_AT, direction: DESC}) {
                    nodes {
                        id
                        number
                        title
                        body
                        state
                        createdAt
                        updatedAt
                        author {
                            login
                        }
                        labels(first: 10) {
                            nodes {
                                name
                                color
                            }
                        }
                        assignees(first: 10) {
                            nodes {
                                login
                            }
                        }
                    }
                }
            }
        }
        """
        
        variables = {
            "owner": owner,
            "repo": repo,
            "state": state
        }
        
        data = await self.execute_query(query, variables)
        return data.get("repository", {}).get("issues", {}).get("nodes", [])
    
    async def create_issue(self, repo_id: str, title: str, body: Optional[str] = None,
                          label_ids: Optional[List[str]] = None,
                          assignee_ids: Optional[List[str]] = None) -> Dict:
        """Create a new issue"""
        query = """
        mutation CreateIssue($input: CreateIssueInput!) {
            createIssue(input: $input) {
                issue {
                    id
                    number
                    title
                    body
                    state
                    createdAt
                    url
                }
            }
        }
        """
        
        input_data = {
            "repositoryId": repo_id,
            "title": title
        }
        
        if body:
            input_data["body"] = body
        if label_ids:
            input_data["labelIds"] = label_ids
        if assignee_ids:
            input_data["assigneeIds"] = assignee_ids
        
        variables = {"input": input_data}
        
        data = await self.execute_query(query, variables)
        return data.get("createIssue", {}).get("issue", {})
    
    async def update_issue(self, issue_id: str, title: Optional[str] = None,
                          body: Optional[str] = None, state: Optional[str] = None,
                          label_ids: Optional[List[str]] = None,
                          assignee_ids: Optional[List[str]] = None) -> Dict:
        """Update an existing issue"""
        query = """
        mutation UpdateIssue($input: UpdateIssueInput!) {
            updateIssue(input: $input) {
                issue {
                    id
                    number
                    title
                    body
                    state
                    updatedAt
                }
            }
        }
        """
        
        input_data = {"id": issue_id}
        
        if title is not None:
            input_data["title"] = title
        if body is not None:
            input_data["body"] = body
        if state is not None:
            input_data["state"] = state
        if label_ids is not None:
            input_data["labelIds"] = label_ids
        if assignee_ids is not None:
            input_data["assigneeIds"] = assignee_ids
        
        variables = {"input": input_data}
        
        data = await self.execute_query(query, variables)
        return data.get("updateIssue", {}).get("issue", {})
    
    async def delete_issue(self, issue_id: str) -> bool:
        """Close an issue (GitHub doesn't allow actual deletion)"""
        query = """
        mutation CloseIssue($input: UpdateIssueInput!) {
            updateIssue(input: $input) {
                issue {
                    id
                    state
                }
            }
        }
        """
        
        variables = {
            "input": {
                "id": issue_id,
                "state": "CLOSED"
            }
        }
        
        data = await self.execute_query(query, variables)
        issue = data.get("updateIssue", {}).get("issue", {})
        return issue.get("state") == "CLOSED"
    
    async def get_repository_id(self, owner: str, repo: str) -> str:
        """Get the repository ID needed for mutations"""
        query = """
        query GetRepoId($owner: String!, $repo: String!) {
            repository(owner: $owner, name: $repo) {
                id
            }
        }
        """
        
        variables = {
            "owner": owner,
            "repo": repo
        }
        
        data = await self.execute_query(query, variables)
        return data.get("repository", {}).get("id", "")
    
    async def list_projects(self, owner: str, repo: str) -> List[Dict]:
        """List projects in a repository (new Projects)"""
        query = """
        query ListProjects($owner: String!, $repo: String!) {
            repository(owner: $owner, name: $repo) {
                projectsV2(first: 20) {
                    nodes {
                        id
                        title
                        shortDescription
                        url
                        closed
                        createdAt
                        updatedAt
                    }
                }
            }
        }
        """
        
        variables = {
            "owner": owner,
            "repo": repo
        }
        
        data = await self.execute_query(query, variables)
        return data.get("repository", {}).get("projectsV2", {}).get("nodes", [])
    
    async def get_project_items(self, project_id: str) -> List[Dict]:
        """Get items in a project"""
        query = """
        query GetProjectItems($projectId: ID!) {
            node(id: $projectId) {
                ... on ProjectV2 {
                    items(first: 100) {
                        nodes {
                            id
                            type
                            content {
                                ... on Issue {
                                    id
                                    number
                                    title
                                    state
                                }
                                ... on PullRequest {
                                    id
                                    number
                                    title
                                    state
                                }
                            }
                        }
                    }
                }
            }
        }
        """
        
        variables = {"projectId": project_id}
        
        data = await self.execute_query(query, variables)
        return data.get("node", {}).get("items", {}).get("nodes", [])


# Initialize the MCP server
server = Server("github-project-server")
github_client: Optional[GitHubGraphQLClient] = None

@server.list_resources()
async def handle_list_resources() -> list[types.Resource]:
    """List available resources"""
    return [
        types.Resource(
            uri="github://readme",
            name="GitHub Project MCP Server README",
            description="Documentation for the GitHub Project MCP Server",
            mimeType="text/plain",
        )
    ]

@server.read_resource()
async def handle_read_resource(uri: str) -> str:
    """Read a resource"""
    if uri == "github://readme":
        return """GitHub Project MCP Server
        
This server provides tools to manage GitHub projects and issues using GraphQL API.

Available tools:
- list_issues: List issues in a repository
- create_issue: Create a new issue
- update_issue: Update an existing issue
- delete_issue: Close an issue (GitHub doesn't allow deletion)
- list_projects: List projects in a repository
- get_project_items: Get items in a project
- get_repo_id: Get repository ID for mutations

Configuration:
Set GITHUB_TOKEN environment variable with your GitHub personal access token.
"""
    raise ValueError(f"Unknown resource: {uri}")

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """List available tools"""
    return [
        types.Tool(
            name="list_issues",
            description="List issues in a GitHub repository",
            inputSchema={
                "type": "object",
                "properties": {
                    "owner": {"type": "string", "description": "Repository owner"},
                    "repo": {"type": "string", "description": "Repository name"},
                    "state": {"type": "string", "enum": ["OPEN", "CLOSED"], "default": "OPEN"}
                },
                "required": ["owner", "repo"]
            }
        ),
        types.Tool(
            name="create_issue",
            description="Create a new issue in a GitHub repository",
            inputSchema={
                "type": "object",
                "properties": {
                    "owner": {"type": "string", "description": "Repository owner"},
                    "repo": {"type": "string", "description": "Repository name"},
                    "title": {"type": "string", "description": "Issue title"},
                    "body": {"type": "string", "description": "Issue body/description"},
                    "labels": {"type": "array", "items": {"type": "string"}, "description": "Label IDs"},
                    "assignees": {"type": "array", "items": {"type": "string"}, "description": "Assignee IDs"}
                },
                "required": ["owner", "repo", "title"]
            }
        ),
        types.Tool(
            name="update_issue",
            description="Update an existing GitHub issue",
            inputSchema={
                "type": "object",
                "properties": {
                    "issue_id": {"type": "string", "description": "Issue ID"},
                    "title": {"type": "string", "description": "New title"},
                    "body": {"type": "string", "description": "New body"},
                    "state": {"type": "string", "enum": ["OPEN", "CLOSED"]},
                    "labels": {"type": "array", "items": {"type": "string"}, "description": "Label IDs"},
                    "assignees": {"type": "array", "items": {"type": "string"}, "description": "Assignee IDs"}
                },
                "required": ["issue_id"]
            }
        ),
        types.Tool(
            name="delete_issue",
            description="Close a GitHub issue (actual deletion not supported by GitHub)",
            inputSchema={
                "type": "object",
                "properties": {
                    "issue_id": {"type": "string", "description": "Issue ID to close"}
                },
                "required": ["issue_id"]
            }
        ),
        types.Tool(
            name="list_projects",
            description="List projects in a GitHub repository",
            inputSchema={
                "type": "object",
                "properties": {
                    "owner": {"type": "string", "description": "Repository owner"},
                    "repo": {"type": "string", "description": "Repository name"}
                },
                "required": ["owner", "repo"]
            }
        ),
        types.Tool(
            name="get_project_items",
            description="Get items in a GitHub project",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {"type": "string", "description": "Project ID"}
                },
                "required": ["project_id"]
            }
        ),
        types.Tool(
            name="get_repo_id",
            description="Get repository ID for mutations",
            inputSchema={
                "type": "object",
                "properties": {
                    "owner": {"type": "string", "description": "Repository owner"},
                    "repo": {"type": "string", "description": "Repository name"}
                },
                "required": ["owner", "repo"]
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(
    name: str,
    arguments: Dict[str, Any]
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """Handle tool calls"""
    
    if not github_client:
        return [types.TextContent(
            type="text",
            text="Error: GitHub client not initialized. Please set GITHUB_TOKEN environment variable."
        )]
    
    try:
        if name == "list_issues":
            issues = await github_client.list_issues(
                arguments["owner"],
                arguments["repo"],
                arguments.get("state", "OPEN")
            )
            return [types.TextContent(
                type="text",
                text=json.dumps(issues, indent=2, default=str)
            )]
        
        elif name == "create_issue":
            repo_id = await github_client.get_repository_id(
                arguments["owner"],
                arguments["repo"]
            )
            issue = await github_client.create_issue(
                repo_id,
                arguments["title"],
                arguments.get("body"),
                arguments.get("labels"),
                arguments.get("assignees")
            )
            return [types.TextContent(
                type="text",
                text=json.dumps(issue, indent=2, default=str)
            )]
        
        elif name == "update_issue":
            issue = await github_client.update_issue(
                arguments["issue_id"],
                arguments.get("title"),
                arguments.get("body"),
                arguments.get("state"),
                arguments.get("labels"),
                arguments.get("assignees")
            )
            return [types.TextContent(
                type="text",
                text=json.dumps(issue, indent=2, default=str)
            )]
        
        elif name == "delete_issue":
            closed = await github_client.delete_issue(arguments["issue_id"])
            return [types.TextContent(
                type="text",
                text=json.dumps({"success": closed, "message": "Issue closed" if closed else "Failed to close issue"})
            )]
        
        elif name == "list_projects":
            projects = await github_client.list_projects(
                arguments["owner"],
                arguments["repo"]
            )
            return [types.TextContent(
                type="text",
                text=json.dumps(projects, indent=2, default=str)
            )]
        
        elif name == "get_project_items":
            items = await github_client.get_project_items(arguments["project_id"])
            return [types.TextContent(
                type="text",
                text=json.dumps(items, indent=2, default=str)
            )]
        
        elif name == "get_repo_id":
            repo_id = await github_client.get_repository_id(
                arguments["owner"],
                arguments["repo"]
            )
            return [types.TextContent(
                type="text",
                text=json.dumps({"repository_id": repo_id})
            )]
        
        else:
            return [types.TextContent(
                type="text",
                text=f"Unknown tool: {name}"
            )]
    
    except Exception as e:
        return [types.TextContent(
            type="text",
            text=f"Error: {str(e)}"
        )]

async def main():
    """Main entry point"""
    global github_client
    
    # Get GitHub token from environment
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        print("Warning: GITHUB_TOKEN not set. Server will run but tools won't work.")
    else:
        github_client = GitHubGraphQLClient(token)
    
    # Run the server
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="github-project-server",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

if __name__ == "__main__":
    asyncio.run(main())