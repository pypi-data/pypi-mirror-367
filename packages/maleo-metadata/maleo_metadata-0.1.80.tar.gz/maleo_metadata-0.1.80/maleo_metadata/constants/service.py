from typing import Callable, Dict
from uuid import UUID
from maleo_soma.schemas.resource import Resource, ResourceIdentifier
from maleo_metadata.enums.service import IdentifierType
from maleo_metadata.types.base.service import IdentifierValueType


IDENTIFIER_TYPE_VALUE_TYPE_MAP: Dict[
    IdentifierType, Callable[[str], IdentifierValueType]
] = {
    IdentifierType.ID: int,
    IdentifierType.UUID: UUID,
    IdentifierType.KEY: str,
    IdentifierType.NAME: str,
}


RESOURCE = Resource(
    identifier=ResourceIdentifier(key="services", name="Services", url_slug="services"),
    details=None,
)
