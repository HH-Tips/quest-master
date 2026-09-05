from langchain_core.language_models import BaseChatModel
from dotenv import load_dotenv
from textual.app import App
from textual.binding import Binding
from tui.welcome_screen import WelcomeScreen
from utils.advanced_chat_model import AdvancedChatModel
import os
import json

class QuestMasterApp(App):
    """Applicazione principale."""
    model: BaseChatModel

    BINDINGS = [
        Binding("q", "quit", "Esci", show=True),
    ]

    def on_mount(self) -> None:
        if not os.getenv("GOOGLE_API_KEY"):
            raise Exception("API KEY mancante, inserire l'API key nel file .env")
        self.app.model = AdvancedChatModel(
            model=os.getenv("DEFAULT_MODEL"),
            base_url=os.getenv("OPENAI_API_URL"),
            api_key=os.getenv("GOOGLE_API_KEY"),
            fallback_models=json.loads(os.getenv("FALLBACK_MODELS")),
            max_retries=0
        )
        self.push_screen(WelcomeScreen())


def main():
    load_dotenv()

    app = QuestMasterApp()
    app.run()

if __name__ == "__main__":
    main()