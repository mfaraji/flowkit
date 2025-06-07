# FlowKit - Atlassian Automation SDK

A comprehensive Python SDK for automating Jira and Confluence operations. FlowKit provides easy-to-use clients for managing tickets, components, custom fields, spaces, and content across your Atlassian ecosystem.

## 🚀 Features

### 🎫 **Jira Integration**
- **Issue Management**: Create, update, search, and manage Jira tickets
- **Component Operations**: List, create, and manage project components  
- **Custom Fields**: Discover and analyze custom fields across projects
- **User & Group Management**: Retrieve users, roles, and group memberships
- **Project Operations**: Access project details and configurations
- **Advanced Search**: Powerful JQL-based issue searching

### 📚 **Confluence Integration**
- **Space Management**: List and browse Confluence spaces
- **Content Search**: Advanced search with CQL support and default space configuration
- **Content Discovery**: Browse pages, blog posts, and attachments
- **Rich Metadata**: Extract excerpts, labels, creators, and timestamps
- **Flexible Filtering**: Search by content type, space, and custom criteria

### 🛠️ **Developer-Friendly**
- **Interactive Examples**: Ready-to-run demo scripts
- **Comprehensive Error Handling**: Graceful fallbacks and detailed error messages
- **Flexible Configuration**: Environment-based setup with .env support
- **Rich Output**: Beautiful console output with emojis and formatting

## 📦 Installation

### Prerequisites
- Python 3.7+
- Poetry (recommended) or pip

### Install Dependencies

```bash
# Using Poetry (recommended)
poetry install

# Using pip
pip install -r requirements.txt
```

### Required Dependencies
- `jira` - Official Jira Python library
- `requests` - HTTP library for Confluence API
- `python-dotenv` - Environment variable management

## ⚙️ Configuration

### 1. Create Environment File
```bash
cp .env.example .env
```

### 2. Configure Credentials
Edit `.env` with your Atlassian credentials:

```env
# Jira Configuration
JIRA_BASE_URL=https://yourcompany.atlassian.net
JIRA_USERNAME=your.email@company.com
JIRA_API_TOKEN=your_jira_api_token

# Confluence Configuration  
CONFLUENCE_BASE_URL=https://yourcompany.atlassian.net/wiki
CONFLUENCE_USERNAME=your.email@company.com
CONFLUENCE_API_TOKEN=your_confluence_api_token
```

### 3. Generate API Tokens
Get your API tokens from: https://id.atlassian.com/manage-profile/security/api-tokens

## 🎯 Quick Start

### Jira Operations

```python
from src.atlassian.jira import Jira

# Initialize client
jira = Jira(base_url, username, api_token)

# Test connection
if jira.test_connection():
    print("Connected to Jira!")

# Create a ticket
issue = jira.create_issue(
    project_key="PROJ",
    summary="Sample Issue",
    description="Created via FlowKit",
    issue_type="Task"
)

# Search issues
issues = jira.search_issues("project = PROJ AND status = Open")

# Get project components
components = jira.get_project_components("PROJ")

# List custom fields
custom_fields = jira.get_project_custom_fields("PROJ")
```

### Confluence Operations

```python
from src.atlassian.confluence import Confluence

# Initialize client with default space
confluence = Confluence(base_url, username, api_token, default_space="ENG")

# Test connection
if confluence.test_connection():
    print("Connected to Confluence!")

# Search in default space
results = confluence.search_content("API documentation")

# Search in specific space
results = confluence.search_in_space("TECH", "deployment guide")

# Get all spaces
spaces = confluence.get_spaces()

# Browse space content
pages = confluence.get_space_content("ENG", content_type="page")
```

## 📋 Example Scripts

FlowKit includes comprehensive example scripts to demonstrate functionality:

### Jira Examples

```bash
# Component management demo
poetry run python examples/jira_components_example.py

# User and roles exploration  
poetry run python examples/jira_users_example.py
```

### Confluence Examples

```bash
# Search and content discovery
poetry run python examples/confluence_search_example.py
```

## 🔧 API Reference

### Jira Client Methods

#### **Connection & Authentication**
- `test_connection()` - Verify Jira connectivity
- `get_projects()` - List accessible projects
- `get_project(project_key)` - Get specific project details

#### **Issue Operations**
- `get_issue(issue_key, fields=None)` - Retrieve specific issue
- `search_issues(jql, max_results=50)` - Search with JQL
- `create_issue(project_key, summary, description, issue_type="Task", **kwargs)` - Create new issue
- `update_issue(issue_key, fields)` - Update existing issue
- `add_comment(issue_key, comment)` - Add comment to issue

#### **Component Management**
- `get_project_components(project_key)` - List project components
- `create_component(project_key, name, description=None, lead=None)` - Create component
- `update_component(component_id, **updates)` - Update component

#### **Custom Fields & Metadata**
- `get_project_custom_fields(project_key)` - Analyze project custom fields
- `get_issue_types()` - List available issue types
- `get_users_with_roles(project_key=None)` - Get users and their roles
- `get_groups()` - List user groups
- `get_group_members(group_name)` - Get group membership

### Confluence Client Methods

#### **Connection & Spaces**
- `test_connection()` - Verify Confluence connectivity
- `get_spaces()` - List accessible spaces

#### **Content Search & Discovery**
- `search_content(query, space_key=None, content_type=None, limit=25)` - Advanced content search
- `search_in_space(space_key, query, content_type=None)` - Space-specific search  
- `get_space_content(space_key, content_type="page")` - Browse space content

#### **Advanced Features**
- **Default Space Support**: Automatically search in configured default space
- **CQL Integration**: Use Confluence Query Language for powerful searches
- **Rich Metadata**: Extract excerpts, labels, creation dates, and more
- **Content Type Filtering**: Search pages, blog posts, attachments separately

## 🎨 Output Examples

### Jira Component Listing
```
🔧 Component 1:
   ID: 12345
   Name: Frontend
   Description: User interface components
   Lead: John Doe (john.doe)
   Assignee Type: COMPONENT_LEAD
   Project: My Project (PROJ)
```

### Confluence Search Results
```
📄 Result 1:
   Title: API Authentication Guide
   Type: page
   Space: Engineering (ENG)
   URL: https://company.atlassian.net/wiki/spaces/ENG/pages/123456
   Creator: Jane Smith
   Excerpt: Learn how to authenticate with our API using OAuth 2.0...
   Labels: api, authentication, oauth
```

## 🛡️ Error Handling

FlowKit includes comprehensive error handling:

- **Connection Issues**: Clear feedback on authentication problems
- **Permission Errors**: Graceful handling of access restrictions  
- **API Limits**: Automatic pagination and rate limiting respect
- **Field Validation**: Smart field availability checking
- **Fallback Strategies**: Multiple approaches for component assignment

## 🤝 Contributing

### Development Setup
```bash
# Clone repository
git clone <repository-url>
cd flowkit

# Install dependencies
poetry install

# Run examples
poetry run python examples/jira_components_example.py
```

### Adding New Features
1. Add methods to appropriate client class (`Jira` or `Confluence`)
2. Include comprehensive error handling
3. Add example usage in relevant example script
4. Update this README with new functionality

## 📄 License

MIT License - see [LICENSE](./LICENSE) for details.

## 🙋 Support

For issues, questions, or contributions:
1. Check existing functionality in example scripts
2. Review error messages for troubleshooting guidance
3. Ensure API tokens have necessary permissions
4. Verify base URLs and project/space keys are correct

---

**FlowKit** - Streamlining Atlassian automation, one API call at a time! 🚀 