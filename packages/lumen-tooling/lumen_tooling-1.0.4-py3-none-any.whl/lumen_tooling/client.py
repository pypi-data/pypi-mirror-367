"""
File: /client.py
Created Date: Tuesday July 29th 2025
Author: Harsh Kumar <fyo9329@gmail.com>
-----
Last Modified: Tuesday July 29th 2025
Modified By: the developer formerly known as Harsh Kumar at <fyo9329@gmail.com>
-----
"""

from typing import Optional, Dict, Any

from .http import BaseHTTPClient
from .managers import ToolsManager, ProviderManager, TriggersManager
from .models import ConnectionCreate, ConnectionResponse, ProviderCredentials


class LumenClient(BaseHTTPClient):
    """
    Main client for interacting with Lumen Core API.
    
    This client handles HTTP requests, authentication, and error handling
    for all Lumen Core API interactions with a focus on reliability and maintainability.
    
    Example:
        async with LumenClient(api_key="your_key") as client:
            user = await client.get_entity("user123")
            connection = await client.connect_provider("user123", "google", credentials)
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Lumen Core client.
        
        Args:
            api_key: API key for authentication.
        """
        super().__init__(api_key=api_key)
        
        self.tools = ToolsManager(self)
        self.provider = ProviderManager(self)  
        self.triggers = TriggersManager(self)
    
    async def connect_provider(
        self,
        user_id: str,
        provider_name: str,
        credentials: ProviderCredentials,
        scopes: Optional[list[str]] = None
    ) -> ConnectionResponse:
        """
        Connect a single provider for a user with specified scopes and get OAuth URL.
        
        This method automatically creates the connection and generates the OAuth 
        authorization URL for immediate use.
        
        Args:
            user_id: The unique identifier for the user
            provider_name: Name of the provider (e.g., 'google')
            credentials: Provider credentials object
            scopes: Optional list of service scopes
            
        Returns:
            ConnectionResponse with connection details and OAuth URL
            
        Raises:
            ValueError: If required parameters are invalid
            LumenError: For API errors
        """
        self._validate_user_id(user_id)
        self._validate_provider_name(provider_name)
        self._validate_credentials(credentials)
        
        user_id = user_id.strip()
        provider_name = provider_name.strip().lower()
        
        await self.__get_entity(user_id)
        
        credentials_dict = self._prepare_credentials_dict(credentials, scopes)
        updated_credentials = ProviderCredentials(**credentials_dict)
        
        providers = {provider_name: updated_credentials}
        connection_response = await self.__create_connection(user_id, providers)
        
        if scopes:
            await self._add_oauth_url_to_response(
                connection_response, provider_name, scopes[0], user_id
            )
        
        return connection_response
    
    async def handle_oauth_callback(self, code: str, state: str) -> Dict[str, Any]:
        """
        Handle OAuth callback with authorization code and state.
        
        Args:
            code: Authorization code from OAuth provider
            state: State parameter to verify the request
            
        Returns:
            Dictionary containing callback result with provider, service, status, and tokens
            
        Raises:
            ValueError: If code or state is empty
            ValidationError: If state is invalid or callback fails
            LumenError: For other API errors
            
        Example:
            result = await client.handle_oauth_callback(
                code="authorization_code_from_callback",
                state="state_from_callback"
            )
            print(f"Authentication status: {result['status']}")
        """
        self._validate_oauth_params(code, state)
        
        return await self._make_request(
            method="GET",
            endpoint="/oauth/callback",
            params={
                "code": code.strip(),
                "state": state.strip()
            }
        )

    def _validate_user_id(self, user_id: str) -> None:
        """Validate user ID parameter."""
        if not user_id or not user_id.strip():
            raise ValueError("User ID cannot be empty")

    def _validate_provider_name(self, provider_name: str) -> None:
        """Validate provider name parameter."""
        if not provider_name or not provider_name.strip():
            raise ValueError("Provider name cannot be empty")

    def _validate_credentials(self, credentials: ProviderCredentials) -> None:
        """Validate credentials parameter."""
        if not credentials:
            raise ValueError("Credentials cannot be empty")

    def _validate_providers(self, providers: Dict[str, ProviderCredentials]) -> None:
        """Validate providers dictionary."""
        if not providers:
            raise ValueError("Providers dictionary cannot be empty")

    def _validate_connection_id(self, connection_id: str) -> None:
        """Validate connection ID parameter."""
        if not connection_id or not connection_id.strip():
            raise ValueError("Connection ID cannot be empty")

    def _validate_oauth_params(self, code: str, state: str) -> None:
        """Validate OAuth callback parameters."""
        if not code or not code.strip():
            raise ValueError("Authorization code cannot be empty")
        if not state or not state.strip():
            raise ValueError("State parameter cannot be empty")

    def _prepare_credentials_dict(
        self, 
        credentials: ProviderCredentials, 
        scopes: Optional[list[str]]
    ) -> Dict[str, Any]:
        """Prepare credentials dictionary with scopes."""
        if isinstance(credentials, ProviderCredentials):
            credentials_dict = credentials.model_dump()
        else:
            credentials_dict = credentials.copy() if hasattr(credentials, 'copy') else dict(credentials)
        
        if scopes:
            credentials_dict['services'] = scopes
        elif 'services' not in credentials_dict or not credentials_dict['services']:
            credentials_dict['services'] = []
        
        return credentials_dict

    def _serialize_providers(self, providers: Dict[str, ProviderCredentials]) -> Dict[str, Any]:
        """Serialize providers dictionary for API request."""
        return {
            provider_name: (
                creds.model_dump() if isinstance(creds, ProviderCredentials) else creds
            )
            for provider_name, creds in providers.items()
        }

    async def _add_oauth_url_to_response(
        self,
        connection_response: ConnectionResponse,
        provider_name: str,
        service: str,
        user_id: str
    ) -> None:
        """Add OAuth URL to connection response if possible."""
        try:
            auth_response = await self._get_oauth_authorization_url(
                connection_id=connection_response.connection_id,
                provider=provider_name,
                service=service,
                user_id=user_id
            )
            
            connection_response.redirect_url = auth_response.get("auth_url")
            connection_response.state = auth_response.get("state")
        except Exception as e:
            print(f"Warning: Could not generate OAuth URL: {str(e)}")

    async def _get_oauth_authorization_url(
        self,
        connection_id: str,
        provider: str,
        service: str,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Internal method to get OAuth authorization URL from the API.
        
        Args:
            connection_id: The connection ID
            provider: Provider name
            service: Service name  
            user_id: User ID
            
        Returns:
            Dictionary with redirect_url and state
        """
        return await self._make_request(
            method="GET",
            endpoint=f"/oauth/{connection_id}/{provider}/{service}/authorize",
            params={"user_id": user_id}
        )
    
    async def __get_entity(self, user_id: str) -> Dict[str, Any]:
        """
        Create or retrieve a user by ID.
        
        This method automatically handles user creation if the user doesn't exist,
        so developers don't need to worry about whether a user exists or not.
        
        Args:
            user_id: The unique identifier for the user
            
        Returns:
            Dictionary containing user data from the API response
            
        Raises:
            ValueError: If user_id is empty or invalid
            AuthenticationError: If API key is invalid
            ValidationError: If user_id format is invalid
            LumenError: For other API errors
        """
        self._validate_user_id(user_id)
        
        return await self._make_request(
            method="POST",
            endpoint="/users/",
            params={"uniqueUserId": user_id.strip()}
        )
    
    async def __create_connection(
        self,
        user_id: str,
        providers: Dict[str, ProviderCredentials]
    ) -> ConnectionResponse:
        """
        Create a unified connection supporting multiple providers and services.
        
        This is the legacy method that supports multiple providers at once.
        For simpler use cases, consider using connect_provider() instead.
        
        Args:
            user_id: The unique identifier for the user
            providers: Dictionary of provider configurations
                     Key: provider name (e.g., 'google')
                     Value: ProviderCredentials object with client_id, client_secret, services, callback_url
        
        Returns:
            ConnectionResponse object containing connection details
            
        Raises:
            ValueError: If user_id is empty or providers is empty
            ValidationError: If provider/service combination is invalid
            LumenError: For other API errors
        """
        self._validate_user_id(user_id)
        self._validate_providers(providers)
        
        providers_dict = self._serialize_providers(providers)
        
        connection_data = ConnectionCreate(
            user_id=user_id.strip(),
            providers=providers_dict
        )
        
        response_data = await self._make_request(
            method="POST",
            endpoint="/connections/",
            json_data=connection_data.model_dump()
        )
        
        return ConnectionResponse(**response_data)