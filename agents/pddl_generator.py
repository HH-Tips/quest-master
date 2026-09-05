import os
from utils import utils
from utils.pddl_metrics_handler import LoreDocument
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.language_models import BaseChatModel
from utils.pddl_analisys import PddlAnalysis, ValidationRes
import asyncio

DEFAULT_MAX_CONSECUTIVE_ERRORS = 2


async def generate_domain(model: BaseChatModel, lore_document: LoreDocument) -> str:
    domain_template = ChatPromptTemplate([
        ("system", "{system_prompt}"),
        ("human", "{human_prompt}")
    ])

    block_world = utils.load(os.getenv("EX_PDDL_BLOCK_WORLD"))
    domain_block_world = utils.split_pddl_content(block_world)[0]
    zeno_travel = utils.load(os.getenv("EX_PDDL_ZENO_TRAVEL"))
    domain_zeno_travel = utils.split_pddl_content(zeno_travel)[0]
    examples = [domain_block_world, domain_zeno_travel]

    formatted_prompt = utils.format_prompt(
        prompt_prefix="Ecco i dati per generare il file DOMAIN PDDL.",
        elements={
            "ESEMPIO - 1": examples[0],
            "ESEMPIO - 2": examples[1],
            "LORE DOCUMENT": lore_document,
        }
    )

    prompt = await domain_template.ainvoke({
        "system_prompt": utils.load(os.getenv("SP_PDDL_DOMAIN_GENERATOR")),
        "human_prompt": formatted_prompt
    })

    response = await model.ainvoke(prompt)
    return response.content.strip()


async def generate_problem(model: BaseChatModel, lore_document: LoreDocument, domain: str) -> str:
    problem_template = ChatPromptTemplate([
        ("system", "{system_prompt}"),
        ("human", "{human_prompt}")
    ])

    block_world = utils.load(os.getenv("EX_PDDL_BLOCK_WORLD"))
    zeno_travel = utils.load(os.getenv("EX_PDDL_ZENO_TRAVEL"))

    formatted_prompt = utils.format_prompt(
        prompt_prefix="Ecco i dati per generare il file PROBLEM PDDL.",
        elements={
            "ESEMPIO - 1": block_world,
            "ESEMPIO - 2": zeno_travel,
            "LORE DOCUMENT": lore_document,
            "DOMAIN": domain
        }
    )

    prompt = await problem_template.ainvoke({
        "system_prompt": utils.load(os.getenv("SP_PDDL_PROBLEM_GENERATOR")),
        "human_prompt": formatted_prompt
    })

    response = await model.ainvoke(prompt)
    return response.content.strip()


async def fix_syntax(model: BaseChatModel, pddl: tuple[str, str], analysis_result: PddlAnalysis) -> tuple[str, str]:
    system_prompt = utils.load(os.getenv("SP_PDDL_FIX_SYNTAX"))
    block_world = utils.load(os.getenv("EX_PDDL_BLOCK_WORLD"))
    zeno_travel = utils.load(os.getenv("EX_PDDL_ZENO_TRAVEL"))

    fix_syntax_template = ChatPromptTemplate([
        ("system", "{system_prompt}"),
        ("human", "{human_prompt}")
    ])

    formatted_prompt = utils.format_prompt(
        prompt_prefix="Ecco i dati per correggere la sintassi e/o la struttura del pddl:",
        elements={
            "PRIMO ESEMPIO DI UN DOMINIO E PROBLEMA CORRETTO": block_world,
            "SECONDO ESEMPIO DI UN DOMINIO E PROBLEMA CORRETTO": zeno_travel,
            "PDDL DA SISTEMARE": pddl,
            "LOG DI ERRORE": analysis_result.log
        }
    )

    prompt = await fix_syntax_template.ainvoke({
        "system_prompt": system_prompt,
        "human_prompt": formatted_prompt
     })

    response = await model.ainvoke(prompt)

    final_pddl = response.content
    domain, problem = utils.split_pddl_content(final_pddl)
    return domain, problem


async def add_solution(model: BaseChatModel, pddl: tuple[str, str]) -> tuple[str, str]:
    domain = pddl[0]
    problem = pddl[1]
    solution_template = ChatPromptTemplate([
        ("system", "{system_prompt}"),
        ("human", "{human_prompt}")
    ])

    block_world = utils.load(os.getenv("EX_PDDL_BLOCK_WORLD"))
    zeno_travel = utils.load(os.getenv("EX_PDDL_ZENO_TRAVEL"))

    formatted_prompt = utils.format_prompt(
        prompt_prefix="Ecco i dati per generare il file DOMAIN PDDL.",
        elements={
            "ESEMPIO - 1": block_world,
            "ESEMPIO - 2": zeno_travel,
            "DOMAIN DA ANALIZZARE": domain,
            "PROBLEM DA ANALIZZARE": problem
        }
    )

    prompt = await solution_template.ainvoke({
        "system_prompt": utils.load(os.getenv("SP_PDDL_ADD_SOLUTION")),
        "human_prompt": formatted_prompt
    })
    response = await model.ainvoke(prompt)
    domain, problem = utils.split_pddl_content(response.content)
    return domain, problem


