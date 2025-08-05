# nus

<!-- TODO: Make it work, make it right, make it fast. -->

[![CI](https://github.com/hasansezertasan/nus/actions/workflows/ci.yml/badge.svg)](https://github.com/hasansezertasan/nus/actions/workflows/ci.yml)
[![PyPI - Version](https://img.shields.io/pypi/v/nus.svg)](https://pypi.org/project/nus)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/nus.svg)](https://pypi.org/project/nus)
[![License - MIT](https://img.shields.io/github/license/hasansezertasan/nus.svg)](https://opensource.org/licenses/MIT)
[![Latest Commit](https://img.shields.io/github/last-commit/hasansezertasan/nus)](https://github.com/hasansezertasan/nus)

[![Checked with mypy](http://www.mypy-lang.org/static/mypy_badge.svg)](http://mypy-lang.org/)
[![linting - Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/charliermarsh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![GitHub Tag](https://img.shields.io/github/tag/hasansezertasan/nus?include_prereleases=&sort=semver&color=black)](https://github.com/hasansezertasan/nus/releases/)

[![Downloads](https://pepy.tech/badge/nus)](https://pepy.tech/project/nus)
[![Downloads/Month](https://pepy.tech/badge/nus/month)](https://pepy.tech/project/nus)
[![Downloads/Week](https://pepy.tech/badge/nus/week)](https://pepy.tech/project/nus)

Software updates made easy and secure :sunglasses:.

-----

## Table of Contents

- [Installation](#installation)
- [Support](#support-heart)
- [Author](#author-person_with_crown)
- [Contributing](#contributing-heart)
- [Development](#development-toolbox)
- [Related Projects](#related-projects-chains)
- [License](#license-scroll)
- [Changelog](#changelog-memo)

## Installation

```console
pip install nus
```

## Support :heart:

If you have any questions or need help, feel free to open an issue on the [GitHub repository][nus].

## Author :person_with_crown:

This project is maintained by [Hasan Sezer Taşan][author], It's me :wave:

## Contributing :heart:

Any contributions are welcome! Please follow the [Contributing Guidelines](./CONTRIBUTING.md) to contribute to this project.

<!-- xc-heading -->
## Development :toolbox:

Clone the repository and cd into the project directory:

```sh
git clone https://github.com/hasansezertasan/nus
cd nus
```

The commands below can also be executed using the [xc task runner](https://xcfile.dev/), which combines the usage instructions with the actual commands. Simply run `xc`, it will pop up an interactive menu with all available tasks.

### `install`

Install the dependencies:

```sh
uv sync
```

### `style`

Run the style checks:

```sh
uv run --locked tox run -e style
```

### `ci`

Run the CI pipeline:

```sh
uv run --locked tox run
```

## Related Projects :chains:

- [tuf] - The Update Framework (TUF)
- [python-tuf] - Python implementation of the Update Framework

## License :scroll:

This project is licensed under the [MIT License](https://spdx.org/licenses/MIT.html).

## Changelog :memo:

For a detailed list of changes, please refer to the [CHANGELOG](./CHANGELOG.md).

<!-- Refs -->
[tuf]: https://github.com/theupdateframework
[python-tuf]: https://github.com/theupdateframework/python-tuf
[author]: https://github.com/hasansezertasan
[nus]: https://github.com/hasansezertasan/nus
