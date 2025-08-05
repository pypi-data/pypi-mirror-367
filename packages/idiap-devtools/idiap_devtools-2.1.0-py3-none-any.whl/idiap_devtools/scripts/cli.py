# Copyright © 2022 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: BSD-3-Clause

import click

from ..click import AliasedGroup
from ..logging import setup
from .badges import badges
from .changelog import changelog
from .getpath import getpath
from .jobs import jobs
from .lasttag import lasttag
from .release import release
from .runners import runners
from .settings import settings

logger = setup(__name__.split(".", 1)[0])


@click.group(
    cls=AliasedGroup,
    context_settings=dict(help_option_names=["-?", "-h", "--help"]),
)
@click.version_option()
def cli() -> None:
    """Commands that interact directly with GitLab.

    Commands defined here are supposed to interact with gitlab, and
    add/modify/remove resources on it directly.

    To avoid repetitive asking, create a configuration file as indicated
    at :ref:`idiap-devtools.install.setup.gitlab` section of the user
    guide.
    """
    pass


cli.add_command(changelog)
cli.add_command(release)
cli.add_command(badges)
cli.add_command(runners)
cli.add_command(jobs)
cli.add_command(getpath)
cli.add_command(lasttag)
cli.add_command(settings)
