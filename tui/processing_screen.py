import os
import pytz
from datetime import datetime

from utils import utils
from utils.pddl_metrics_handler import PddlMetric, get_pddl_metrics, save_metrics
from utils.pddl_analisys import ValidationRes
from utils.lore_document import LoreDocument
from textual.screen import Screen
from textual.reactive import reactive
from textual.app import ComposeResult
from textual.css.query import NoMatches
import agents.lore_agent as lore_agent
import agents.html_generator as html_generator
from tui.editor import TextualEditorScreen
import agents.pddl_generator as pddl_generator
from textual.containers import Vertical, Horizontal
from tui.components.LoadingLabel import LoadingLabel
from langchain_core.language_models import BaseChatModel
from textual.widgets import Header, Footer, TextArea, Static, Label, TabbedContent, TabPane


class ProcessingScreen(Screen):
    """Schermo che mostra l'avanzamento dell'elaborazione dell'LLM."""

    CSS_PATH = "stylesheets/processing_screen.tcss"
    MAX_ATTEMPTS = 2  # numero massimo di tentativi consecutivi di aggiustare un PDDL prima di rigenerarlo da capo.
    ERRORS_COUNTER_ID = "errors-counter"

    text = reactive("")
    attempt = reactive(1)
    syntax_errors = reactive(0)
    logic_errors = reactive(0)
    critical_errors = reactive(0)
    errors_to_regeneration = reactive(MAX_ATTEMPTS)
    regenerations = reactive(0)
    operation_info = reactive("")


    def __init__(self, lore_document: LoreDocument, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.lore_document = lore_document
        time_separator = ":" if utils.is_unix_based() else "-"
        self.day, self.time = datetime.now(tz=pytz.timezone('Europe/Rome')).strftime(f'%d-%m-%Y_%H{time_separator}%M{time_separator}%S').split('_')


    def watch_text(self, value: str) -> None:
        try:
            self.query_one("#logs-tab-text-area", TextArea).load_text(value)
        except NoMatches:
            return


    def watch_attempt(self, value: int) -> None:
        try:
            self.query_one("#stat-attempt", Label).update(f"Tentativi: {value}")
        except NoMatches:
            return


    def watch_syntax_errors(self, value: int) -> None:
        try:
            self.query_one("#stat-syntax", Label).update(f"Errore sintassi: {value}")
        except NoMatches:
            return


    def watch_logic_errors(self, value: int) -> None:
        try:
            self.query_one("#stat-logic", Label).update(f"Errore logica: {value}")
        except NoMatches:
            return


    def watch_critical_errors(self, value: int) -> None:
        try:
            self.query_one("#stat-critical", Label).update(f"Errore critico: {value}")
        except NoMatches:
            return


    def watch_errors_to_regeneration(self, value: int) -> None:
        try:
            self.query_one(f"#{self.ERRORS_COUNTER_ID}", Label).update(f"{value}")
        except NoMatches:
            return


    def watch_regenerations(self, value: int) -> None:
        try:
            self.query_one("#stat-regen", Label).update(f"Rigenerazioni: {value}")
        except NoMatches:
            return


    def watch_operation_info(self, value: str) -> None:
        try:
            self.query_one("#operation-info", LoadingLabel).set_text(value)
        except NoMatches:
            return


    async def add_text_area_tab(self, tab_id: str, title: str, content: str = "", readonly: bool = False) -> None:
        tabbed_content = self.query_one(TabbedContent)
        pane = TabPane(title=title, id=tab_id)
        await tabbed_content.add_pane(pane)
        await pane.mount(TextArea(content, id=f"{tab_id}-text-area", read_only=readonly))
        tabbed_content.active = tab_id

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal(id="top-stats"):
            yield Label(f"Tentativi: {self.attempt}", id="stat-attempt", classes="stat-item")
            yield Label(f"Errore sintassi: {self.syntax_errors}", id="stat-syntax", classes="stat-item")
            yield Label(f"Errore logica: {self.logic_errors}", id="stat-logic", classes="stat-item")
            yield Label(f"Errore critico: {self.critical_errors}", id="stat-critical", classes="stat-item")
            yield Label(f"Rigenerazioni: {self.regenerations}", id="stat-regen", classes="stat-item")

        with Vertical():
            yield LoadingLabel("", id="operation-info")
            with TabbedContent():
                with TabPane("logs", id="logs-tab"):
                    yield TextArea("", id="logs-tab-text-area", read_only=True)
                with TabPane("Lore Document", id="lore-document-tab"):
                    yield TextArea(self.lore_document.to_json(), id="lore-document-tab-text-area", read_only=True)



        with Horizontal(id="bottom-bar"):
            errors_label = Static("Errori alla rigenerazione:", id="errors-label")
            errors_label.visible = False
            yield errors_label
            errors_counter_label = Label(f"{self.errors_to_regeneration}", id=self.ERRORS_COUNTER_ID)
            errors_counter_label.visible = False
            yield errors_counter_label

        yield Footer()


    def action_quit(self) -> None:
        """Viene chiamata quando premi CTRL+Q (azione predefinita)."""
        self.notify("Chiusura in corso...")
        self.app.action_quit()


    def on_mount(self) -> None:
        self.run_worker(self.generate_game())


    async def generate_game(self):
        await self.lore_refinement()
        domain, problem = await self.pddl_generation()
        title = utils.get_pddl_title(domain)
        await utils.async_store(os.getenv("OUT_PDDL_FMT").format(title=title, day=self.day, time=self.time), utils.join_pddl_content((domain, problem)))
        await self.add_text_area_tab("pddl-tab", "PDDL", (3*"\n").join([domain, problem]), readonly=True)

        self.operation_info = "Finalizing Lore"
        finalized_lore = await lore_agent.finalize_lore(self.app.model, self.lore_document, (domain, problem))
        await self.add_text_area_tab("finalized-lore-tab", "Finalized Lore", finalized_lore.lore, readonly=True)
        await utils.async_store(os.getenv("OUT_FINALIZED_LORE").format(title=title, day=self.day, time=self.time), finalized_lore.to_json())

        self.operation_info = "Generating HTML"
        html = await html_generator.generate_html(self.app.model, (domain, problem), finalized_lore)
        await self.add_text_area_tab("html-tab", "HTML", html, readonly=True)
        html_output_path = os.getenv("OUT_HTML_FMT").format(title=title, day=self.day, time=self.time)
        await utils.async_store(html_output_path, html)
        self.operation_info = "Done"
        self.query_one("#operation-info", LoadingLabel).set_loading(False)
        utils.xdg_open(html_output_path)


    async def lore_refinement(self):
        self.operation_info = "Preprocessing lore document"
        model: BaseChatModel = self.app.model
        self.lore_document = await lore_agent.refine_lore(model, self.lore_document)
        await self.add_text_area_tab("refined-lore-tab", "Refined Lore Document", self.lore_document.lore, readonly=True)


    async def pddl_generation(self) -> tuple[str, str]:
        self.operation_info = "Generating PDDL"
        self.query_one("#errors-label").visible = True
        self.query_one(f"#{self.ERRORS_COUNTER_ID}").visible = True
        model: BaseChatModel = self.app.model

        domain = await pddl_generator.generate_domain(model, self.lore_document)
        problem = await pddl_generator.generate_problem(model, self.lore_document, domain)

        pddl_metric: PddlMetric = PddlMetric(self.lore_document, 0, 0, 0)
        self.errors_to_regeneration = self.MAX_ATTEMPTS  # numero massimo di tentativi consecutivi di aggiustare un PDDL prima di rigenerarlo da capo.

        validation_result = await pddl_generator.validate_pddl((domain, problem))
        iterazione_sintassi = 0
        iterazione_logica = 0
        iterazione_critica = 0
        rigenerazione = 0

        while validation_result.exit_code != ValidationRes.VALID:
            self.attempt += 1
            if validation_result.exit_code == ValidationRes.SYNTAX_ERROR and self.errors_to_regeneration > 0:
                self.errors_to_regeneration -= 1
                pddl_metric.syntax_errors += 1
                self.syntax_errors += 1
                domain, problem = await pddl_generator.fix_syntax(model, (domain, problem), validation_result)
                iterazione_sintassi += 1
                await utils.async_store(os.getenv("OUT_PDDL_FAULTY_FMT").format(day=self.day, err="syntax_err", time=self.time, regen=rigenerazione, iter=iterazione_sintassi), utils.join_pddl_content((domain, problem)))
            elif validation_result.exit_code == ValidationRes.NO_SOLUTION and self.errors_to_regeneration > 0:
                self.errors_to_regeneration -= 1
                pddl_metric.logic_errors += 1
                self.logic_errors += 1
                domain, problem = await pddl_generator.add_solution(model, (domain, problem))
                iterazione_logica += 1
                await utils.async_store(os.getenv("OUT_PDDL_FAULTY_FMT").format(day=self.day, err="logic_err", time=self.time, regen=rigenerazione, iter=iterazione_logica), utils.join_pddl_content((domain, problem)))
            else:
                # ERRORE CRITICO o MAX_TRIES: rigenerare da capo.
                if self.errors_to_regeneration > 0:
                    pddl_metric.critical_errors += 1
                    self.critical_errors += 1
                    iterazione_critica += 1
                await utils.async_store(os.getenv("OUT_PDDL_FAULTY_FMT").format(day=self.day, err="critical_err", time=self.time, regen=rigenerazione, iter=iterazione_critica), utils.join_pddl_content((domain, problem)))
                hint = await pddl_generator.suggest_fix(model, (domain, problem), validation_result)
                modified_pddl = await self.app.push_screen_wait(TextualEditorScreen(hint, (domain, problem)))
                if modified_pddl:
                    domain = modified_pddl[0]
                    problem = modified_pddl[1]
                else:
                    rigenerazione += 1
                    self.regenerations += 1
                    self.errors_to_regeneration = pddl_generator.DEFAULT_MAX_CONSECUTIVE_ERRORS
                    iterazione_sintassi = 0
                    iterazione_logica = 0
                    iterazione_critica = 0
                    domain = await pddl_generator.generate_domain(model, self.lore_document)
                    problem = await pddl_generator.generate_problem(model, self.lore_document, domain)
            self.text += f"Validation result[{pddl_metric.total_errors()}]:  {validation_result}{'\n'*3}"
            validation_result = await pddl_generator.validate_pddl((domain, problem))
        # Salva le metriche.
        try:
            metrics = get_pddl_metrics(os.getenv("OUT_METRICS_PDDL_GENERATION"))
        except FileNotFoundError:
            metrics = []
        metrics.append(pddl_metric)
        save_metrics(os.getenv("OUT_METRICS_PDDL_GENERATION"), metrics)
        self.operation_info = "PDDL Generated correctly"
        self.query_one("#errors-label").visible = False
        self.query_one(f"#{self.ERRORS_COUNTER_ID}").visible = False
        return domain, problem