import asyncio
import os
import sys
import json
import hashlib
from concurrent.futures.thread import ThreadPoolExecutor
from dataclasses import is_dataclass, asdict
from utils.json_serializable import JsonSerializable
import regex as re


def load(file_path: str) -> str:
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            f.close()
            return content
    except UnicodeDecodeError:
        with open(file_path, "r", encoding="cp1252") as f:
            content =  f.read()
            f.close()
            return content


def store(file_path: str, content: str) -> None:
    dirname = os.path.dirname(file_path)
    if not os.path.exists(dirname):
        os.makedirs(dirname)
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
            f.close()
    except UnicodeDecodeError:
        with open(file_path, "w", encoding="cp1252") as f:
            f.write(content)
            f.close()


def temp_store(relative_path: str, content: str) -> str:
    temp_directory = get_temp()
    path = os.path.join(temp_directory, relative_path)
    store(path, content)
    return path


async def async_load(file_path: str) -> str:
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor() as executor:
        return await loop.run_in_executor(executor, load, file_path)


async def async_store(file_path: str, content: str) -> None:
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor() as executor:
        await loop.run_in_executor(executor, store, file_path, content)


async def async_temp_store(relative_path: str, content: str) -> None:
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor() as executor:
        await loop.run_in_executor(executor, temp_store, relative_path, content)


def is_unix_based() -> bool:
    return os.name != "nt"


def format_prompt(elements: dict[str,object], prompt_prefix: str = "") -> str:
    formatted_prompt = prompt_prefix + "\n"
    for key, value in elements.items():
        formatted_prompt += f"""[{key}]\n{format_value(value)}\n\n"""
    return formatted_prompt


def format_value(value: object) -> str:
    if isinstance(value, str):
        return value
    elif isinstance(value, JsonSerializable):
        return value.to_json()
    elif is_dataclass(value):
        return json.dumps(asdict(value), sort_keys=True, indent=4)
    else:
        try :
            return json.dumps(value, sort_keys=True, indent=4)
        except TypeError:
            return value.__str__()


def get_temp():
    tmp = "/dev/shm"
    if sys.platform == "win32":
        tmp = os.getenv("temp")
    if sys.platform == "darwin":
        tmp = "/tmp"
    return tmp


def md5sum(content: str) -> str:
    return hashlib.md5(content.encode()).hexdigest()


def md5sum_file(file: str) -> str:
    content = load(file)
    return md5sum(content)


def get_default_texteditor():
    platform = sys.platform
    default_editor = os.getenv("EDITOR") or "nano"

    if platform == "linux" or platform == "darwin":
        return default_editor
    else:  # win32
        return "start"


def split_pddl_content(pddl_content: str) -> tuple[str, str]:
    pddl = pddl_content
    pddl = pddl.replace("```pddl", "").replace("```", "") 
    pddl = pddl.split("(define (problem")
    pddl[1] = "(define (problem" + pddl[1]
    for i in range(len(pddl)):
        pddl[i] = pddl[i].strip()
    return pddl[0], pddl[1]


def join_pddl_content(pddl: tuple[str, str]) -> str:
    return (3*"\n").join(pddl)


def get_pddl_title(domain: str) -> str:
    match = re.search(r"\(define\s+\(domain\s+([^\s\)]+)", domain, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return ""


def xdg_open(file_path: str) -> None:
    if sys.platform == "win32":
        os.system(f"start {file_path}")
    elif sys.platform == "darwin":
        os.system(f"open {file_path}")
    else:
        os.system(f"xdg-open {file_path}")