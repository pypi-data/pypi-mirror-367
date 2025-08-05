"""
Base backend database options.
"""
import logging
from collections.abc import Generator
from typing import Any

logger = logging.getLogger(__name__)


ItemMeta = dict[str, Any]
ItemMetaGen = Generator[ItemMeta, None, None]


class _Backend:
    """
    Base class for backend database.

    Backends are internal to happi and are subject to change.  Users should
    interact with the :class:`happi.Client`.
    """

    @property
    def all_items(self) -> list[ItemMeta]:
        """
        List of all items in the database.

        This base class ``_Backend`` provides no implementation and requires
        that a subclass provide its customized implementation.
        """
        raise NotImplementedError

    def clear_cache(self) -> None:
        """
        Request to clear any cached data.

        Optional implementation may be customized in subclass.
        """

    def find(self, multiples: bool = False, **kwargs) -> ItemMetaGen:
        """
        Find an instance or instances that matches the search criteria.

        This base class ``_Backend`` provides no implementation and requires
        that a subclass provide its customized implementation.

        Parameters
        ----------
        multiples : bool
            Find a single result or all results matching the provided
            information.
        kwargs
            Requested information.
        """
        raise NotImplementedError

    def save(
        self,
        _id: str,
        post: dict[str, Any],
        insert: bool = True
    ) -> None:
        """
        Save information to the database.

        This base class ``_Backend`` provides no implementation and requires
        that a subclass provide its customized implementation.

        Parameters
        ----------
        _id : str
            ID of device.
        post : dict
            Information to place in database.
        insert : bool, optional
            Whether or not this a new device to the database.

        Raises
        ------
        DuplicateError
            If ``insert`` is `True`, but there is already a device with the
            provided ``_id``.
        SearchError
            If ``insert`` is `False`, but there is no device with the provided
            ``_id``.
        PermissionError
            If the write operation fails due to issues with permissions.
        """
        raise NotImplementedError

    def delete(self, _id: str) -> None:
        """
        Delete a device instance from the database.

        This base class ``_Backend`` provides no implementation and requires
        that a subclass provide its customized implementation.

        Parameters
        ----------
        _id : str
            ID of device.

        Raises
        ------
        PermissionError
            If the write operation fails due to issues with permissions.
        """
        raise NotImplementedError