async def add_comments_to_pddl(model: BaseChatModel, pddl: tuple[str, str]) -> tuple[str, str]:
    domain = pddl[0]
    problem = pddl[1]
    add_comments_template = ChatPromptTemplate([
        ("system", "{system_prompt}"),
        ("human", "{human_prompt}")
    ])

    formatted_prompt = utils.format_prompt(
        prompt_prefix="Ecco il domain e il problem PDDL a cui aggiungere i commenti:",
        elements={
            "DOMAIN:": domain,
            "PROBLEM:": problem
        }
    )

    prompt = await add_comments_template.ainvoke({
        "system_prompt": utils.load(os.getenv("SP_PDDL_ADD_COMMENTS")),
        "human_prompt": formatted_prompt
    })
    response = await model.ainvoke(prompt)
    domain, problem = utils.split_pddl_content(response.content)
    return domain, problem


async def suggest_fix(model: BaseChatModel, pddl: tuple[str, str], error: PddlAnalysis) -> str:
    domain = pddl[0]
    problem = pddl[1]
    suggest_template = ChatPromptTemplate([
        ("system", "{system_prompt}"),
        ("human", "{human_prompt}")
    ])

    formatted_prompt = utils.format_prompt(
        prompt_prefix="Ecco i dati per generare il suggerimento:",
        elements={
            "DOMAIN:": domain,
            "PROBLEM:": problem,
            "LOG DI ERRORE:": error.log
        }
    )

    prompt = await suggest_template.ainvoke({
        "system_prompt": utils.load(os.getenv("SP_PDDL_SUGGEST")),
        "human_prompt": formatted_prompt
    })
    response = await model.ainvoke(prompt)
    return response.content


async def edit_using_llm(model: BaseChatModel, pddl: tuple[str, str], user_prompt: str) -> tuple[str, str]:
    domain = pddl[0]
    problem = pddl[1]
    edit_template = ChatPromptTemplate([
        ("system", "{system_prompt}"),
        ("human", "{human_prompt}")
    ])
    formatted_prompt = utils.format_prompt(
        prompt_prefix="Ecco i dati per modificare il PDDL.",
        elements={
            "DOMAIN DA ANALIZZARE": domain,
            "PROBLEM DA ANALIZZARE": problem,
            "ISTRUZIONI UTENTE": user_prompt
        }
    )
    prompt = await edit_template.ainvoke({
        "system_prompt": await utils.async_load(os.getenv("SP_PDDL_EDIT_USING_LLM")),
        "human_prompt": formatted_prompt
    })
    response = await model.ainvoke(prompt)
    return utils.split_pddl_content(response.content)


async def validate_pddl(pddl_content: tuple[str, str]) -> PddlAnalysis:
    tmp = utils.get_temp()

    relative_dir_path = "quest-master/pddl"
    temp_dir = os.path.join(tmp, relative_dir_path)
    await utils.async_temp_store(f"{relative_dir_path}/domain.pddl", pddl_content[0])
    await utils.async_temp_store(f"{relative_dir_path}/problem.pddl", pddl_content[1])

    command = f"run --rm -v {temp_dir}:/benchmarks aibasel/downward --alias lama-first /benchmarks/domain.pddl /benchmarks/problem.pddl".split(" ")
    process = await asyncio.create_subprocess_exec(
        os.getenv("DOCKER"), *command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )

    stdout, stderr = await process.communicate()

    if process.returncode in ValidationRes.VALID.value:
        return PddlAnalysis(ValidationRes.VALID, None)
    elif process.returncode in ValidationRes.SYNTAX_ERROR.value:
        return PddlAnalysis(ValidationRes.SYNTAX_ERROR, stdout.decode())
    elif process.returncode in ValidationRes.NO_SOLUTION.value:
        return PddlAnalysis(ValidationRes.NO_SOLUTION, stdout.decode())
    elif process.returncode in ValidationRes.CRITICAL_ERROR.value:
        return PddlAnalysis(ValidationRes.CRITICAL_ERROR, stdout.decode())
    else:
        raise RuntimeError(f"Errore: {stderr.decode()}")
