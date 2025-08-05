# SPDX-FileCopyrightText: 2024-present Tobi DEGNON <tobidegnon@proton.me>
# SPDX-FileCopyrightText: 2025 Aoi <aoicistus@gmail.com>
#
# SPDX-License-Identifier: MIT
from __future__ import annotations

import subprocess
import sys
from contextlib import contextmanager
from dataclasses import dataclass
from dataclasses import field
from pathlib import Path
from typing import Iterator
from typing import TYPE_CHECKING
import shutil

from litestar.config.app import AppConfig
from litestar.template.base import TemplateEngineProtocol
from litestar.plugins import CLIPlugin
from litestar_tailwind_cli.utils import OS_TYPE
from rich import print as rprint

if TYPE_CHECKING:
    from litestar import Litestar
    from click import Group

__all__ = ("TailwindCLIPlugin",)


def _default_cli_path(
    conventional_path_resolve: bool = True, custom_bin_name: str = "tailwind-cli"
) -> Path:
    if conventional_path_resolve:
        bin_path = Path(sys.prefix) / "bin"
        extension = ".exe" if OS_TYPE == "windows" else ""
        return bin_path / f"{custom_bin_name}{extension}"
    else:
        bin_path = Path(sys.prefix) / "bin"
        extension = ".exe" if OS_TYPE == "windows" else ""
        location = shutil.which(f"{custom_bin_name}{extension}")
        if location:
            return location
        else:
            if custom_bin_name == "tailwindcss":
                return _default_cli_path(custom_bin_name="tailwind")
            elif custom_bin_name == "tailwind-cli":
                return _default_cli_path(custom_bin_name="tailwindcss")
        return bin_path / f"tailwind-cli{extension}"

def get_tailwind_path(dist: str | Path = "css/tailwind.css"):
    return "static" / dist

def load_tailwind(dist: str | Path = "css/tailwind.css"):
    tailwind_location = get_tailwind_path(dist)
    return f"""
    <link rel="preload" href="{tailwind_location}" as="style" />
    <link rel="stylesheet" href="{tailwind_location}" />
    """

@dataclass(frozen=True)
class TailwindCLIPlugin(CLIPlugin):
    src_css: str | Path = "css/input.css"
    dist_css: str | Path = "css/tailwind.css"
    config_file: str | Path = "tailwind.config.js"
    use_server_lifespan: bool = False
    cli_version: str = "latest"
    src_repo: str = "tailwindlabs/tailwindcss"
    asset_name: str = "tailwindcss"
    conventional_path_resolve: bool = True
    cli_path: str | Path | None = field(init=None)

    def __post_init__(self):
        if self.cli_path is None:
            object.__setattr__(
                self, "cli_path", _default_cli_path(self.conventional_path_resolve)
            )


    def on_app_init(self, app_config: AppConfig) -> AppConfig:
        engine: TemplateEngineProtocol = app_config.template_config.engine_instance
        engine.register_template_callable(
            key="tailwind_css",
            template_callable=lambda: get_tailwind_path(self.dist_css),
        )
        engine.register_template_callable(
            key="load_tailwind",
            template_callable=lambda: load_tailwind(self.dist_css),
        )
        return app_config

    def on_cli_init(self, cli: Group) -> None:
        from litestar_tailwind_cli.cli import tailwind_group

        cli.add_command(tailwind_group)
        return super().on_cli_init(cli)

    @property
    def tailwind_cli_is_installed(self) -> bool:
        try:
            subprocess.run([self.cli_path], capture_output=True, check=True)
        except FileNotFoundError:
            return False
        return True

    @contextmanager
    def server_lifespan(self, app: Litestar) -> Iterator[None]:
        import multiprocessing
        import platform
        from litestar_tailwind_cli.cli import run_tailwind_watch

        run_using_server_lifespan = self.use_server_lifespan and app.debug
        if not run_using_server_lifespan:
            yield

        if platform.system() == "Darwin":
            multiprocessing.set_start_method("fork", force=True)

        rprint("[yellow]Starting tailwind watch process[/]")
        process = multiprocessing.Process(
            target=run_tailwind_watch,
            args=(self,),
        )

        try:
            process.start()
            yield
        finally:
            if process.is_alive():
                process.terminate()
                process.join()
            rprint("[yellow]Tailwind watch process stopped[/]")
