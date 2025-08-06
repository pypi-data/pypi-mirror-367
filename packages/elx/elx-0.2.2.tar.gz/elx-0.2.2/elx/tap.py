import asyncio
import logging
import contextlib
from functools import cached_property
from pathlib import Path
from typing import Generator, List, Optional
from elx.singer import Singer, require_install, BUFFER_SIZE_LIMIT
from elx.catalog import Stream, Catalog
from elx.json_temp_file import json_temp_file
from subprocess import Popen, PIPE


class Tap(Singer):
    def __init__(
        self,
        spec: str,
        executable: str | None = None,
        config: dict = {},
        deselected: List[str] = None,
        replication_keys: dict = {},
        schema: dict = {},
    ):
        super().__init__(spec, executable, config)
        self.deselected = deselected
        self.replication_keys = replication_keys
        self.schema = schema

    def discover(self, config_path: Path) -> dict:
        """
        Run the tap in discovery mode.

        Args:
            config_path (Path): Path to the config file.

        Returns:
            dict: The catalog.
        """
        logging.debug(f"Discovering {self.executable} with {config_path}")
        return self.run(["--config", str(config_path), "--discover"])

    @cached_property
    def catalog(self) -> Catalog:
        """
        Discover the catalog.

        Returns:
            Catalog: The catalog as a Pydantic model.
        """
        with json_temp_file(self.config) as config_path:
            catalog = self.discover(config_path)
            catalog = Catalog(**catalog)
            catalog = catalog.deselect(patterns=self.deselected)
            catalog = catalog.set_replication_keys(
                replication_keys=self.replication_keys
            )
            catalog = catalog.add_properties_to_schema(custom_schema=self.schema)
            return catalog

    @contextlib.asynccontextmanager
    @require_install
    async def process(
        self,
        state: dict = {},
        streams: Optional[List[str]] = None,
    ) -> Generator[Popen, None, None]:
        """
        Run the tap process.

        Returns:
            Popen: The tap process.
        """
        catalog = self.catalog.select(streams=streams)

        with json_temp_file(self.config) as config_path:
            with json_temp_file(catalog.dict(by_alias=True)) as catalog_path:
                with json_temp_file(state) as state_path:
                    yield await asyncio.create_subprocess_exec(
                        *[
                            self.executable,
                            "--config",
                            str(config_path),
                            "--catalog",
                            str(catalog_path),
                            "--state",
                            str(state_path),
                        ],
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE,
                        limit=BUFFER_SIZE_LIMIT,
                    )

    def invoke(
        self,
        streams: Optional[List[str]] = None,
        limit: int = None,
        debug: bool = True,
    ) -> None:
        """
        Invoke the tap.

        Args:
            streams (Optional[List[str]], optional): The streams to invoke. Defaults to None.
        """
        # TODO: Make use of the process context manager.

        catalog = self.catalog.select(streams=streams)

        with json_temp_file(self.config) as config_path:
            with json_temp_file(catalog.dict(by_alias=True)) as catalog_path:
                with json_temp_file({}) as state_path:
                    process = Popen(
                        [
                            self.executable,
                            "--config",
                            str(config_path),
                            "--catalog",
                            str(catalog_path),
                            "--state",
                            str(state_path),
                        ],
                        stdout=PIPE,
                        stderr=PIPE,
                    )

                    n_lines = 0

                    for line in process.stdout:
                        if limit and n_lines >= limit:
                            break
                        if debug:
                            print(line.decode("utf-8"))
                        n_lines += 1
