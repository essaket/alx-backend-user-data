#!/usr/bin/env python3
"""3. Auth class
   4. Define which routes don't need authentication
   5. Request validation!
"""
import fnmatch
from typing import List, TypeVar

User = TypeVar('User')


class Auth:
    """Auth class to manage the API authentication
    """

    def require_auth(self, path: str, excluded_paths: List[str]) -> bool:
        """Method to require the authentication
        """
        if path is None or excluded_paths is None or excluded_paths == []:
            return True
        if path[-1] != '/':
            path += '/'
        if path in excluded_paths:
            return False
        for excluded_path in excluded_paths:
            if fnmatch.fnmatch(path, excluded_path):
                return False
        return True

    def authorization_header(self, request=None) -> str:
        """Method to get the authorization header
        """
        if request is None:
            return None
        return request.headers.get("Authorization", None)

    def current_user(self, request=None) -> User:
        """Method to get the current user
        """
        return None
