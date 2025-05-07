import json
from datetime import datetime
from uuid import uuid4

import env

from .__schema__ import Collection


class ProjectData(Collection):
    BASE = "projects"
    id: int
    name: str
    links: dict[str, dict]
    deadtime: str

    @classmethod
    def read(cls, id: str):
        try:
            with open(f"{env.BASE_DIR}/data/{cls.BASE}/{id}.json", "r") as file:
                return cls(id=str(id), **json.load(file))
        except FileNotFoundError:
            return None

    @classmethod
    def new(cls, name: str, deadtime: str):
        ids = [project.id for project in cls.read_all()]

        project_id = None
        while True:
            project_id = str(uuid4())
            if project_id and project_id not in ids:
                break

        ProjectData(
            id=project_id,
            name=name,
            deadtime=str(deadtime),
            links={},
        ).update()

        return project_id

    def add_link(
        self, *, user_id: int | str, now: datetime | str, link: str, dead: bool
    ):
        self.links[str(user_id)] = {
            "datetime": str(now),
            "link": link,
            "dead": dead,
        }
        self.update()
