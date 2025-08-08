import uuid
from abc import ABC, abstractmethod

class IdentifiedObject(ABC):
    """
    The IdentifiedObject interface defines methods for objects that require unique identification
    within the platform. Classes implementing this interface must provide methods for retrieving 
    and assigning identifiers.
    """

    @abstractmethod
    def get_id(self):
        pass

    @abstractmethod
    def get_key(self):
        pass


class EntityId(IdentifiedObject):
    """
    The EntityId class provides unique identification for entities in the platform, adhering to Clean Architecture principles.
    
    It supports identification using either a UUID or a string-based key, ensuring flexibility for diverse use cases. 
    This implementation is designed to be serializable and forms the foundational component for entity identification 
    within the Machanism Core Entities Module.
    
    Key Features:
    - Supports UUID or string-based key for identification.
    - Implements IdentifiedObject interface to standardize entity identification.
    - Designed for easy serialization and persistence.
    """
    
    def __init__(self, id=None, key=None):
        """
        Constructs an EntityId using either a UUID or a custom string-based key.

        Args:
            id (uuid.UUID, optional): The UUID to assign as the unique identifier.
            key (str, optional): The string-based key for custom identification.
        """
        self._id = id
        self._key = key

    def get_id(self):
        """
        Retrieves the UUID for this EntityId.

        Returns:
            uuid.UUID: The UUID assigned as the unique identifier, or None if not set.
        """
        return self._id

    def set_id(self, id):
        """
        Sets the UUID for this EntityId.

        Args:
            id (uuid.UUID): The UUID to assign as the unique identifier.
        """
        self._id = id

    def get_key(self):
        """
        Retrieves the custom string-based key for this EntityId.

        Returns:
            str: The string key assigned as the identifier, or None if not set.
        """
        return self._key

    def set_key(self, key):
        """
        Sets the custom string-based key for this EntityId.

        Args:
            key (str): The string key to assign as the identifier.
        """
        self._key = key


# Example usage:
if __name__ == "__main__":
    # Creating EntityId instances
    entity_with_uuid = EntityId(id=uuid.uuid4())
    entity_with_key = EntityId(key="custom-key")

    # Accessing properties
    print(f"Entity with UUID: {entity_with_uuid.get_id()}")
    print(f"Entity with Key: {entity_with_key.get_key()}")

    # Modifying properties
    entity_with_uuid.set_id(uuid.uuid4())
    entity_with_key.set_key("new-custom-key")

    print(f"Updated Entity with UUID: {entity_with_uuid.get_id()}")
    print(f"Updated Entity with Key: {entity_with_key.get_key()}")