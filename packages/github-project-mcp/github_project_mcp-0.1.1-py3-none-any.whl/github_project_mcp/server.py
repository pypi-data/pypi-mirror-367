#!/usr/bin/env python3
"""GitHub Project MCP Server - Manage GitHub projects and issues via GraphQL API"""

import asyncio
import json
import os
import base64
import mimetypes
from typing import Any, Dict, List, Optional, Union
from datetime import datetime
from pathlib import Path

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
        self.rest_endpoint = "https://api.github.com"
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        self.upload_headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github.v3+json",
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
    
    async def add_labels_to_issue(self, issue_id: str, label_ids: List[str]) -> Dict:
        """Add labels to an issue"""
        query = """
        mutation AddLabels($input: AddLabelsToLabelableInput!) {
            addLabelsToLabelable(input: $input) {
                labelable {
                    ... on Issue {
                        id
                        labels(first: 10) {
                            nodes {
                                name
                                color
                            }
                        }
                    }
                }
            }
        }
        """
        
        variables = {
            "input": {
                "labelableId": issue_id,
                "labelIds": label_ids
            }
        }
        
        data = await self.execute_query(query, variables)
        return data.get("addLabelsToLabelable", {}).get("labelable", {})
    
    async def remove_labels_from_issue(self, issue_id: str, label_ids: List[str]) -> Dict:
        """Remove labels from an issue"""
        query = """
        mutation RemoveLabels($input: RemoveLabelsFromLabelableInput!) {
            removeLabelsFromLabelable(input: $input) {
                labelable {
                    ... on Issue {
                        id
                        labels(first: 10) {
                            nodes {
                                name
                                color
                            }
                        }
                    }
                }
            }
        }
        """
        
        variables = {
            "input": {
                "labelableId": issue_id,
                "labelIds": label_ids
            }
        }
        
        data = await self.execute_query(query, variables)
        return data.get("removeLabelsFromLabelable", {}).get("labelable", {})
    
    async def add_assignees_to_issue(self, issue_id: str, assignee_ids: List[str]) -> Dict:
        """Add assignees to an issue"""
        query = """
        mutation AddAssignees($input: AddAssigneesToAssignableInput!) {
            addAssigneesToAssignable(input: $input) {
                assignable {
                    ... on Issue {
                        id
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
            "input": {
                "assignableId": issue_id,
                "assigneeIds": assignee_ids
            }
        }
        
        data = await self.execute_query(query, variables)
        return data.get("addAssigneesToAssignable", {}).get("assignable", {})
    
    async def remove_assignees_from_issue(self, issue_id: str, assignee_ids: List[str]) -> Dict:
        """Remove assignees from an issue"""
        query = """
        mutation RemoveAssignees($input: RemoveAssigneesFromAssignableInput!) {
            removeAssigneesFromAssignable(input: $input) {
                assignable {
                    ... on Issue {
                        id
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
            "input": {
                "assignableId": issue_id,
                "assigneeIds": assignee_ids
            }
        }
        
        data = await self.execute_query(query, variables)
        return data.get("removeAssigneesFromAssignable", {}).get("assignable", {})
    
    async def add_issue_to_project(self, project_id: str, content_id: str) -> Dict:
        """Add an issue to a project"""
        query = """
        mutation AddProjectItem($input: AddProjectV2ItemByIdInput!) {
            addProjectV2ItemById(input: $input) {
                item {
                    id
                    content {
                        ... on Issue {
                            id
                            number
                            title
                        }
                    }
                }
            }
        }
        """
        
        variables = {
            "input": {
                "projectId": project_id,
                "contentId": content_id
            }
        }
        
        data = await self.execute_query(query, variables)
        return data.get("addProjectV2ItemById", {}).get("item", {})
    
    async def remove_issue_from_project(self, project_id: str, item_id: str) -> bool:
        """Remove an issue from a project"""
        query = """
        mutation RemoveProjectItem($input: DeleteProjectV2ItemInput!) {
            deleteProjectV2Item(input: $input) {
                deletedItemId
            }
        }
        """
        
        variables = {
            "input": {
                "projectId": project_id,
                "itemId": item_id
            }
        }
        
        data = await self.execute_query(query, variables)
        return bool(data.get("deleteProjectV2Item", {}).get("deletedItemId"))
    
    async def update_project_item_field(self, project_id: str, item_id: str, 
                                       field_id: str, value: Any) -> Dict:
        """Update a field value for a project item"""
        query = """
        mutation UpdateProjectItemField($input: UpdateProjectV2ItemFieldValueInput!) {
            updateProjectV2ItemFieldValue(input: $input) {
                projectV2Item {
                    id
                }
            }
        }
        """
        
        # For single select fields (like Status), we need to pass the option ID
        # The value should be either the option ID directly or the option name
        variables = {
            "input": {
                "projectId": project_id,
                "itemId": item_id,
                "fieldId": field_id,
                "value": {"singleSelectOptionId": value} if not value.startswith("{") else value
            }
        }
        
        data = await self.execute_query(query, variables)
        return data.get("updateProjectV2ItemFieldValue", {}).get("projectV2Item", {})
    
    async def update_project_item_status(self, project_id: str, item_id: str, 
                                        status_name: str) -> Dict:
        """Update the status of a project item (e.g., Todo, In Progress, Done)"""
        # First, get the project fields to find the Status field and its options
        fields = await self.get_project_fields(project_id)
        
        # Find the Status field (usually named "Status")
        status_field = None
        status_option_id = None
        
        for field in fields:
            if field.get("name", "").lower() == "status" and "options" in field:
                status_field = field
                # Find the matching status option
                for option in field["options"]:
                    if option["name"].lower() == status_name.lower():
                        status_option_id = option["id"]
                        break
                break
        
        if not status_field:
            raise Exception("Status field not found in project")
        
        if not status_option_id:
            available_options = [opt["name"] for opt in status_field.get("options", [])]
            raise Exception(f"Status '{status_name}' not found. Available options: {', '.join(available_options)}")
        
        # Update the status using the field ID and option ID
        return await self.update_project_item_field(
            project_id, 
            item_id, 
            status_field["id"], 
            status_option_id
        )
    
    async def get_repository_labels(self, owner: str, repo: str) -> List[Dict]:
        """Get all labels in a repository"""
        query = """
        query GetRepoLabels($owner: String!, $repo: String!) {
            repository(owner: $owner, name: $repo) {
                labels(first: 100) {
                    nodes {
                        id
                        name
                        color
                        description
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
        return data.get("repository", {}).get("labels", {}).get("nodes", [])
    
    async def get_user_id(self, username: str) -> str:
        """Get a user's ID by username"""
        query = """
        query GetUserId($username: String!) {
            user(login: $username) {
                id
            }
        }
        """
        
        variables = {"username": username}
        
        data = await self.execute_query(query, variables)
        return data.get("user", {}).get("id", "")
    
    async def get_project_fields(self, project_id: str) -> List[Dict]:
        """Get fields in a project (for status/columns)"""
        query = """
        query GetProjectFields($projectId: ID!) {
            node(id: $projectId) {
                ... on ProjectV2 {
                    fields(first: 20) {
                        nodes {
                            ... on ProjectV2Field {
                                id
                                name
                            }
                            ... on ProjectV2SingleSelectField {
                                id
                                name
                                options {
                                    id
                                    name
                                }
                            }
                            ... on ProjectV2IterationField {
                                id
                                name
                            }
                        }
                    }
                }
            }
        }
        """
        
        variables = {"projectId": project_id}
        
        data = await self.execute_query(query, variables)
        return data.get("node", {}).get("fields", {}).get("nodes", [])
    
    async def upload_image_to_github(self, owner: str, repo: str, 
                                    image_path: str, image_content: Optional[bytes] = None) -> str:
        """Upload an image to GitHub and return the URL for embedding"""
        # If image_content not provided, read from file
        if image_content is None:
            path = Path(image_path)
            if not path.exists():
                raise FileNotFoundError(f"Image file not found: {image_path}")
            with open(path, 'rb') as f:
                image_content = f.read()
        
        # Determine file extension and mime type
        if '.' in image_path:
            ext = image_path.split('.')[-1].lower()
        else:
            ext = 'png'
        
        mime_type = mimetypes.guess_type(f"dummy.{ext}")[0] or 'image/png'
        
        # Generate unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"image_{timestamp}.{ext}"
        
        # Create the content for GitHub (base64 encoded)
        content_base64 = base64.b64encode(image_content).decode('utf-8')
        
        # Use REST API to create/upload file to a special assets branch or wiki
        # We'll use the GitHub user content URL approach
        # Note: GitHub doesn't have a direct API for uploading to user-images.githubusercontent.com
        # Instead, we'll create the image as a file in the repository
        
        url = f"{self.rest_endpoint}/repos/{owner}/{repo}/contents/.github/assets/{filename}"
        
        payload = {
            "message": f"Upload image {filename}",
            "content": content_base64,
            "branch": "main"  # You might want to use a different branch
        }
        
        async with httpx.AsyncClient() as client:
            # First, try to create the directory structure if it doesn't exist
            try:
                response = await client.put(
                    url,
                    json=payload,
                    headers=self.upload_headers,
                    timeout=60.0
                )
                response.raise_for_status()
                result = response.json()
                # Return the raw GitHub URL for the uploaded file
                return result['content']['download_url']
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 422:
                    # File might already exist or branch issues
                    # Try with a different filename
                    import random
                    filename = f"image_{timestamp}_{random.randint(1000,9999)}.{ext}"
                    url = f"{self.rest_endpoint}/repos/{owner}/{repo}/contents/.github/assets/{filename}"
                    response = await client.put(
                        url,
                        json=payload,
                        headers=self.upload_headers,
                        timeout=60.0
                    )
                    response.raise_for_status()
                    result = response.json()
                    return result['content']['download_url']
                else:
                    raise
    
    def embed_images_in_markdown(self, body: str, images: List[Dict[str, str]]) -> str:
        """
        Embed images in markdown body
        images: List of dicts with 'url' and optional 'alt' text
        """
        if not images:
            return body
        
        # Add images at the end of the body
        image_markdown = "\n\n---\n\n"
        for img in images:
            alt_text = img.get('alt', 'Image')
            url = img['url']
            image_markdown += f"![{alt_text}]({url})\n\n"
        
        return body + image_markdown
    
    async def create_issue_with_images(self, owner: str, repo: str, title: str, 
                                      body: Optional[str] = None,
                                      images: Optional[List[Union[str, Dict]]] = None,
                                      label_ids: Optional[List[str]] = None,
                                      assignee_ids: Optional[List[str]] = None) -> Dict:
        """Create an issue with embedded images"""
        # First, upload any local images
        image_urls = []
        if images:
            for image in images:
                if isinstance(image, str):
                    # It's a file path, upload it
                    if image.startswith('http://') or image.startswith('https://'):
                        # It's already a URL
                        image_urls.append({'url': image, 'alt': 'Image'})
                    else:
                        # It's a local file, upload it
                        url = await self.upload_image_to_github(owner, repo, image)
                        image_urls.append({'url': url, 'alt': Path(image).name})
                elif isinstance(image, dict):
                    # It has url and possibly alt text
                    if 'path' in image:
                        # Upload local file
                        url = await self.upload_image_to_github(owner, repo, image['path'])
                        image_urls.append({'url': url, 'alt': image.get('alt', Path(image['path']).name)})
                    else:
                        image_urls.append(image)
        
        # Embed images in the body
        if image_urls:
            body = self.embed_images_in_markdown(body or "", image_urls)
        
        # Get repository ID
        repo_id = await self.get_repository_id(owner, repo)
        
        # Create the issue with embedded images
        return await self.create_issue(repo_id, title, body, label_ids, assignee_ids)


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
- create_issue_with_images: Create a new issue with embedded images
- update_issue: Update an existing issue
- delete_issue: Close an issue (GitHub doesn't allow deletion)
- list_projects: List projects in a repository
- get_project_items: Get items in a project
- get_repo_id: Get repository ID for mutations
- add_labels_to_issue: Add labels to an issue
- remove_labels_from_issue: Remove labels from an issue
- add_assignees_to_issue: Add assignees to an issue
- remove_assignees_from_issue: Remove assignees from an issue
- add_issue_to_project: Add an issue to a project
- remove_issue_from_project: Remove an issue from a project
- update_project_item_field: Update project item field (e.g., status/column)
- update_project_item_status: Update project item status (Todo, In Progress, Done, etc.)
- get_repository_labels: Get all labels in a repository with IDs
- get_user_id: Get a GitHub user's ID by username
- get_project_fields: Get fields in a project (for status/columns)

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
            name="create_issue_with_images",
            description="Create a new issue with embedded images",
            inputSchema={
                "type": "object",
                "properties": {
                    "owner": {"type": "string", "description": "Repository owner"},
                    "repo": {"type": "string", "description": "Repository name"},
                    "title": {"type": "string", "description": "Issue title"},
                    "body": {"type": "string", "description": "Issue body/description"},
                    "images": {
                        "type": "array", 
                        "items": {
                            "oneOf": [
                                {"type": "string", "description": "Image file path or URL"},
                                {
                                    "type": "object",
                                    "properties": {
                                        "path": {"type": "string", "description": "Image file path"},
                                        "url": {"type": "string", "description": "Image URL"},
                                        "alt": {"type": "string", "description": "Alt text for image"}
                                    }
                                }
                            ]
                        },
                        "description": "Images to embed (file paths or URLs)"
                    },
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
        ),
        types.Tool(
            name="add_labels_to_issue",
            description="Add labels to an issue",
            inputSchema={
                "type": "object",
                "properties": {
                    "issue_id": {"type": "string", "description": "Issue ID"},
                    "label_ids": {"type": "array", "items": {"type": "string"}, "description": "Label IDs to add"}
                },
                "required": ["issue_id", "label_ids"]
            }
        ),
        types.Tool(
            name="remove_labels_from_issue",
            description="Remove labels from an issue",
            inputSchema={
                "type": "object",
                "properties": {
                    "issue_id": {"type": "string", "description": "Issue ID"},
                    "label_ids": {"type": "array", "items": {"type": "string"}, "description": "Label IDs to remove"}
                },
                "required": ["issue_id", "label_ids"]
            }
        ),
        types.Tool(
            name="add_assignees_to_issue",
            description="Add assignees to an issue",
            inputSchema={
                "type": "object",
                "properties": {
                    "issue_id": {"type": "string", "description": "Issue ID"},
                    "assignee_ids": {"type": "array", "items": {"type": "string"}, "description": "User IDs to assign"}
                },
                "required": ["issue_id", "assignee_ids"]
            }
        ),
        types.Tool(
            name="remove_assignees_from_issue",
            description="Remove assignees from an issue",
            inputSchema={
                "type": "object",
                "properties": {
                    "issue_id": {"type": "string", "description": "Issue ID"},
                    "assignee_ids": {"type": "array", "items": {"type": "string"}, "description": "User IDs to unassign"}
                },
                "required": ["issue_id", "assignee_ids"]
            }
        ),
        types.Tool(
            name="add_issue_to_project",
            description="Add an issue to a GitHub project",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {"type": "string", "description": "Project ID"},
                    "issue_id": {"type": "string", "description": "Issue ID to add"}
                },
                "required": ["project_id", "issue_id"]
            }
        ),
        types.Tool(
            name="remove_issue_from_project",
            description="Remove an issue from a GitHub project",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {"type": "string", "description": "Project ID"},
                    "item_id": {"type": "string", "description": "Project item ID to remove"}
                },
                "required": ["project_id", "item_id"]
            }
        ),
        types.Tool(
            name="update_project_item_field",
            description="Update a project item's field value (e.g., status/column)",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {"type": "string", "description": "Project ID"},
                    "item_id": {"type": "string", "description": "Project item ID"},
                    "field_id": {"type": "string", "description": "Field ID to update"},
                    "value": {"type": "string", "description": "New value for the field (option ID for single-select fields)"}
                },
                "required": ["project_id", "item_id", "field_id", "value"]
            }
        ),
        types.Tool(
            name="update_project_item_status",
            description="Update the status of a project item (e.g., Todo, In Progress, Done)",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {"type": "string", "description": "Project ID"},
                    "item_id": {"type": "string", "description": "Project item ID"},
                    "status": {"type": "string", "description": "Status name (e.g., 'Todo', 'In Progress', 'Done')"}
                },
                "required": ["project_id", "item_id", "status"]
            }
        ),
        types.Tool(
            name="get_repository_labels",
            description="Get all labels in a repository with their IDs",
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
            name="get_user_id",
            description="Get a GitHub user's ID by username",
            inputSchema={
                "type": "object",
                "properties": {
                    "username": {"type": "string", "description": "GitHub username"}
                },
                "required": ["username"]
            }
        ),
        types.Tool(
            name="get_project_fields",
            description="Get fields in a project (including status/column options)",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {"type": "string", "description": "Project ID"}
                },
                "required": ["project_id"]
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
        
        elif name == "create_issue_with_images":
            issue = await github_client.create_issue_with_images(
                arguments["owner"],
                arguments["repo"],
                arguments["title"],
                arguments.get("body"),
                arguments.get("images"),
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
        
        elif name == "add_labels_to_issue":
            result = await github_client.add_labels_to_issue(
                arguments["issue_id"],
                arguments["label_ids"]
            )
            return [types.TextContent(
                type="text",
                text=json.dumps(result, indent=2, default=str)
            )]
        
        elif name == "remove_labels_from_issue":
            result = await github_client.remove_labels_from_issue(
                arguments["issue_id"],
                arguments["label_ids"]
            )
            return [types.TextContent(
                type="text",
                text=json.dumps(result, indent=2, default=str)
            )]
        
        elif name == "add_assignees_to_issue":
            result = await github_client.add_assignees_to_issue(
                arguments["issue_id"],
                arguments["assignee_ids"]
            )
            return [types.TextContent(
                type="text",
                text=json.dumps(result, indent=2, default=str)
            )]
        
        elif name == "remove_assignees_from_issue":
            result = await github_client.remove_assignees_from_issue(
                arguments["issue_id"],
                arguments["assignee_ids"]
            )
            return [types.TextContent(
                type="text",
                text=json.dumps(result, indent=2, default=str)
            )]
        
        elif name == "add_issue_to_project":
            result = await github_client.add_issue_to_project(
                arguments["project_id"],
                arguments["issue_id"]
            )
            return [types.TextContent(
                type="text",
                text=json.dumps(result, indent=2, default=str)
            )]
        
        elif name == "remove_issue_from_project":
            success = await github_client.remove_issue_from_project(
                arguments["project_id"],
                arguments["item_id"]
            )
            return [types.TextContent(
                type="text",
                text=json.dumps({"success": success, "message": "Item removed from project" if success else "Failed to remove item"})
            )]
        
        elif name == "update_project_item_field":
            result = await github_client.update_project_item_field(
                arguments["project_id"],
                arguments["item_id"],
                arguments["field_id"],
                arguments["value"]
            )
            return [types.TextContent(
                type="text",
                text=json.dumps(result, indent=2, default=str)
            )]
        
        elif name == "update_project_item_status":
            result = await github_client.update_project_item_status(
                arguments["project_id"],
                arguments["item_id"],
                arguments["status"]
            )
            return [types.TextContent(
                type="text",
                text=json.dumps(result, indent=2, default=str)
            )]
        
        elif name == "get_repository_labels":
            labels = await github_client.get_repository_labels(
                arguments["owner"],
                arguments["repo"]
            )
            return [types.TextContent(
                type="text",
                text=json.dumps(labels, indent=2, default=str)
            )]
        
        elif name == "get_user_id":
            user_id = await github_client.get_user_id(arguments["username"])
            return [types.TextContent(
                type="text",
                text=json.dumps({"user_id": user_id, "username": arguments["username"]})
            )]
        
        elif name == "get_project_fields":
            fields = await github_client.get_project_fields(arguments["project_id"])
            return [types.TextContent(
                type="text",
                text=json.dumps(fields, indent=2, default=str)
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