import os
import json
import random
import re
import utils.utils as utils
from utils.lore_document import LoreDocument
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.language_models import BaseChatModel


async def generate_html(model: BaseChatModel, pddl: tuple[str, str], lore_document: LoreDocument) -> str:
    game = None
    while not validate_json(game):
        try:
            game_json = await generate_json(model, pddl, lore_document)
            game = json.loads(game_json)
        except json.decoder.JSONDecodeError:
            game = None
    remove_text_in_parenthesis(game)
    shuffle_choices(game)
    base_html = await utils.async_load(os.getenv("BASE_HTML"))
    html_finale = base_html.replace("$JSON_HERE", json.dumps(game))
    return html_finale


async def generate_json(model: BaseChatModel,  pddl: tuple[str, str], lore_document: LoreDocument) -> str:
    branching_factor = lore_document.branching_factor
    depth_constraint = lore_document.depth_constraint

    prompt_template = ChatPromptTemplate([
        ("system", "{system_prompt}"),
        ("human", "{human_prompt}")
    ])

    example_json = await utils.async_load(os.getenv("EX_JSON_MUSEUM_HEIST"))
    example_pddl = await utils.async_load(os.getenv("EX_PDDL_MUSEUM_HEIST"))

    formatted_prompt = utils.format_prompt(
        prompt_prefix="Ecco i dati per generare il json:",
        elements={
            "PDDL PER GENERARE IL JSON:": utils.join_pddl_content(pddl),
            "ESEMPIO PDDL:": example_pddl,
            "ESEMPIO JSON:": example_json,
            "LORE": lore_document.lore,
            "BRANCHING FACTOR:": branching_factor,
            "DEPTH CONSTRAINT:": depth_constraint
        }
    )
    prompt = await prompt_template.ainvoke({
        "system_prompt": utils.load(os.getenv("SP_GAME_JSON_GENERATOR")),
        "human_prompt": formatted_prompt
    })
    response = await model.ainvoke(prompt)
    return response.content


def validate_json(game: dict) -> bool:
    if game is None:
        return False
    try:
        for state_name in game["states"]:
            state = game["states"][state_name]
            if "choices" in state:
                for choice in state["choices"]:
                    # Verifica che ci sia un prossimo stato e che non sia un ciclo sullo stesso stato.
                    if choice["next"] not in game["states"] or choice["next"] == state_name:
                        return False
        return has_solution(game, game["initialState"])
    except RuntimeError:
        return False


def has_solution(game: dict, current_state: str, visited_states: set[str] = None) -> bool:
    if not visited_states:
        visited_states = set()
    state = game["states"][current_state]
    result = False
    if current_state in visited_states:
        return False
    visited_states.add(current_state)
    if "type" in state:
        return state["type"] == "victory"
    for choice in state["choices"]:
        next_state_name = choice["next"]
        result = result or has_solution(game, next_state_name, visited_states)
        if result:
            return result
    return result


def shuffle_choices(game: dict) -> None:
    for state in game["states"].values():
        if "choices" in state:
            random.shuffle(state["choices"])

def remove_text_in_parenthesis(game: dict) -> None:
    for state in game["states"].values():
        if "choices" in state:
            for choice in state["choices"]:
                choice["text"] = re.sub(r'\s*\([^)]*\)', '', choice["text"]).strip() 