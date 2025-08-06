from typing import Callable, Dict
from uuid import UUID
from maleo_metadata.enums.system_role import IdentifierType
from maleo_metadata.types.base.system_role import IdentifierValueType


IDENTIFIER_TYPE_VALUE_TYPE_MAP: Dict[
    IdentifierType,
    Callable[[str], IdentifierValueType],
] = {
    IdentifierType.ID: int,
    IdentifierType.UUID: UUID,
    IdentifierType.KEY: str,
    IdentifierType.NAME: str,
}
