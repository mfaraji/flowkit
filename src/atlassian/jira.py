#!/usr/bin/env python3
"""
Jira utilities for managing Jira operations using the official jira library.
"""

from typing import Optional, Dict, Any, List

try:
    from jira import JIRA
    from jira.exceptions import JIRAError
except ImportError as e:
    print(f"Error: Missing required dependencies. Please install them using:")
    print("pip install jira")
    import sys
    sys.exit(1)


class Jira:
    """
    Utility class for Jira operations using the official jira library.
    """
    
    def __init__(self, base_url: str, username: str, api_token: str):
        """
        Initialize the Jira interface.

        Args:
            base_url: The base URL of your Jira instance (e.g., 'https://yourcompany.atlassian.net')
            username: Your Jira username (email)
            api_token: Your Jira API token
        """
        self.base_url = base_url.rstrip('/')
        self.username = username
        self.api_token = api_token
        self.jira = None
        self._connect()

    def _connect(self) -> bool:
        """
        Connect to Jira using the official library.

        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            self.jira = JIRA(
                server=self.base_url,
                basic_auth=(self.username, self.api_token)
            )
            return True
        except JIRAError as e:
            print(f"✗ Jira connection error: {e}")
            return False
        except Exception as e:
            print(f"✗ Connection error: {e}")
            return False

    def get_issue(self, issue_key: str, fields: str = None) -> Optional[Any]:
        """
        Get a Jira issue by its key.

        Args:
            issue_key: The issue key (e.g., 'PROJ-123')
            fields: Comma-separated list of fields to retrieve (optional)

        Returns:
            Issue object, or None if error
        """
        try:
            if not self.jira:
                if not self._connect():
                    return None
            
            issue = self.jira.issue(issue_key, fields=fields)
            print(f"✓ Retrieved issue: {issue.key} - {issue.fields.summary}")
            return issue
        except JIRAError as e:
            print(f"✗ Failed to get issue {issue_key}: {e}")
            return None
        except Exception as e:
            print(f"✗ Error getting issue {issue_key}: {e}")
            return None

    def search_issues(self, jql: str, max_results: int = 50, fields: str = None) -> Optional[List[Any]]:
        """
        Search for issues using JQL (Jira Query Language).

        Args:
            jql: JQL query string
            max_results: Maximum number of results to return
            fields: Comma-separated list of fields to retrieve (optional)

        Returns:
            List of issue objects, or None if error
        """
        try:
            if not self.jira:
                if not self._connect():
                    return None
            
            issues = self.jira.search_issues(
                jql_str=jql,
                maxResults=max_results,
                fields=fields
            )
            
            print(f"✓ Found {len(issues)} issues")
            return issues
        except JIRAError as e:
            print(f"✗ Search failed: {e}")
            return None
        except Exception as e:
            print(f"✗ Search error: {e}")
            return None

    def create_issue(self, project_key: str, summary: str, description: str, 
                     issue_type: str = "Task", **kwargs) -> Optional[Any]:
        """
        Create a new Jira issue.

        Args:
            project_key: The project key (e.g., 'PROJ')
            summary: Issue summary/title
            description: Issue description
            issue_type: Issue type (default: "Task")
            **kwargs: Additional fields for the issue

        Returns:
            The created issue object, or None if error
        """
        try:
            if not self.jira:
                if not self._connect():
                    return None

            issue_dict = {
                'project': {'key': project_key},
                'summary': summary,
                'description': description,
                'issuetype': {'name': issue_type}
            }
            
            # Add any additional fields
            issue_dict.update(kwargs)

            issue = self.jira.create_issue(fields=issue_dict)
            print(f"✓ Created issue: {issue.key} - {issue.fields.summary}")
            return issue
        except JIRAError as e:
            print(f"✗ Failed to create issue: {e}")
            return None
        except Exception as e:
            print(f"✗ Error creating issue: {e}")
            return None

    def get_projects(self) -> Optional[List[Any]]:
        """
        Get all accessible projects.

        Returns:
            List of project objects, or None if error
        """
        try:
            if not self.jira:
                if not self._connect():
                    return None
            
            projects = self.jira.projects()
            print(f"✓ Found {len(projects)} projects")
            return projects
        except JIRAError as e:
            print(f"✗ Failed to get projects: {e}")
            return None
        except Exception as e:
            print(f"✗ Error getting projects: {e}")
            return None

    def get_project(self, project_key: str) -> Optional[Any]:
        """
        Get a specific project by key.

        Args:
            project_key: The project key (e.g., 'PROJ')

        Returns:
            Project object, or None if error
        """
        try:
            if not self.jira:
                if not self._connect():
                    return None
            
            project = self.jira.project(project_key)
            print(f"✓ Retrieved project: {project.key} - {project.name}")
            return project
        except JIRAError as e:
            print(f"✗ Failed to get project {project_key}: {e}")
            return None
        except Exception as e:
            print(f"✗ Error getting project {project_key}: {e}")
            return None

    def update_issue(self, issue_key: str, fields: Dict[str, Any]) -> bool:
        """
        Update an existing issue.

        Args:
            issue_key: The issue key (e.g., 'PROJ-123')
            fields: Dictionary of fields to update

        Returns:
            True if successful, False otherwise
        """
        try:
            if not self.jira:
                if not self._connect():
                    return False
            
            issue = self.jira.issue(issue_key)
            issue.update(fields=fields)
            print(f"✓ Updated issue: {issue_key}")
            return True
        except JIRAError as e:
            print(f"✗ Failed to update issue {issue_key}: {e}")
            return False
        except Exception as e:
            print(f"✗ Error updating issue {issue_key}: {e}")
            return False

    def add_comment(self, issue_key: str, comment: str) -> bool:
        """
        Add a comment to an issue.

        Args:
            issue_key: The issue key (e.g., 'PROJ-123')
            comment: Comment text

        Returns:
            True if successful, False otherwise
        """
        try:
            if not self.jira:
                if not self._connect():
                    return False
            
            self.jira.add_comment(issue_key, comment)
            print(f"✓ Added comment to issue: {issue_key}")
            return True
        except JIRAError as e:
            print(f"✗ Failed to add comment to {issue_key}: {e}")
            return False
        except Exception as e:
            print(f"✗ Error adding comment to {issue_key}: {e}")
            return False

    def get_issue_types(self) -> Optional[List[Any]]:
        """
        Get all available issue types.

        Returns:
            List of issue type objects, or None if error
        """
        try:
            if not self.jira:
                if not self._connect():
                    return None
            
            issue_types = self.jira.issue_types()
            print(f"✓ Found {len(issue_types)} issue types")
            return issue_types
        except JIRAError as e:
            print(f"✗ Failed to get issue types: {e}")
            return None
        except Exception as e:
            print(f"✗ Error getting issue types: {e}")
            return None

    def get_users_with_roles(self, project_key: str = None, include_groups: bool = True) -> Optional[List[Dict[str, Any]]]:
        """
        Get users with their roles and groups.

        Args:
            project_key: Optional project key to get project-specific roles (e.g., 'PROJ')
            include_groups: Whether to include group membership information

        Returns:
            List of user dictionaries with role information, or None if error
        """
        try:
            if not self.jira:
                if not self._connect():
                    return None
            
            users_with_roles = []
            
            if project_key:
                # Get project-specific roles
                try:
                    project_roles = self.jira.project_roles(project_key)
                    print(f"✓ Found {len(project_roles)} project roles for {project_key}")
                    
                    for role_name, role_url in project_roles.items():
                        try:
                            # Get role actors (users and groups) for this role
                            # Handle both URL string and dict formats
                            if isinstance(role_url, str):
                                role_id = role_url.split('/')[-1]
                            elif isinstance(role_url, dict):
                                role_id = str(role_url.get('id', ''))
                            else:
                                print(f"✗ Unexpected role_url format for {role_name}: {type(role_url)}")
                                continue
                                
                            if not role_id:
                                print(f"✗ Could not extract role ID for {role_name}")
                                continue
                                
                            role_actors = self.jira.project_role(project_key, role_id)
                            
                            for actor in role_actors.actors:
                                if actor.type == 'atlassian-user-role-actor':
                                    user_info = {
                                        'user_key': actor.actorUser.key if hasattr(actor, 'actorUser') else 'N/A',
                                        'user_name': actor.actorUser.name if hasattr(actor, 'actorUser') else actor.name,
                                        'display_name': actor.actorUser.displayName if hasattr(actor, 'actorUser') else actor.displayName,
                                        'email': getattr(actor.actorUser, 'emailAddress', 'N/A') if hasattr(actor, 'actorUser') else 'N/A',
                                        'project_key': project_key,
                                        'role': role_name,
                                        'role_id': role_id,
                                        'type': 'project_role'
                                    }
                                    users_with_roles.append(user_info)
                        except Exception as role_error:
                            print(f"✗ Error getting actors for role {role_name}: {role_error}")
                            continue
                            
                except Exception as e:
                    print(f"✗ Error getting project roles for {project_key}: {e}")
                    return None
            else:
                # Get all users if no specific project
                try:
                    # Search for all users (this might be limited based on Jira permissions)
                    # Use a wildcard search or search for active users
                    try:
                        users = self.jira.search_users('', maxResults=1000)
                    except Exception:
                        # Fallback: try searching with a dot (common in email addresses)
                        users = self.jira.search_users('.', maxResults=1000)
                    
                    for user in users:
                        user_info = {
                            'user_key': user.key,
                            'user_name': user.name,
                            'display_name': user.displayName,
                            'email': getattr(user, 'emailAddress', 'N/A'),
                            'active': user.active,
                            'type': 'global_user'
                        }
                        
                        # Add group information if requested
                        if include_groups:
                            try:
                                user_groups = self.jira.user_groups(user.name)
                                user_info['groups'] = [group.name for group in user_groups]
                            except Exception as group_error:
                                user_info['groups'] = []
                                print(f"✗ Could not get groups for user {user.name}: {group_error}")
                        
                        users_with_roles.append(user_info)
                        
                except Exception as e:
                    print(f"✗ Error getting users: {e}")
                    # Fallback: try to get users through groups
                    try:
                        groups = self.jira.groups()
                        users_seen = set()
                        
                        for group in groups:
                            try:
                                # Handle different group object types
                                if hasattr(group, 'name'):
                                    group_name = group.name
                                elif isinstance(group, str):
                                    group_name = group
                                elif isinstance(group, dict):
                                    group_name = group.get('name', str(group))
                                else:
                                    group_name = str(group)
                                    
                                group_members = self.jira.group_members(group_name)
                                for member in group_members:
                                    # Handle different member object types
                                    if hasattr(member, 'key'):
                                        member_key = member.key
                                        member_name = getattr(member, 'name', 'N/A')
                                        member_display_name = getattr(member, 'displayName', member_name)
                                        member_email = getattr(member, 'emailAddress', 'N/A')
                                        member_active = getattr(member, 'active', True)
                                    elif isinstance(member, str):
                                        # Member is just a string (possibly account ID or username)
                                        member_key = member
                                        member_name = member
                                        member_display_name = member
                                        member_email = 'N/A'
                                        member_active = True
                                    elif isinstance(member, dict):
                                        member_key = member.get('accountId') or member.get('key') or member.get('name', 'unknown')
                                        member_name = member.get('name', member_key)
                                        member_display_name = member.get('displayName', member_name)
                                        member_email = member.get('emailAddress', 'N/A')
                                        member_active = member.get('active', True)
                                    else:
                                        # Skip unknown member types
                                        continue
                                        
                                    if member_key not in users_seen:
                                        user_info = {
                                            'user_key': member_key,
                                            'user_name': member_name,
                                            'display_name': member_display_name,
                                            'email': member_email,
                                            'active': member_active,
                                            'groups': [group_name],
                                            'type': 'group_member'
                                        }
                                        users_with_roles.append(user_info)
                                        users_seen.add(member_key)
                                    else:
                                        # User already exists, just add the group
                                        for existing_user in users_with_roles:
                                            if existing_user['user_key'] == member_key:
                                                if 'groups' not in existing_user:
                                                    existing_user['groups'] = []
                                                existing_user['groups'].append(group_name)
                                                break
                            except Exception as group_error:
                                print(f"✗ Could not get members for group {group_name}: {group_error}")
                                continue
                    except Exception as groups_error:
                        print(f"✗ Error with fallback groups method: {groups_error}")
                        return None
            
            print(f"✓ Found {len(users_with_roles)} users with role information")
            return users_with_roles
            
        except JIRAError as e:
            print(f"✗ Failed to get users with roles: {e}")
            return None
        except Exception as e:
            print(f"✗ Error getting users with roles: {e}")
            return None

    def get_groups(self) -> Optional[List[Any]]:
        """
        Get all available groups.

        Returns:
            List of group objects, or None if error
        """
        try:
            if not self.jira:
                if not self._connect():
                    return None
            
            groups = self.jira.groups()
            print(f"✓ Found {len(groups)} groups")
            return groups
        except JIRAError as e:
            print(f"✗ Failed to get groups: {e}")
            return None
        except Exception as e:
            print(f"✗ Error getting groups: {e}")
            return None

    def get_group_members(self, group_name: str) -> Optional[List[Any]]:
        """
        Get members of a specific group.

        Args:
            group_name: Name of the group

        Returns:
            List of user objects in the group, or None if error
        """
        try:
            if not self.jira:
                if not self._connect():
                    return None
            
            members = self.jira.group_members(group_name)
            print(f"✓ Found {len(members)} members in group '{group_name}'")
            return members
        except JIRAError as e:
            print(f"✗ Failed to get members for group '{group_name}': {e}")
            return None
        except Exception as e:
            print(f"✗ Error getting group members: {e}")
            return None

    def get_project_components(self, project_key: str) -> Optional[List[Dict[str, Any]]]:
        """
        Get all components for a specific project.

        Args:
            project_key: The project key (e.g., 'PROJ')

        Returns:
            List of component dictionaries with details, or None if error
        """
        try:
            if not self.jira:
                if not self._connect():
                    return None
            
            # Get the project first to validate it exists
            try:
                project = self.jira.project(project_key)
            except JIRAError as e:
                print(f"✗ Project '{project_key}' not found: {e}")
                return None
            
            # Get project components
            components = self.jira.project_components(project_key)
            
            # Convert components to a more usable format
            component_list = []
            for component in components:
                # Handle component lead (can be None or a User object)
                if hasattr(component, 'lead') and component.lead:
                    lead_display_name = getattr(component.lead, 'displayName', 'Unknown')
                    lead_username = getattr(component.lead, 'name', 'N/A')
                else:
                    lead_display_name = 'No lead assigned'
                    lead_username = 'N/A'
                
                component_info = {
                    'id': component.id,
                    'name': component.name,
                    'description': getattr(component, 'description', 'No description'),
                    'lead': lead_display_name,
                    'lead_username': lead_username,
                    'assignee_type': getattr(component, 'assigneeType', 'UNASSIGNED'),
                    'is_assignee_type_valid': getattr(component, 'isAssigneeTypeValid', False),
                    'project_key': project_key,
                    'project_name': project.name
                }
                component_list.append(component_info)
            
            print(f"✓ Found {len(component_list)} components in project '{project_key}'")
            return component_list
            
        except JIRAError as e:
            print(f"✗ Failed to get components for project '{project_key}': {e}")
            return None
        except Exception as e:
            print(f"✗ Error getting project components: {e}")
            return None

    def create_component(self, project_key: str, name: str, description: str = None, 
                        lead: str = None, assignee_type: str = "UNASSIGNED") -> Optional[Any]:
        """
        Create a new component in a project.

        Args:
            project_key: The project key (e.g., 'PROJ')
            name: Component name
            description: Component description (optional)
            lead: Component lead username (optional)
            assignee_type: Assignee type - UNASSIGNED, COMPONENT_LEAD, PROJECT_LEAD, PROJECT_DEFAULT

        Returns:
            The created component object, or None if error
        """
        try:
            if not self.jira:
                if not self._connect():
                    return None
            
            component_dict = {
                'name': name,
                'project': project_key,
                'assigneeType': assignee_type
            }
            
            if description:
                component_dict['description'] = description
            
            if lead:
                # Try to find the user first
                try:
                    user = self.jira.user(lead)
                    component_dict['lead'] = {'name': user.name}
                except Exception as user_error:
                    print(f"✗ Warning: Could not find user '{lead}': {user_error}")
                    print(f"  Creating component without lead assignment")
            
            component = self.jira.create_component(component_dict)
            print(f"✓ Created component: {component.name} in project {project_key}")
            return component
            
        except JIRAError as e:
            print(f"✗ Failed to create component '{name}' in project '{project_key}': {e}")
            return None
        except Exception as e:
            print(f"✗ Error creating component: {e}")
            return None

    def update_component(self, component_id: str, name: str = None, description: str = None,
                        lead: str = None, assignee_type: str = None) -> bool:
        """
        Update an existing component.

        Args:
            component_id: The component ID
            name: New component name (optional)
            description: New component description (optional)
            lead: New component lead username (optional)
            assignee_type: New assignee type (optional)

        Returns:
            True if successful, False otherwise
        """
        try:
            if not self.jira:
                if not self._connect():
                    return False
            
            # Get the existing component
            component = self.jira.component(component_id)
            update_dict = {}
            
            if name:
                update_dict['name'] = name
            if description:
                update_dict['description'] = description
            if assignee_type:
                update_dict['assigneeType'] = assignee_type
            if lead:
                try:
                    user = self.jira.user(lead)
                    update_dict['lead'] = {'name': user.name}
                except Exception as user_error:
                    print(f"✗ Warning: Could not find user '{lead}': {user_error}")
                    return False
            
            component.update(fields=update_dict)
            print(f"✓ Updated component: {component.name}")
            return True
            
        except JIRAError as e:
            print(f"✗ Failed to update component '{component_id}': {e}")
            return False
        except Exception as e:
            print(f"✗ Error updating component: {e}")
            return False

    def get_project_custom_fields(self, project_key: str) -> Optional[List[Dict[str, Any]]]:
        """
        Get all custom fields used in a specific project.

        Args:
            project_key: The project key (e.g., 'PROJ')

        Returns:
            List of custom field dictionaries with details, or None if error
        """
        try:
            if not self.jira:
                if not self._connect():
                    return None
            
            # Get the project first to validate it exists
            try:
                project = self.jira.project(project_key)
            except JIRAError as e:
                print(f"✗ Project '{project_key}' not found: {e}")
                return None
            
            # Get all fields first
            all_fields = self.jira.fields()
            
            # Filter for custom fields (custom fields have IDs that start with "customfield_")
            custom_fields = [field for field in all_fields if field['id'].startswith('customfield_')]
            
            # Now we need to check which custom fields are actually used in this project
            # We'll do this by getting the project's field configuration or checking issues
            project_custom_fields = []
            
            try:
                # Try to get project configuration to see which fields are available
                # First, try to get some issues from the project to see which fields are in use
                sample_issues = self.jira.search_issues(
                    f'project = {project_key}',
                    maxResults=50,
                    fields='*all'
                )
                
                # Collect all field IDs that appear in issues
                used_field_ids = set()
                for issue in sample_issues:
                    # Get all field IDs from the issue
                    for field_id in issue.raw['fields'].keys():
                        if field_id.startswith('customfield_'):
                            used_field_ids.add(field_id)
                
                # Match used field IDs with custom field definitions
                for custom_field in custom_fields:
                    if custom_field['id'] in used_field_ids:
                        # Get more details about the field
                        field_info = {
                            'id': custom_field['id'],
                            'name': custom_field['name'],
                            'custom': custom_field.get('custom', True),
                            'orderable': custom_field.get('orderable', False),
                            'navigable': custom_field.get('navigable', True),
                            'searchable': custom_field.get('searchable', True),
                            'clause_names': custom_field.get('clauseNames', []),
                            'schema': custom_field.get('schema', {}),
                            'project_key': project_key,
                            'project_name': project.name
                        }
                        
                        # Try to get field type information
                        schema = custom_field.get('schema', {})
                        if schema:
                            field_info['field_type'] = schema.get('type', 'Unknown')
                            field_info['system'] = schema.get('system', 'Unknown')
                            field_info['items'] = schema.get('items', 'N/A')
                        else:
                            field_info['field_type'] = 'Unknown'
                            field_info['system'] = 'Unknown'
                            field_info['items'] = 'N/A'
                        
                        project_custom_fields.append(field_info)
                
                if not project_custom_fields:
                    # If no custom fields found in issues, return all available custom fields
                    # This might happen if there are no issues or no custom fields in use
                    print(f"✓ No custom fields found in issues for project '{project_key}'")
                    print(f"✓ Returning all available custom fields ({len(custom_fields)} total)")
                    for custom_field in custom_fields:
                        field_info = {
                            'id': custom_field['id'],
                            'name': custom_field['name'],
                            'custom': custom_field.get('custom', True),
                            'orderable': custom_field.get('orderable', False),
                            'navigable': custom_field.get('navigable', True),
                            'searchable': custom_field.get('searchable', True),
                            'clause_names': custom_field.get('clauseNames', []),
                            'schema': custom_field.get('schema', {}),
                            'project_key': project_key,
                            'project_name': project.name
                        }
                        
                        # Try to get field type information
                        schema = custom_field.get('schema', {})
                        if schema:
                            field_info['field_type'] = schema.get('type', 'Unknown')
                            field_info['system'] = schema.get('system', 'Unknown')
                            field_info['items'] = schema.get('items', 'N/A')
                        else:
                            field_info['field_type'] = 'Unknown'
                            field_info['system'] = 'Unknown' 
                            field_info['items'] = 'N/A'
                        
                        project_custom_fields.append(field_info)
                    
            except Exception as search_error:
                print(f"✗ Could not search issues to determine used fields: {search_error}")
                # Fallback: return all custom fields
                for custom_field in custom_fields:
                    field_info = {
                        'id': custom_field['id'],
                        'name': custom_field['name'],
                        'custom': custom_field.get('custom', True),
                        'orderable': custom_field.get('orderable', False),
                        'navigable': custom_field.get('navigable', True),
                        'searchable': custom_field.get('searchable', True),
                        'clause_names': custom_field.get('clauseNames', []),
                        'schema': custom_field.get('schema', {}),
                        'project_key': project_key,
                        'project_name': project.name
                    }
                    
                    # Try to get field type information
                    schema = custom_field.get('schema', {})
                    if schema:
                        field_info['field_type'] = schema.get('type', 'Unknown')
                        field_info['system'] = schema.get('system', 'Unknown')
                        field_info['items'] = schema.get('items', 'N/A')
                    else:
                        field_info['field_type'] = 'Unknown'
                        field_info['system'] = 'Unknown' 
                        field_info['items'] = 'N/A'
                    
                    project_custom_fields.append(field_info)
            
            print(f"✓ Found {len(project_custom_fields)} custom fields for project '{project_key}'")
            return project_custom_fields
            
        except JIRAError as e:
            print(f"✗ Failed to get custom fields for project '{project_key}': {e}")
            return None
        except Exception as e:
            print(f"✗ Error getting project custom fields: {e}")
            return None 