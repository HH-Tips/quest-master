from textual.app import ComposeResult
from textual.containers import Vertical, Horizontal
from textual.css.query import NoMatches
from textual.reactive import reactive
from textual.widgets import Header, Footer, TextArea, Button, Static, TabbedContent, TabPane, Markdown
from textual.screen import Screen
from textual import on
import agents.pddl_generator as pddl_generator
import utils.utils as utils
from utils.pddl_analisys import PddlAnalysis, ValidationRes


class TextualEditorScreen(Screen):

    CSS_PATH = "stylesheets/editor.tcss"
    LLM_INPUT_AREA_ID = "llm-input"
    BUTTON_SHOW_PROMPT_FIELD_ID = "btn-prompt"
    PDDL_EDITOR_AREA_ID = "editor-pddl"
    LLM_INPUT_CONTAINER_ID = "llm-input-container"

    logs = reactive("")
    original_pddl = ""

    def __init__(self, llm_hint: str, pddl: tuple[str, str]):
        super().__init__()
        self.llm_hint = llm_hint
        self.pddl_content = (3*"\n").join(pddl)
        self.original_pddl = self.pddl_content


    def watch_logs(self, value: str):
        try:
            text_area = self.query_one("#text-area-logs", TextArea)
            text_area.load_text(value)
            # Sposta la scrollbar alla fine senza animazione.
            last_line = text_area.document.line_count - 1
            text_area.cursor_location = (last_line, 0)
        except NoMatches:
            pass

    def compose(self) -> ComposeResult:
        """Crea i widget per lo schermo."""
        yield Header(show_clock=True)

        with Vertical(id="main-container"):
            with TabbedContent(initial="tab-hint"):
                with TabPane("Hint LLM", id="tab-hint"):
                    yield Markdown(self.llm_hint, id="editor-hint")
                with TabPane("File PDDL", id="tab-pddl"):
                    yield TextArea(self.pddl_content, id=self.PDDL_EDITOR_AREA_ID, read_only=True)
                with TabPane("Logs", id="tab-logs"):
                    yield TextArea(self.pddl_content, id="text-area-logs", read_only=True)

            # Input LLM
            with Horizontal(id=self.LLM_INPUT_CONTAINER_ID):
                yield TextArea(placeholder="Istruzioni per l'LLM...", id=self.LLM_INPUT_AREA_ID)
                yield Button("Send", id="btn-send-llm", variant="success")
                yield Button("X", id="btn-close-llm", variant="error")

            with Horizontal(id="button-bar"):
                # Stato Iniziale (4 pulsanti)
                with Horizontal(id="normal-actions", classes="nav-container"):
                    yield Button("Modifica", variant="default", id="btn-modifica")
                    yield Button("Conferma", variant="success", id="btn-conferma")
                    yield Button("Rigenera", variant="error", id="btn-rigenera")

                # Stato Modifica (2 pulsanti)
                with Horizontal(id="edit-actions", classes="nav-container"):
                    yield Button("Valida e Conferma", variant="success", id="btn-valida")
                    yield Button("Ripristina", variant="warning", id="btn-ripristina")
                    yield Button("Show Prompt Field", variant="primary", id=self.BUTTON_SHOW_PROMPT_FIELD_ID)

            yield Static("Pronto", id="status-display")

        yield Footer()


    def update_status(self, message: str) -> None:
        """Aggiorna la barra di stato inferiore."""
        self.query_one("#status-display", Static).update(message)


    def toggle_edit_mode(self, editing: bool, is_llm: bool = False):
        """Passa dalla modalità visualizzazione alla modalità modifica."""
        self.query_one("#normal-actions").display = not editing
        self.query_one("#edit-actions").display = editing
        self.query_one(f"#{self.PDDL_EDITOR_AREA_ID}").read_only = not editing

        container_llm = self.query_one(f"#{self.LLM_INPUT_CONTAINER_ID}")
        container_llm.display = editing and is_llm

        if editing:
            if is_llm:
                self.query_one(f"#{self.LLM_INPUT_AREA_ID}").focus()
                self.update_status("Modalità LLM: inserisci il prompt o modifica il PDDL")
            else:
                self.query_one(f"#{self.PDDL_EDITOR_AREA_ID}").focus()
                self.update_status("Modalità Modifica: puoi editare il file PDDL")
        else:
            self.update_status("Pronto")


    @on(Button.Pressed, "#btn-modifica")
    def handle_modifica(self) -> None:
        self.query_one(TabbedContent).active = "tab-pddl"
        self.toggle_edit_mode(True, is_llm=False)


    @on(Button.Pressed, "#btn-conferma")
    def handle_conferma(self) -> None:
        """Salva le modifiche e torna alla modalità normale."""
        try:
            self.dismiss(utils.split_pddl_content(self.pddl_content))
        except IndexError:
            self.notify("missing problem definition.")


    @on(Button.Pressed, "#btn-ripristina")
    def handle_ripristina(self) -> None:
        """Annulla le modifiche correnti e torna alla modalità normale."""
        self.query_one(f"#{self.PDDL_EDITOR_AREA_ID}").text = self.pddl_content
        self.query_one(f"#{self.LLM_INPUT_AREA_ID}").text = ""
        self.query_one(f"#{self.BUTTON_SHOW_PROMPT_FIELD_ID}").display = True
        self.query_one(f"#{self.LLM_INPUT_CONTAINER_ID}").display = False
        self.notify("Modifiche annullate.")
        self.toggle_edit_mode(False)


    @on(Button.Pressed, f"#{BUTTON_SHOW_PROMPT_FIELD_ID}")
    def handle_prompt(self) -> None:
        self.query_one(f"#{self.BUTTON_SHOW_PROMPT_FIELD_ID}", Button).display = False
        self.toggle_edit_mode(True, is_llm=True)


    @on(Button.Pressed, "#btn-send-llm")
    async def handle_send_llm(self) -> None:
        async def handle_request() -> None:
            response = await pddl_generator.edit_using_llm(self.app.model, (utils.split_pddl_content(pddl)), user_prompt)
            pddl_response = utils.join_pddl_content(response)
            self.app.call_from_thread(update_tui, pddl_response)
        def update_tui(pddl_response: str) -> None:
            editor.text = pddl_response
            self.update_status("Modificato con successo.")
        editor = self.query_one(f"#{self.PDDL_EDITOR_AREA_ID}", TextArea)
        self.update_status("Modifica in corso: attendendo risposta dal LLM")
        user_prompt = self.query_one(f"#{self.LLM_INPUT_AREA_ID}", TextArea).text
        pddl = editor.text
        self.run_worker(handle_request(), thread=True)


    @on(Button.Pressed, "#btn-close-llm")
    def handle_close_llm(self) -> None:
        """Nasconde il campo di input LLM ma resta in modalità modifica."""
        self.query_one(f"#{self.LLM_INPUT_AREA_ID}").text = ""
        self.query_one(f"#{self.BUTTON_SHOW_PROMPT_FIELD_ID}", Button).display = True
        self.query_one(f"#{self.LLM_INPUT_CONTAINER_ID}").display = False


    @on(Button.Pressed, "#btn-valida")
    async def handle_valida_conferma_modifica(self) -> None:
        async def validate(pddl_content: str) -> PddlAnalysis:
            try:
                return await pddl_generator.validate_pddl(utils.split_pddl_content(pddl_content))
            except IndexError:
                return PddlAnalysis(ValidationRes.SYNTAX_ERROR, log="missing problem definition.")
        self.update_status("Validazione in corso...")
        pddl = self.query_one(f"#{self.PDDL_EDITOR_AREA_ID}", TextArea).text
        result = await validate(pddl)
        if result.exit_code == ValidationRes.VALID:
            self.notify("PDDL VALIDO")
            self.pddl_content = pddl
            self.update_status("Validazione superata.")
            self.query_one("#btn-conferma", Button).styles.display = "block"
            self.toggle_edit_mode(False)
        else:
            self.notify("PDDL NON VALIDO", severity="error")
            self.update_status("Validazione fallita.")
            self.logs += result.log + 3*"\n"


    @on(Button.Pressed, "#btn-rigenera")
    def handle_rigenera(self) -> None:
        """Ripristina i contenuti al valore salvato (cache)."""
        self.query_one(f"#{self.PDDL_EDITOR_AREA_ID}").text = self.pddl_content
        self.dismiss()
        self.notify("Contenuto ripristinato", severity="warning")