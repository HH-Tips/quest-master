import os
from langchain_core.prompts import ChatPromptTemplate
from utils.lore_document import LoreDocument
import utils.utils as utils
from langchain_core.language_models import BaseChatModel

async def refine_lore(model: BaseChatModel, lore_document: LoreDocument) -> LoreDocument:
    chat_template = ChatPromptTemplate([
        ("system", "{system_prompt}"),
        ("human", "{lore}")
    ])

    prompt_value = await chat_template.ainvoke({
        "system_prompt": utils.load(os.getenv("SP_STORY_GENERATOR")),
        "lore": lore_document
    })
    response = await model.ainvoke(prompt_value)

    return LoreDocument(
        lore = response.content,
        branching_factor = lore_document.branching_factor,
        depth_constraint = lore_document.depth_constraint
    )


async def finalize_lore(model: BaseChatModel, lore_doc: LoreDocument, pddl: tuple[str, str]) -> LoreDocument:
    domain = pddl[0]
    problem = pddl[1]
    finalize_template = ChatPromptTemplate([
        ("system", "{system_prompt}"),
        ("human", "{human_prompt}")
    ])
    formatted_prompt = utils.format_prompt(
        prompt_prefix="Ecco i dati per generare il file LORE.",
        elements={
            "DOMAIN": domain,
            "PROBLEM": problem,
            "ESEMPIO DI LORE": lore_doc.lore
        }
    )
    prompt = await finalize_template.ainvoke({
        "system_prompt": utils.load(os.getenv("SP_PDDL_FINALIZE_LORE")),
        "human_prompt": formatted_prompt
    })
    response = await model.ainvoke(prompt)

    return LoreDocument(
        lore=response.content,
        branching_factor=lore_doc.branching_factor,
        depth_constraint=lore_doc.depth_constraint
    )
