from __future__ import annotations

from typing import Any
from uuid import UUID

import attrs
from advanced_alchemy.filters import FilterTypes
from sqlalchemy import select

from leaguemanager.models import Organization
from leaguemanager.repository import OrganizationSyncRepository
from leaguemanager.repository._async import OrganizationAsyncRepository
from leaguemanager.services._typing import ModelT
from leaguemanager.services.base import (
    SQLAlchemyAsyncRepositoryService,
    SQLAlchemySyncRepositoryService,
    is_dict_with_field,
    is_dict_without_field,
)

__all__ = ["OrganizationService", "OrganizationAsyncService"]


class OrganizationService(SQLAlchemySyncRepositoryService):
    """Handles database operations for roles data."""

    repository_type = OrganizationSyncRepository

    def to_model_on_create(
        self,
        data: ModelT | dict[str, Any],
    ) -> ModelT:
        if attrs.has(data):
            data = attrs.asdict(data)
        if is_dict_without_field(data, "slug"):
            data["slug"] = self.repository.get_available_slug(data["name"])
        return data

    def to_model_on_update(self, data):
        if attrs.has(data):
            data = attrs.asdict(data)
        if is_dict_without_field(data, "slug") and is_dict_with_field(data, "name"):
            data["slug"] = self.repository.get_available_slug(data["name"])
        return data


class OrganizationAsyncService(SQLAlchemyAsyncRepositoryService):
    """Handles database operations for roles data."""

    repository_type = OrganizationAsyncRepository

    async def to_model_on_create(
        self,
        data: ModelT | dict[str, Any],
    ) -> ModelT:
        if attrs.has(data):
            data = attrs.asdict(data)
        if is_dict_without_field(data, "slug"):
            data["slug"] = await self.repository.get_available_slug(data["name"])
        return data

    async def to_model_on_update(self, data):
        if attrs.has(data):
            data = attrs.asdict(data)
        if is_dict_without_field(data, "slug") and is_dict_with_field(data, "name"):
            data["slug"] = await self.repository.get_available_slug(data["name"])
        return data
