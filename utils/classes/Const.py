import json
from dataclasses import dataclass
from utils.library import files

conf = files.get_yaml("config.yaml")
patch = conf["patch"][-5:]


@dataclass(frozen=True)
class FileName:
    config: str
    gamestrings: str
    heroes: str
    heroes_ru: str
    pancho: str
    stlk: str

@dataclass(frozen=True)
class Json:
    heroes: dict
    heroes_ru: dict
    gamestrings: dict
    pancho: dict
    stlk: dict


data = FileName(
    config="config.yaml",
    gamestrings=f"data/gamestrings{patch}.json",
    heroes=f"data/heroesdata{patch}.json",
    heroes_ru=f"data/heroesdata_ru.json",
    pancho=f"data/pancho.json",
    stlk=f"data/stlk_builds.json"
)

jsons = Json(
    heroes=files.get_json(data.heroes),
    heroes_ru=files.get_json(data.heroes_ru),
    gamestrings=files.get_json(data.gamestrings),
    pancho=files.get_json(data.pancho),
    stlk=files.get_json(data.stlk)
)