"""
Unified client for MafiaOnline services.

This module provides a unified interface for interacting with the
MafiaOnline API. It includes methods for authentication, room
management, global chat, matchmaking, and more.

Typical usage example:

    client = Client()
    client.auth.login(...)
"""


class Client:
    """
    Unified client for interacting with MafiaOnline services.

    Provides a single entry point exposing submodules for authentication,
    user management, players, global chat, rooms, matchmaking, HTTPS proxying,
    and low‑level Mafia API calls. Delegates method access to the appropriate
    submodule when attributes are looked up.

    Attributes:
        auth (Auth): Authentication submodule for login and token management.
        sub_modules (dict[str, Any]): Mapping of submodule names to instances,
            used to delegate attribute access dynamically.
    """

    # TODO: @unelected - improve inheritance hierarchy to avoid dynamic delegation
    def __init__(self, proxy: str | None = None):
        """
        Initializes all service submodules with shared client context.

        Dynamically imports and instantiates each API submodule, injecting
        this client (or the auth submodule) and optional proxy settings.

        Args:
            proxy (str | None): Optional proxy URL applied to HTTP sessions.
                If None, no proxy will be used.
        """
        from zafiaonline.api_client.player_methods import Players
        from zafiaonline.api_client.global_chat_methods import GlobalChat
        from zafiaonline.api_client.user_methods import Auth, User
        from zafiaonline.api_client.room_methods import Room, MatchMaking
        from zafiaonline.api_client.https_api import HttpsApi
        from zafiaonline.api_client.zafia_api import ZafiaApi

        self.auth = Auth(client = self, proxy = proxy)

        self.sub_modules: dict[str, Auth | Players | GlobalChat | User | Room | MatchMaking | HttpsApi | ZafiaApi] = {
            "auth": self.auth,
            "user": User(client = self.auth),
            "players": Players(client = self.auth),
            "global_chat": GlobalChat(client = self.auth),
            "room": Room(client = self.auth),
            "matchmaking": MatchMaking(client = self.auth),
            "https": HttpsApi(proxy = proxy),
            "zafia": ZafiaApi(proxy = proxy),
        }

    def __getattr__(self, name: str):
        """Delegates attribute access to the appropriate submodule.

        If an attribute is not found on this Client instance, each submodule
        is checked in order, and the attribute is returned from the first one
        that defines it.

        Args:
            name (str): The attribute name being accessed.

        Returns:
            Any: The attribute value from the submodule.

        Raises:
            AttributeError: If no submodule defines the requested attribute.
        """
        for sub_name, sub in self.sub_modules.items():
            if hasattr(sub, name):
                return getattr(sub, name)
        raise AttributeError(f"'{self.__class__.__name__}' "
                             f"object has no attribute '{name}'")
