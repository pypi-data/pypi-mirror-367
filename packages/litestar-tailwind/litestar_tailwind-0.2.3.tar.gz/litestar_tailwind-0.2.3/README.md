# litestar-tailwind
forked from Tobi-De/litestar-tailwind-cli with improves

[![PyPI - Version](https://img.shields.io/pypi/v/litestar-tailwind-cli.svg)](https://pypi.org/project/litestar-tailwind-cli)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/litestar-tailwind-cli.svg)](https://pypi.org/project/litestar-tailwind-cli)

-----

> [!IMPORTANT]
> This plugin currently contains minimal features and is a work-in-progress

Provides a CLI plugin for [Litestar](https://litestar.dev) to use [Tailwind CSS](https://tailwindcss.com) via the Tailwind CLI.

## Table of Contents

- [litestar-tailwind](#litestar-tailwind)
  - [Table of Contents](#table-of-contents)
  - [Installation](#installation)
  - [Usage](#usage)
  - [License](#license)
  - [Changes from original](#changes-from-original)

## Installation

```console
pip install litestar-tailwind
```

## Usage

Configure and include the `TailwindCLIPlugin` in your Litestar app:

```python
from pathlib import Path

from litestar import Litestar
from litestar.static_files import create_static_files_router
from litestar.contrib.jinja import JinjaTemplateEngine
from litestar.template.config import TemplateConfig
from litestar_tailwind_cli import TailwindCLIPlugin

ASSETS_DIR = Path("assets")

tailwind_cli = TailwindCLIPlugin(
  use_server_lifespan=True,
  src_css=ASSETS_DIR / "css" / "input.css",
  dist_css=ASSETS_DIR / "css" / "tailwind.css",
)

app = Litestar(
    route_handlers=[create_static_files_router(path="/static", directories=["assets"])],
    debug=True,
    plugins=[tailwind_cli],
    template_config=TemplateConfig(
        directory=Path("templates"),
        engine=JinjaTemplateEngine,
    ),
)
```

```jinja
<head>
...
  <link rel="stylesheet" href="/static/css/tailwind.css">
</head>
```

After setting up, you can use the following commands:

- `litestar tailwind init`: This command initializes the tailwind configuration and downloads the CLI if it's not already installed.
- `litestar tailwind watch`: This command starts the Tailwind CLI in watch mode during development. You won't have to use this if you set `use_server_lifespan` to `True`.
- `litestar tailwind build`: This command builds a minified production-ready CSS file.

> [!NOTE]
> Don't forget to update the `content` key in `tailwind.config.js` to specify your templates directories.

The `TailwindCLIPlugin` has the following configuration options:

- `src_css`: The path to the source CSS file. Defaults to "css/input.css".
- `dist_css`: The path to the distribution CSS file. Defaults to "css/tailwind.css".
- `config_file`: The path to the Tailwind configuration file. Defaults to "tailwind.config.js".
- `use_server_lifespan`: Whether to use server lifespan. Defaults to `False`. It will start the Tailwind CLI in watch mode when you use the `litestar run` command.
- `conventional_path_resolve`: Only use the existing implementation for Tailwind CLI searches. defaults to `True`.
- `cli_version`: The version of the Tailwind CLI to download. Defaults to "latest".
- `src_repo`: The GitHub repository from which to download the Tailwind CLI. Defaults to `tailwindlabs/tailwindcss`.
- `asset_name`: The name of the asset to download from the repository. Defaults to `tailwindcss`.

For example, if you are using the repository `https://github.com/dobicinaitis/tailwind-cli-extra/tree/main`, you would set `src_repo` to `"dobicinaitis/tailwind-cli-extra"` and `asset_name` to `"tailwindcss-extra"`.

## License

`litestar-tailwind` and `litestar-tailwind-cli` (original library) is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
 is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.

## Changes from Original
- litestar-tailwind now supports tailwindcss v4. v3 is no longer supported.
- You can now use `{% tailwind_css() %}` to get the location of TailwindCSS's dist CSS. However, TailwindCSS files must be located under the web server's URI, `static`.
- By using `{% load_tailwind() %}`, you can now automatically load TailwindCSS. However, the same requirements apply as when using `{% tailwind_css() %}`.