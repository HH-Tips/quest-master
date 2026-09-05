from textual.app import ComposeResult
from textual.containers import Center, Vertical, Horizontal
from textual.widgets import Input, Button, Header, Footer, Static, Label, TextArea
from textual.screen import Screen
from tui.processing_screen import ProcessingScreen
from utils.lore_document import LoreDocument

ASCII_TITLE = """                                                                          
   ▄▄▄▄                            ▄▄▄     ▄▄▄                            
 ▄█▀▀███▄▄                  █▄      ███▄ ▄███               █▄            
 ██    ██                  ▄██▄     ██ ▀█▀ ██              ▄██▄      ▄    
 ██    ██ ██ ██ ▄█▀█▄ ▄██▀█ ██      ██     ██   ▄▀▀█▄ ▄██▀█ ██ ▄█▀█▄ ████▄
 ██  ▄ ██ ██ ██ ██▄█▀ ▀███▄ ██      ██     ██   ▄█▀██ ▀███▄ ██ ██▄█▀ ██   
  ▀█████▄▄▀██▀█▄▀█▄▄▄█▄▄██▀▄██    ▀██▀     ▀██▄▄▀█▄███▄▄██▀▄██▄▀█▄▄▄▄█▀   
       ▀█                                                                 
                                                                          """

SUBTITLE = "L'AVVENTURA HA INIZIO NEL TERMINALE"


class WelcomeScreen(Screen):
    """Schermata iniziale di benvenuto."""
    
    CSS_PATH = "stylesheets/welcome_screen.tcss"

    lore: str = ""
    branching_factors: dict[str, int | str] = {
        "min": 2,
        "max": 4
    }
    depth_constraints: dict[str, int | str] = {
        "min": 4,
        "max": 7
    }

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Vertical(id="welcome-container"):
            with Center():
                # width: 100% nel CSS permetterà la centratura reale del testo
                yield Static(ASCII_TITLE, id="hero-title")
                yield Static(SUBTITLE, id="hero-subtitle")
            
            with Center():
                yield TextArea(placeholder="Inserisci i dettagli della lore...", id="lore-input", classes="large-input")
            
            with Center():
                with Horizontal(id="params-grid"):
                    with Vertical(classes="param-column"):
                        yield Label("Branching Factor", classes="param-label")
                        yield Input(placeholder=f"Min (default: {self.branching_factors["min"]})", id="branch-min", classes="small-input")
                        yield Input(placeholder=f"Max (default: {self.branching_factors["max"]})", id="branch-max", classes="small-input")

                    with Vertical(classes="param-column"):
                        yield Label("Depth Constraint", classes="param-label")
                        yield Input(placeholder=f"Min (default: {self.depth_constraints["min"]})", id="depth-min", classes="small-input")
                        yield Input(placeholder=f"Max (default: {self.depth_constraints["max"]})", id="depth-max", classes="small-input")
            
            with Center():
                yield Button("INIZIA AVVENTURA", variant="primary", id="start-btn")
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Gestiamo l'evento qui, dove l'input è visibile allo Screen."""
        if event.button.id == "start-btn":
            self.handle_start()


    def on_text_area_changed(self, event: TextArea.Changed) -> None:
        if event.text_area.id == "lore-input":
            self.lore = event.text_area.text


    def on_input_changed(self, event: Input.Changed) -> None:
        value: int | str = event.input.value if not event.input.value.isnumeric() else int(event.input.value)
        if event.input.id == "branch-min":
            self.branching_factors["min"] = value
        elif event.input.id == "branch-max":
            self.branching_factors["max"] = value
        elif event.input.id == "depth-min":
            self.depth_constraints["min"] = value
        elif event.input.id == "depth-max":
            self.depth_constraints["max"] = value


    def handle_start(self) -> None:
        """Logica di validazione e cambio schermo."""
        try:
            if self.validate_input():
                lore_document = LoreDocument(
                    lore = self.lore,
                    branching_factor = (self.branching_factors["min"], self.branching_factors["max"]),
                    depth_constraint = (self.depth_constraints["min"], self.depth_constraints["max"])
                )
                self.app.push_screen(ProcessingScreen(lore_document))
        except Exception as e:
            self.app.notify(f"Errore: {e}", severity="error")


    def validate_input(self) -> bool:
        result = True
        for key, value in self.branching_factors.items():
            if not isinstance(value, int):
                self.notify(f"Il {key.capitalize()} Branching Factor non è valido.", severity="error")
                result = False
        for key, value in self.depth_constraints.items():
            if not isinstance(value, int):
                self.notify(f"Il {key.capitalize()} Depth Constraint non è valido.", severity="error")
                result = False
        if not self.lore:
            self.app.notify("Inserisci i dettagli della lore prima di iniziare!", severity="error")
            result = False
        if self.branching_factors["min"] > self.branching_factors["max"] or self.branching_factors["min"] <= 1:
            self.notify("Branching Factors non validi.", severity="error")
            result = False
        if self.depth_constraints["min"] > self.depth_constraints["max"] or self.depth_constraints["min"] <= 1:
            self.notify("Depth Constraints non valide.", severity="error")
            result = False
        return result