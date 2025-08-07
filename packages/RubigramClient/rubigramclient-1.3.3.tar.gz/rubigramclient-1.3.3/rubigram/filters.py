from rubigram.types import Update, InlineMessage
from typing import Union


class filter:
    @staticmethod
    def command(command: Union[str, list[str]], prefixes: Union[str, list[str]] = "/"):
        def inner(update: Update):
            if isinstance(update, Update) and update.new_message and update.new_message.text:
                message = update.new_message
                commands = command if isinstance(command, list) else [command]
                commands = [c.lower() for c in commands]
                prefix_list = [] if prefixes is None else prefixes
                prefix_list = prefix_list if isinstance(prefix_list, list) else [prefix_list]
                for prefix in prefix_list:
                    if message.text.startswith(prefix) and commands:
                        return message.text[len(prefix):].split()[0].lower() in commands
                    return False
            return False
        return inner
    
    @staticmethod
    def text():
        def inner(update: Update):
            if isinstance(update, Update) and update.new_message:
                return update.new_message.text is not None
            return False
        return inner

    @staticmethod
    def private():
        def inner(update: Update):
            if isinstance(update, Update) and update.new_message:
                return update.new_message.sender_type == "User"
            return False
        return inner
    
    @staticmethod
    def chat(chat_id: str):
        def inner(update: Update):
            return getattr(update, "chat_id", None) == chat_id
        return inner
    
    @staticmethod
    def file():
        def inner(update: Update):
            if isinstance(update, Update) and update.new_message:
                return update.new_message.file is not None
            return False
        return inner
    
    @staticmethod
    def button(id: str):
        def inner(update: InlineMessage):
            if isinstance(update, InlineMessage):
                return update.aux_data.button_id == id
            return False
        return inner