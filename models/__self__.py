import json
import os

import env
from utils import Log


class Migration:
    data = {
        "dirs": ["projects", "quizes", "users", "weeks", "products"],
        "files": {
            "[]": ["channels", "evaluations", "files"],
            "{}": ["outlist"],
        },
        "tables": [
            ("transactions", "datetime,id,current,operation,amount,reason"),
            ("interactions", "datetime,id,name,command,options"),
        ],
    }
    storage = [
        "files",
        "images",
        "subjects",
        "solutions",
        "logs",
        "evaluations",
        "errors",
    ]
    config = {
        "global": {
            str: ("REPOSITORY",),
            int: ("GUILD",),
            list: ("ROLES", "USERS"),
            dict: ("CHANNELS", "EMOJIS", "REACTIONS", "EXTENSIONS"),
        },
        "leaderboard": {dict: ("ALL",)},
        "msgs": {dict: ("LEADERBOARD",)},
    }

    @classmethod
    def run(cls) -> None:
        base_dir = os.path.abspath(env.BASE_DIR)

        for base in ("data", "storage", "config", "backup"):
            os.makedirs(os.path.join(base_dir, base), exist_ok=True)

        for dir in cls.data["dirs"]:
            dir_path = os.path.join(base_dir, "data", dir)
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)
                Log.info("Data", f"Dir {os.path.relpath(dir_path)} created.")

        for content, files in cls.data["files"].items():
            for file in files:
                file_path = os.path.join(base_dir, "data", f"{file}.json")
                try:
                    with open(file_path, "x") as f:
                        f.write(content)
                        Log.info("Data", f"File {os.path.relpath(file_path)} created.")
                except FileExistsError:
                    pass

        for table_name, table_header in cls.data["tables"]:
            table_path = os.path.join(base_dir, "data", f"{table_name}.csv")
            try:
                with open(table_path, "x") as f:
                    f.write(table_header.replace("\n", "") + "\n")
                    Log.info("Data", f"Table {os.path.relpath(table_path)} created.")
            except FileExistsError:
                pass

        for store in cls.storage:
            store_path = os.path.join(base_dir, "storage", store)
            if not os.path.exists(store_path):
                os.makedirs(store_path)
                Log.info("Storage", f"{os.path.relpath(store_path)} created.")

        for config, attrs in cls.config.items():
            config_path = os.path.join(base_dir, "config", f"{config}.json")
            try:
                with open(config_path, "x") as f:
                    f.write("{}")
                    Log.info("Config", f"{os.path.relpath(config_path)} created.")
            except FileExistsError:
                pass

            with open(config_path, "r") as f:
                configs: dict = json.load(f)

            changed: bool = False

            for attr_type, attributes in attrs.items():
                for attribute in attributes:
                    if attribute not in configs:
                        configs[attribute] = attr_type()
                        changed = True

            if changed:
                with open(config_path, "w") as f:
                    json.dump(configs, f, indent=2)
