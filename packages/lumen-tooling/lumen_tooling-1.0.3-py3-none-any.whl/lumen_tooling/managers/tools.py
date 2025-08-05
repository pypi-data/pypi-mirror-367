"""
File: /managers/tools.py
Created Date: Tuesday July 29th 2025
Author: Harsh Kumar <fyo9329@gmail.com>
-----
Last Modified: Tuesday July 29th 2025
Modified By: the developer formerly known as Harsh Kumar at <fyo9329@gmail.com>
-----
"""

from typing import Optional, Dict, Any, List
from openai.types.chat import ChatCompletionToolParam

from lumen_tooling.constants import ACTION_METADATA
from ..exceptions import LumenError
from ..tool_function import ToolFunction


class ToolsManager:
    """
    Manager for tool-related operations including schema retrieval and function creation.
    
    This manager handles the complex logic of converting action constants to callable
    tool functions and managing tool schemas for OpenAI integration.
    """
    
    FRIENDLY_NAME_TO_ACTION = {
        metadata["friendly_name"]: action 
        for action, metadata in ACTION_METADATA.items()
    }

    def __init__(self, client):
        """
        Initialize tools manager.
        
        Args:
            client: LumenClient instance for API communication
        """
        self.client = client

    def get_action_metadata(self, action: str) -> Dict[str, str]:
        """
        Get metadata for an action constant.
        
        Args:
            action: Action constant (e.g., Action.GMAIL_SEND_EMAIL)
            
        Returns:
            Dictionary with provider, service, and friendly_name
            
        Raises:
            ValueError: If action is not found
        """
        if action not in ACTION_METADATA:
            available_actions = list(ACTION_METADATA.keys())[:5]
            raise ValueError(
                f"Unknown action: {action}. "
                f"Available actions include: {available_actions}..."
            )
        
        return ACTION_METADATA[action].copy()

    async def get(self, user_id: str, tools: Optional[List[str]] = None) -> List[ChatCompletionToolParam]:
        """
        Get tool schemas from action constants or app constants.
        
        Args:
            tools: List of action constants (e.g., [Action.GMAIL_SEND_EMAIL])
                or app constants (e.g., [App.GMAIL, App.DRIVE])
                or None to get all available tools
            user_id: User ID to fetch user-specific available actions when tools is None
                
        Returns:
            List of ChatCompletionToolParam objects for OpenAI integration
            
        Raises:
            ValueError: If tools parameter is invalid
            LumenError: If schema retrieval fails
        """
        from lumen_tooling.constants import APP_TO_ACTIONS
        
        # If no specific tools requested, get all available actions for the user
        if tools is None:
            if user_id:
                return await self._get_user_available_actions(user_id)
            else:
                # Fallback to all predefined actions if no user_id provided
                validated_tools = list(ACTION_METADATA.keys())
        else:
            validated_tools = self._validate_and_prepare_tools(tools)
    
        tool_schemas: List[ChatCompletionToolParam] = []
        processed_providers = set()
        
        for tool in validated_tools:
            if tool in APP_TO_ACTIONS:
                await self._process_app_constant(tool, tool_schemas, processed_providers)
            else:
                await self._process_action_constant(tool, tool_schemas)
        
        if not tool_schemas:
            raise ValueError("No valid tool schemas could be retrieved")
        
        return tool_schemas

    async def _get_user_available_actions(self, user_id: str) -> List[ChatCompletionToolParam]:
        """
        Get all available actions for a specific user based on their authenticated connections.
        
        Args:
            user_id: User ID to fetch available actions for
            
        Returns:
            List of ChatCompletionToolParam objects for user's available actions
            
        Raises:
            LumenError: If API request fails
        """
        try:
            # Get user's available actions from the API endpoint
            available_actions = await self.client._make_request(
                method="GET",
                endpoint="/actions/",
                params={"user_id": user_id}
            )
            
            tool_schemas: List[ChatCompletionToolParam] = []
            
            # Convert each action to ChatCompletionToolParam format
            for action in available_actions:
                if isinstance(action, dict) and "function" in action:
                    # Action already has the correct structure
                    schema = {"type": "function", "function": action["function"]}
                elif isinstance(action, dict):
                    # Action needs to be wrapped in function structure
                    schema = {"type": "function", "function": action}
                else:
                    continue  # Skip invalid actions
                
                try:
                    tool_schemas.append(ChatCompletionToolParam(**schema))
                except Exception as e:
                    print(f"Warning: Could not create tool schema for action: {str(e)}")
                    continue
            
            return tool_schemas
            
        except Exception as e:
            print(f"Warning: Could not fetch user available actions, falling back to all actions: {str(e)}")
            # Fallback to all predefined actions if API call fails
            return await self._get_all_predefined_actions()

    async def _get_all_predefined_actions(self) -> List[ChatCompletionToolParam]:
        """
        Get all predefined actions as a fallback when user-specific actions can't be retrieved.
        
        Returns:
            List of ChatCompletionToolParam objects for all predefined actions
        """
        tool_schemas: List[ChatCompletionToolParam] = []
        processed_providers = set()
        
        for action in ACTION_METADATA.keys():
            try:
                await self._process_action_constant(action, tool_schemas)
            except Exception as e:
                print(f"Warning: Could not process predefined action '{action}': {str(e)}")
                continue
        
        return tool_schemas

    async def get_functions(
        self,
        user_id: str,
        tools: Optional[List[str]] = None,
        connection_id: Optional[str] = None
    ) -> Dict[str, ToolFunction]:
        """
        Get multiple ToolFunction objects for direct execution.
        
        Args:
            user_id: User ID for function execution
            tools: List of action constants or app constants, or None for all tools
            connection_id: Optional connection ID for the functions
            
        Returns:
            Dictionary mapping action constants to ToolFunction objects
            
        Raises:
            ValueError: If parameters are invalid
            LumenError: If function creation fails
        """
        from lumen_tooling.constants import APP_TO_ACTIONS
        
        self._validate_user_id(user_id)
        validated_tools = self._validate_and_prepare_tools(tools)
        
        functions = {}
        processed_providers = set()
        
        for tool in validated_tools:
            if tool in APP_TO_ACTIONS:
                await self._create_functions_from_app(
                    tool, functions, user_id, connection_id, processed_providers
                )
            else:
                await self._create_function_from_action(
                    tool, functions, user_id, connection_id
                )
        
        return functions

    def _validate_user_id(self, user_id: str) -> None:
        """Validate user ID parameter."""
        if not user_id or not user_id.strip():
            raise ValueError("User ID cannot be empty")

    def _validate_and_prepare_tools(self, tools: Optional[List[str]]) -> List[str]:
        """Validate and prepare tools list."""
        if tools is None:
            return list(ACTION_METADATA.keys())
        
        if not isinstance(tools, list):
            raise ValueError("Tools must be a list or None")
        
        if not tools:
            raise ValueError("Tools list cannot be empty")
            
        return tools

    async def _process_app_constant(
        self, 
        app_tool: str, 
        tool_schemas: List[ChatCompletionToolParam],
        processed_providers: set
    ) -> None:
        """Process an app constant and add its tool schemas."""
        try:
            provider_service_key = self._get_provider_service_from_app(app_tool)
            
            if provider_service_key not in processed_providers:
                processed_providers.add(provider_service_key)
                provider, service = provider_service_key.split(":")
                
                actions_response = await self._get_available_actions(provider, service)
                
                for action_name, action_data in actions_response.items():
                    schema = {"type": "function", "function": action_data}
                    tool_schemas.append(ChatCompletionToolParam(**schema))
                    
        except Exception as e:
            print(f"Warning: Could not process app constant '{app_tool}': {str(e)}")

    async def _process_action_constant(
        self, 
        action_tool: str, 
        tool_schemas: List[ChatCompletionToolParam]
    ) -> None:
        """Process an action constant and add its tool schema."""
        try:
            metadata = self.get_action_metadata(action_tool)

            schema = await self._get_tool_schema(
                action_name=metadata["friendly_name"],
                provider=metadata["provider"],
                service=metadata["service"]
            )

            if "function" not in schema:
                schema = {"type": "function", "function": schema}

            tool_schemas.append(ChatCompletionToolParam(**schema))

        except Exception as e:
            print(f"Warning: Could not process action constant '{action_tool}': {str(e)}")

    async def _create_functions_from_app(
        self,
        app_tool: str,
        functions: Dict[str, ToolFunction],
        user_id: str,
        connection_id: Optional[str],
        processed_providers: set
    ) -> None:
        """Create ToolFunction objects from an app constant."""
        try:
            provider_service_key = self._get_provider_service_from_app(app_tool)
            
            if provider_service_key not in processed_providers:
                processed_providers.add(provider_service_key)
                provider, service = provider_service_key.split(":")
                
                actions_response = await self._get_available_actions(provider, service)
                
                for action_name, action_schema in actions_response.items():
                    action_constant = self._find_action_constant(action_name, provider, service)
                    
                    if action_constant:
                        tool_function = ToolFunction(
                            client=self.client,
                            user_id=user_id.strip(),
                            action=action_constant,
                            connection_id=connection_id,
                            schema=action_schema
                        )
                        functions[action_constant] = tool_function
                        
        except Exception as e:
            print(f"Warning: Could not create functions from app '{app_tool}': {str(e)}")

    async def _create_function_from_action(
        self,
        action_tool: str,
        functions: Dict[str, ToolFunction],
        user_id: str,
        connection_id: Optional[str]
    ) -> None:
        """Create a ToolFunction object from an action constant."""
        try:
            metadata = self.get_action_metadata(action_tool)
            schema = await self._get_tool_schema(
                action_name=metadata["friendly_name"],
                provider=metadata["provider"],
                service=metadata["service"]
            )
            
            tool_function = ToolFunction(
                client=self.client,
                user_id=user_id.strip(),
                action=action_tool,
                connection_id=connection_id,
                schema=schema
            )
            
            functions[action_tool] = tool_function
            
        except Exception as e:
            print(f"Warning: Could not create function for action '{action_tool}': {str(e)}")

    def _find_action_constant(self, action_name: str, provider: str, service: str) -> Optional[str]:
        """Find action constant by matching metadata."""
        for action, metadata in ACTION_METADATA.items():
            if (metadata["friendly_name"] == action_name and 
                metadata["provider"] == provider and 
                metadata["service"] == service):
                return action
        return None

    def _get_provider_service_from_app(self, app_constant: str) -> str:
        """
        Get provider:service key from app constant.
        
        Args:
            app_constant: App constant (e.g., App.GMAIL)
            
        Returns:
            String in format "provider:service" (e.g., "google:gmail")
            
        Raises:
            ValueError: If app constant is invalid
        """
        from lumen_tooling.constants import APP_TO_ACTIONS
        
        actions = APP_TO_ACTIONS.get(app_constant, [])
        if not actions:
            raise ValueError(f"No actions found for app constant: {app_constant}")
        
        first_action = actions[0]
        metadata = ACTION_METADATA.get(first_action)
        if not metadata:
            raise ValueError(f"No metadata found for action: {first_action}")
        
        return f"{metadata['provider']}:{metadata['service']}"

    async def _get_tool_schema(self, action_name: str, provider: str, service: str) -> Dict[str, Any]:
        """
        Get schema for a specific action.
        
        Args:
            action_name: Friendly name of the action (e.g., "send_email")
            provider: Provider name (e.g., "google")
            service: Service name (e.g., "gmail")
            
        Returns:
            Dictionary containing the action schema
            
        Raises:
            LumenError: If schema retrieval fails
        """
        params = {"provider": provider, "service": service}
        
        return await self.client._make_request(
            method="GET",
            endpoint=f"/actions/{action_name}/schema",
            params=params
        )

    async def _get_available_actions(self, provider: str, service: str) -> Dict[str, Dict[str, Any]]:
        """
        Get all available actions for a provider/service combination.
        
        Args:
            provider: Provider name (e.g., "google")
            service: Service name (e.g., "gmail")
            
        Returns:
            Dictionary containing all available actions for the provider/service
            
        Raises:
            LumenError: If actions retrieval fails
        """
        params = {"provider": provider, "service": service}
        
        actions_list = await self.client._make_request(
            method="GET",
            endpoint="/actions/",
            params=params
        )
        
        if isinstance(actions_list, list):
            actions_dict = {}
            for action_item in actions_list:
                if isinstance(action_item, dict):
                    func = action_item.get("function")
                    if isinstance(func, dict) and "name" in func:
                        actions_dict[func["name"]] = func
            return actions_dict
        
        return actions_list if isinstance(actions_list, dict) else {}