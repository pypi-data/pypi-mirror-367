from machc.core.entities.base.identifier import EntityId


class AddressId(EntityId):
    """
    The AddressId class extends EntityId to uniquely identify address entities
    within the platform. It serves as the foundational identifier for the Address class,
    ensuring consistency and reliability in managing address-related records across the
    Machc project.

    This class inherits the flexibility of EntityId, enabling identification through either
    a UUID or a string-based key, and aligns with Clean Architecture principles to ensure
    modularity and separation of concerns.
    """

    def __init__(self, id=None, key=None):
        """
        Constructs an AddressId instance using either a UUID or a string-based key.

        Args:
            id (uuid.UUID, optional): The UUID to assign as the unique identifier.
            key (str, optional): The string-based key for custom identification.
        """
        super().__init__(id=id, key=key)