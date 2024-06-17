import typing as t

from backup_me.destinations import DESTINATIONS, BaseDestination
from backup_me.sources import SOURCES, BaseSource


class Config:
    app: str
    sources: t.List[BaseSource]
    destinations: t.List[BaseDestination]

    def __init__(
        self,
        config: t.Dict[str, t.Any],
    ) -> None:
        self.app = config["app"]
        self.sources = []
        self.destinations = []
        for raw_src in config["sources"]:
            src_klass = SOURCES.get(raw_src["type"])
            if not src_klass:
                raise ValueError("Invalid source type")
            src = src_klass(**raw_src)
            self.sources.append(src)

        for raw_dest in config["destinations"]:
            dest_klass = DESTINATIONS.get(raw_dest["type"])
            if not dest_klass:
                raise ValueError("Invalid destination type")
            dest = dest_klass(**raw_dest)
            self.destinations.append(dest)
