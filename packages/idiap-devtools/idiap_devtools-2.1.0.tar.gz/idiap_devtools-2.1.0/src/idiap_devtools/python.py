# Copyright © 2022 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: BSD-3-Clause

import pathlib

import packaging.requirements
import tomli


def dependencies_from_pyproject_toml(
    path: pathlib.Path,
) -> tuple[str, list[packaging.requirements.Requirement]]:
    """Return a list with all ``project.optional-dependencies``.

    Arguments:

        path: The path to a ``pyproject.toml`` file to load


    Returns
    -------
        A list of optional dependencies (if any exist) on the provided python
        project.
    """

    data = tomli.load(path.open("rb"))

    deps = data.get("project", {}).get("dependencies", [])
    optional_deps = data.get("project", {}).get("optional-dependencies", {})

    retval = [packaging.requirements.Requirement(k) for k in deps]
    for v in optional_deps.values():
        retval += [packaging.requirements.Requirement(k) for k in v]

    return data.get("project", {}).get("name", "UNKNOWN"), retval
