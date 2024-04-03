from typing import Any
from datetime import datetime
from pydantic import BaseModel, Field


class BaseH2ogptModel(BaseModel):
    """
    Base model for the H2OGPT API.

    Attributes:
        metadata (dict): A dictionary containing metadata for the model.
        chat_history (list): A list containing the chat history.
    """

    metadata: dict = {}


class ChatModel(BaseH2ogptModel):
    """
    Chat model for the H2OGPT API.

    This class represents a chat model for the H2OGPT API. It provides methods to convert chat history
    between different formats and perform operations on the chat model.

    Attributes:
        res (dict): The resource dictionary containing the SHA256 hash and content.
        metadata (dict): The metadata associated with the chat model.
        chat_history (list): The chat history stored as a list of dictionaries.

    """

    # res: list[dict[str, Any]] = Field(
    #     default_factory=lambda: [{"content": None, "sha256": None}]
    # )
    res: list[dict[str, Any]] = Field(default_factory=list)
    chat_history: list = Field(default_factory=lambda: [(None, None)])

    def __pydantic_post_init__(self):
        super().__init__()
        if self.metadata == {}:  # new chat object
            self.metadata = {
                "dateCreated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "lastUpdated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "chatId": None,
            }

    def h2ogpt_chat_conversation(self):
        """
        Convert the chat history to H2OGPT chat conversation type.

        This method converts the chat history stored in `self.chat_history` to a list of tuples,
        where each tuple represents a conversation in the H2OGPT chat conversation format.

        Returns:
            list[tuple[str, str]]: The H2OGPT chat conversation.

        Example:
            >>> model = Model()
            >>> model.chat_history = [
            ...     {"instruction": "Hello!", "response": "Hi there!"},
            ...     {"instruction": "How are you?", "response": "I'm good, thanks!"},
            ... ]
            >>> model.h2ogpt_chat_conversation()
            [('Hello!', 'Hi there!'), ('How are you?', "I'm good, thanks!")]

        """
        history = []
        for c in self.chat_history:
            history.append((c["instruction"], c["response"]))

        return history

    def db_chat_conversation(
        self,
        chat_conversation: list[tuple[str, str]],
        refresh: bool = False,
    ):
        """
        Convert H2OGPT chat conversation to chat history compatible with MongoDB.

        Args:
            chat_conversation (list[tuple[str, str]]): The H2OGPT chat conversation to be converted.
            refresh (bool, optional): If set to True, the chat history will be refreshed. Defaults to False.

        Returns:
            list[dict]: The converted chat history as a list of dictionaries, where each dictionary contains an instruction and a response.

        """
        history = []
        for c in chat_conversation:
            history.append({"instruction": c[0], "response": c[1]})

        if refresh:
            self.chat_history = history

        return history

    def tosha256(self, content: str):
        """
        Convert content to SHA256 hash.

        Args:
            content (str): The content to convert.

        Returns:
            str: The SHA256 hash of the content.

        """
        import hashlib

        result = hashlib.sha256(content.encode()).hexdigest()
        return result

    def isduplicate(self, sha256: str):
        """
        Check if SHA256 hash is in res.

        Args:
            sha256 (str): The SHA256 hash to check.

        Returns:
            bool: True if the SHA256 hash is in res, False otherwise.

        """
        return sha256 in [r["sha256"] for r in self.res]


class AllChatsModel(BaseH2ogptModel):
    """
    Chat history model for H2OGPT API
    """
