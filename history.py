from langchain_core.chat_history import BaseChatMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory


class HistoryStore:
    def __init__(self):
        self.store = {}

    def get_history(self, user_id, target_id) -> BaseChatMessageHistory:
        if (user_id, target_id) not in self.store:
            print("create new history : ", user_id, target_id)
            self.store[(user_id, target_id)] = ChatMessageHistory()
        return self.store[(user_id, target_id)]
    
