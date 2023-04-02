import moto
from src.database.chat_state import ChatStateTable


def test_database():
    print(1)
    state_manager = ChatStateTable()
    assert 1
    print(state_manager)

