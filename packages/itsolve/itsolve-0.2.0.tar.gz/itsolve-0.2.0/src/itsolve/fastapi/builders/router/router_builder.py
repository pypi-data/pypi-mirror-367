from __future__ import annotations

from typing import TYPE_CHECKING, Any

from casbin import Enforcer
from fastapi import APIRouter, Depends, Request
from fastapi.routing import APIRoute
from fastapi.security import HTTPBearer

from authx import AuthX
from core.casbin import apply_permissions
from settings import get_settings

from .auth_route import AuthRouteMeta
from .default_user_payload_schema import DefaultTUserPayload

if TYPE_CHECKING:
    from src import RootContainer


class APIRouterBuilder(APIRouter):
    def __init__(
        self, container: RootContainer, *args: Any, **kwargs: Any
    ) -> None:
        super().__init__(*args, **kwargs)
        self.settings = get_settings()
        self.container = container
        self.is_auth_router: bool = False

    def apply_version(self, version: str) -> APIRouterBuilder:
        if not version.startswith("v"):
            raise ValueError("Version must start with 'v'")
        self.version = version
        return self

    def apply_auth(
        self,
        jwt_service: AuthX | None = None,
        auth_schema: HTTPBearer | None = None,
        user_payload_schema: type[DefaultTUserPayload] | None = None,
    ) -> APIRouterBuilder:
        self.auth_schema = auth_schema or HTTPBearer()
        self.user_payload_schema = user_payload_schema or DefaultTUserPayload
        self.route_class = (
            AuthRouteMeta(
                user_payload_schema=self.user_payload_schema,
                jwt_service=jwt_service or self.container.jwt_service(),
            )
            if not self.settings.jwt.mock_user
            else APIRoute
        )

        async def mock_user(request: Request) -> None:
            request.state.user = self.user_payload_schema()

        if self.settings.jwt.mock_user:
            self.dependencies.append(Depends(mock_user))
        else:
            self.dependencies.append(Depends(self.auth_schema))
        self.is_auth_router = True
        return self

    def apply_permissions(
        self,
        enforcer: Enforcer | None = None,
        resource: str | None = None,
    ) -> APIRouterBuilder:
        if not self.is_auth_router:
            raise ValueError("Permissions can only be applied to auth routers")
        if self.settings.permissions.enabled:
            self.dependencies.append(
                Depends(
                    apply_permissions(
                        enforcer or self.container.casbin_enforcer(),
                        resource or self.prefix.replace("/", ""),
                    )
                )
            )
        return self
