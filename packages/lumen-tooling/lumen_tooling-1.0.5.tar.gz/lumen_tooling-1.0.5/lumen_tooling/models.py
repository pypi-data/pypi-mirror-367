"""
File: /models.py
Created Date: Friday July 27th 2025
Author: Harsh Kumar <fyo9329@gmail.com>
-----
Last Modified: Friday July 27th 2025
Modified By: the developer formerly known as Harsh Kumar at <fyo9329@gmail.com>
-----
"""

from typing import Optional, Dict, List
from pydantic import BaseModel
from datetime import datetime

class User(BaseModel):
    id: Optional[str] = None
    user_id: str
    created_at: Optional[datetime] = None

class ServiceTokens(BaseModel):
    access_token_encrypted: Optional[str] = None
    refresh_token_encrypted: Optional[str] = None
    token_expires_at: Optional[datetime] = None
    scopes: List[str] = []
    is_authenticated: bool = False
    last_used: Optional[datetime] = None

class ProviderConnection(BaseModel):
    client_id: str
    client_secret_encrypted: str
    callback_url: Optional[str] = None
    services: Dict[str, ServiceTokens] = {}

class Connection(BaseModel):
    id: Optional[str] = None
    user_id: str
    providers: Dict[str, ProviderConnection] = {}
    api_key: Optional[str] = None
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class ProviderCredentials(BaseModel):
    client_id: str
    client_secret: str
    services: Optional[List[str]] = []
    callback_url: Optional[str] = None

class ConnectionCreate(BaseModel):
    providers: Dict[str, ProviderCredentials]
    user_id: str

class ConnectionResponse(BaseModel):
    connection_id: str
    api_key: str
    providers_services_configured: List[str]
    callback_urls: Dict[str, str]
    status: str
    message: str
    redirect_url: Optional[str] = None
    state: Optional[str] = None 