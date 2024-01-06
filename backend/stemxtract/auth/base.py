from abc import ABCMeta, abstractmethod


# NOTE: This may just end up being an oauth client we subclass for providers
class AuthManager(metaclass=ABCMeta):
    # NOTE: Will need to extend this to add refresh token etc
    @abstractmethod
    async def create(self, token: str, user_id: str) -> None:
        ...

    @abstractmethod
    async def validate(self, token: str, force_refresh: bool = False) -> bool:
        ...
