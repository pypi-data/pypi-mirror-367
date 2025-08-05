# Copyright © 2022 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: BSD-3-Clause
"""Utilities to needed to release packages."""

import difflib
import logging
import re
import time

import gitlab
import gitlab.v4.objects
import packaging.requirements
import packaging.version
import tomlkit

logger = logging.getLogger(__name__)


def _update_readme(
    contents: str,
    version: str,
    default_branch: str,
) -> str:
    """Update README file text to make it release/latest ready.

    Inside text of the readme, replaces parts of the links to the provided
    version. If version is not provided, replace to `stable` or the default
    project branch name.

    Arguments:

        context: Text of the README.rst file from a package

        version: Format of the version string is '#.#.#'

        default_branch: The name of the default project branch to use

    Returns
    -------
        New text of readme with all replaces done
    """

    variants = {
        "available",
        "latest",
        "main",
        "master",
        "stable",
        default_branch,
        packaging.version.VERSION_PATTERN,
    }

    # matches the graphical badge in the readme's text with the given version
    doc_image_re = re.compile(
        r"docs\-(" + "|".join(variants) + r")\-", re.VERBOSE | re.IGNORECASE
    )

    # matches all other occurrences we need to handle
    branch_re = re.compile(
        r"/(" + "|".join(variants) + r")", re.VERBOSE | re.IGNORECASE
    )

    new_contents = []
    for line in contents.splitlines():
        if branch_re.search(line) is not None:
            if "gitlab" in line:  # gitlab links
                replacement = (
                    "/v%s" % version if version is not None else f"/{default_branch}"
                )
                line = branch_re.sub(replacement, line)
            if ("docs-latest" in line) or ("docs-stable" in line):
                # our doc server
                replacement = (
                    "/v%s" % version if version is not None else f"/{default_branch}"
                )
                line = branch_re.sub(replacement, line)
        if doc_image_re.search(line) is not None:
            replacement = (
                "docs-v%s-" % version if version is not None else "docs-latest-"
            )
            line = doc_image_re.sub(replacement, line)
        new_contents.append(line)

    return "\n".join(new_contents) + "\n"


def _update_pyproject(
    contents: str,
    version: str,
    default_branch: str,
    update_urls: bool,
) -> str:
    """Update contents of pyproject.toml to make it release/latest ready.

    - Sets the project.version field to the given version, if the version is
      not dynamic.
    - Updates the documentation URLs to point specifically to the given version.

    Parameters
    ----------
    contents
        Text of the ``pyproject.toml`` file from a package
    version
        Format of the version string is '#.#.#'
    default_branch
        The name of the default project branch to use
    update_urls
        If set to ``True``, then also updates the relevant URL links
        considering the version number provided at ``version``.


    Returns
    -------
        New version of ``pyproject.toml`` with all replaces done
    """

    variants = {
        "available",
        "latest",
        "main",
        "master",
        "stable",
        default_branch,
        packaging.version.VERSION_PATTERN,
    }

    data = tomlkit.loads(contents)
    project = data.setdefault("project", {})

    if "version" in project.get("dynamic", []):
        logger.info("Not setting project version on pyproject.toml as it is dynamic")

    elif (
        re.match(
            packaging.version.VERSION_PATTERN,
            version,
            re.VERBOSE | re.IGNORECASE,
        )
        is not None
    ):
        logger.info(
            "Updating pyproject.toml version from '%s' to '%s'",
            data.get("project", {}).get("version", "unknown version"),
            version,
        )
        project["version"] = version

    else:
        logger.info(
            f"Not setting project version on pyproject.toml as it is "
            f"not PEP-440 compliant (given value: `{version}')"
        )

    if update_urls:
        # matches all other occurrences we need to handle
        branch_re = re.compile(
            r"/(" + "|".join(variants) + r")", re.VERBOSE | re.IGNORECASE
        )

        # sets the various URLs
        urls = project.setdefault("urls", {})
        docurl = urls.get("documentation")
        if (docurl is not None) and (branch_re.search(docurl) is not None):
            replacement = (
                f"/v{version}" if version is not None else f"/{default_branch}"
            )
            urls["documentation"] = branch_re.sub(replacement, docurl)

    return tomlkit.dumps(data)


def get_latest_tag_name(
    gitpkg: gitlab.v4.objects.projects.Project,
) -> str | None:
    """Find the name of the latest tag for a given package in the format
    '#.#.#'.

    Arguments:

        gitpkg: gitlab package object

    Returns
    -------
        The name of the latest tag in format '#.#.#'. ``None`` if no tags for
        the package were found.
    """

    # get 50 latest tags as a list
    latest_tags = gitpkg.releases.list(all=True)
    if not latest_tags:
        return None
    # create list of tags' names but ignore the first 'v' character in each name
    # also filter out non version tags
    version_pattern_re = re.compile(
        packaging.version.VERSION_PATTERN, re.VERBOSE | re.IGNORECASE
    )
    tag_names = [
        tag.name[1:] for tag in latest_tags if version_pattern_re.match(tag.name)
    ]
    if not tag_names:  # no tags were found.
        return None
    # sort them correctly according to each version number
    tag_names.sort(key=packaging.version.Version)
    # take the last one, as it is the latest tag in the sorted tags
    return tag_names[-1]


def get_next_version(gitpkg: gitlab.v4.objects.projects.Project, bump: str) -> str:
    """Return the next version of this package to be tagged.

    Arguments:

        gitpkg: gitlab package object

        bump: what to bump (can be "major", "minor", or "patch" versions)


    Returns
    -------
        The new version of the package (to be tagged)


    Raises
    ------
        ValueError: if the latest tag retrieve from the package does not
            conform with the subset of PEP440 we use (e.g. "v1.2.3b1").
    """

    # if we bump the version, we need to find the latest released version for
    # this package
    assert bump in ("major", "minor", "patch")

    # find the correct latest tag of this package (without 'v' in front),
    # None if there are no tags yet
    latest_tag_name = get_latest_tag_name(gitpkg)

    if latest_tag_name is None:
        if bump == "major":
            return "v1.0.0"

        if bump == "minor":
            return "v0.1.0"

        # patch
        return "v0.0.1"

    # check that it has expected format #.#.#
    # latest_tag_name = Version(latest_tag_name)
    m = re.match(r"(\d+\.\d+\.\d+)", latest_tag_name)
    if not m:
        raise ValueError(
            "The latest tag name {} in package {} has " "unknown format".format(
                "v" + latest_tag_name,
                gitpkg.attributes["path_with_namespace"],
            )
        )

    # increase the version accordingly
    major, minor, patch = latest_tag_name.split(".")

    if bump == "major":
        return f"v{int(major) + 1}.0.0"

    if bump == "minor":
        return f"v{major}.{int(minor) + 1}.0"

    # it is a patch release, proceed with caution for pre-releases

    # handles possible pre-release (alpha, beta, etc) extensions
    pre_releases = ("a", "b", "c", "rc", "dev")
    matches_pre_release = next((k for k in pre_releases if k in patch), "")
    if len(matches_pre_release) != 0:
        patch = patch.split(matches_pre_release)[0]
        # in these cases, we just need to respect the current patch number for
        # a patch release - this doesn't matter otherwise
        patch_int = int(patch) - 1
    else:
        patch_int = int(patch)

    # increment the last number in 'v#.#.#'
    return f"v{major}.{minor}.{patch_int + 1}"


def update_files_at_default_branch(
    gitpkg: gitlab.v4.objects.projects.Project,
    files_dict: dict[str, str],
    message: str,
    dry_run: bool,
) -> None:
    """Update (via a commit) files of a given gitlab package, directly on the
    default project branch.

    Arguments:

        gitpkg: gitlab package object

        files_dict: Dictionary of file names and their contents (as text)

        message: Commit message

        dry_run: If True, nothing will be committed or pushed to GitLab
    """

    data = {
        "branch": gitpkg.default_branch,
        "commit_message": message,
        "actions": [],
    }  # v4

    # add files to update
    for filename in files_dict.keys():
        update_action = dict(action="update", file_path=filename)
        update_action["content"] = files_dict[filename]
        data["actions"].append(update_action)  # type: ignore

    logger.debug(
        "Committing changes in files (%s) to branch '%s'",
        ", ".join(files_dict.keys()),
        gitpkg.default_branch,
    )
    if not dry_run:
        commit = gitpkg.commits.create(data)
        logger.info(
            "Created commit %s at %s (branch=%s)",
            commit.short_id,
            gitpkg.attributes["path_with_namespace"],
            gitpkg.default_branch,
        )


def _get_last_pipeline(
    gitpkg: gitlab.v4.objects.projects.Project,
) -> gitlab.v4.objects.pipelines.ProjectPipeline:
    """Return the last pipeline of the project.

    Arguments:

        gitpkg: gitlab package object

    Returns
    -------
        The gitlab object of the pipeline
    """

    # wait for 10 seconds to ensure that if a pipeline was just submitted,
    # we can retrieve it
    time.sleep(10)

    # get the last pipeline
    return gitpkg.pipelines.list(per_page=1, page=1)[0]


def wait_for_pipeline_to_finish(
    gitpkg: gitlab.v4.objects.projects.Project,
    pipeline_id: int | None,
) -> None:
    """Wait for the latest pipeline to finish building via ``sleep()``.

    This function pauses the script until pipeline completes either
    successfully or with error.

    Arguments:

        gitpkg: gitlab package object
        pipeline_id: id of the pipeline for which we are waiting to finish
        dry_run: If True, outputs log message and exit. There wil be no
                 waiting.
    """

    sleep_step = 30
    max_sleep = 120 * 60  # two hours

    logger.warning(
        f"Waiting for the pipeline {pipeline_id} of "
        f"`{gitpkg.attributes['path_with_namespace']}' to finish",
    )
    logger.warning("Do **NOT** interrupt!")

    if pipeline_id is None:
        return

    # retrieve the pipeline we are waiting for
    pipeline = gitpkg.pipelines.get(pipeline_id)

    # probe and wait for the pipeline to finish
    slept_so_far = 0

    while pipeline.status == "running" or pipeline.status == "pending":
        time.sleep(sleep_step)
        slept_so_far += sleep_step
        if slept_so_far > max_sleep:
            raise ValueError(
                f"I cannot wait longer than {max_sleep} seconds for "
                f"pipeline {pipeline_id} to finish running!"
            )
        # probe gitlab to update the status of the pipeline
        pipeline = gitpkg.pipelines.get(pipeline_id)

    # finished running, now check if it succeeded
    if pipeline.status != "success":
        raise ValueError(
            "Pipeline {} of project {} exited with "
            'undesired status "{}". Release is not possible.'.format(
                pipeline_id,
                gitpkg.attributes["path_with_namespace"],
                pipeline.status,
            )
        )

    logger.info(
        "Pipeline %s of package %s SUCCEEDED. Continue processing.",
        pipeline_id,
        gitpkg.attributes["path_with_namespace"],
    )


def _cancel_last_pipeline(gitpkg: gitlab.v4.objects.projects.Project) -> None:
    """Cancel the last started pipeline of a package.

    Arguments:

        gitpkg: gitlab package object
    """
    pipeline = _get_last_pipeline(gitpkg)
    logger.info(
        "Cancelling the last pipeline %s of project %s",
        pipeline.id,
        gitpkg.attributes["path_with_namespace"],
    )
    pipeline.cancel()


def _get_differences(orig: str, changed: str, fname: str) -> str:
    """Calculate the unified diff between two files readout as strings.

    Arguments:

        orig: The original file

        changed: The changed file, after manipulations

        fname: The name of the file


    Returns
    -------
        The unified differences between the changes.
    """
    differences = difflib.unified_diff(
        orig.split("\n"),
        changed.split("\n"),
        fromfile=fname,
        tofile=fname + ".new",
        n=0,
        lineterm="",
    )

    return "\n".join(differences)


def release_package(
    gitpkg: gitlab.v4.objects.projects.Project,
    tag_name: str,
    tag_comments: str,
    dry_run: bool = False,
) -> int | None:
    """Release a package.

    The provided tag will be annotated with a given list of comments. Files
    such as ``README.md`` and ``pyproject.toml`` will be updated according to
    the release procedures.

    Parameters
    ----------
    gitpkg
        gitlab package object
    tag_name
        The name of the release tag
    tag_comments_list
        New annotations for this tag in a form of list
    dry_run
        If ``True``, nothing will be committed or pushed to GitLab

    Returns
    -------
        The (integer) pipeline identifier, or None, if a pipeline was not
        actually started (e.g. ``dry_run`` is set to ``True``)
    """

    # 1. Replace branch tag in Readme to new tag, change version file to new
    # version tag. Add and commit to gitlab
    version_number = tag_name[1:]  # remove 'v' in front

    readme_file = gitpkg.files.get(file_path="README.md", ref=gitpkg.default_branch)

    readme_contents_orig = readme_file.decode().decode()
    readme_contents = _update_readme(
        readme_contents_orig, version_number, gitpkg.default_branch
    )
    if dry_run:
        d = _get_differences(readme_contents_orig, readme_contents, "README.md")
        logger.info(f"Changes to release (from latest):\n{d}")

    pyproject_file = gitpkg.files.get(
        file_path="pyproject.toml", ref=gitpkg.default_branch
    )

    pyproject_contents_orig = pyproject_file.decode().decode()
    pyproject_contents = _update_pyproject(
        contents=pyproject_contents_orig,
        version=version_number,
        default_branch=gitpkg.default_branch,
        update_urls=True,
    )
    if dry_run:
        d = _get_differences(
            pyproject_contents_orig, pyproject_contents, "pyproject.toml"
        )
        logger.info(f"Changes to release (from latest):\n{d}")

    # commit and push changes
    update_files_at_default_branch(
        gitpkg,
        {"README.md": readme_contents, "pyproject.toml": pyproject_contents},
        f"Increased stable version to {version_number}",
        dry_run,
    )

    if not dry_run:
        # cancel running the pipeline triggered by the last commit
        _cancel_last_pipeline(gitpkg)

    # 2. Tag package with new tag and push
    logger.info('Tagging "%s"', tag_name)
    logger.debug("Updating tag comments with:\n%s", tag_comments)
    if not dry_run:
        params = {
            "name": tag_name,
            "tag_name": tag_name,
            "ref": gitpkg.default_branch,
        }
        if tag_comments:
            params["description"] = tag_comments
        gitpkg.releases.create(params)

    # get the pipeline that is actually running with no skips
    running_pipeline = _get_last_pipeline(gitpkg)

    # 3. Re-store the original README, bump the pyproject.toml release by a
    # (beta) notch

    # sets the next beta version
    major, minor, patch = version_number.split(".")
    next_version_number = f"{major}.{minor}.{int(patch) + 1}b0"

    pyproject_contents_latest = _update_pyproject(
        contents=pyproject_contents_orig,
        version=next_version_number,
        default_branch=gitpkg.default_branch,
        update_urls=False,
    )
    # commit and push changes
    update_files_at_default_branch(
        gitpkg,
        {
            "README.md": readme_contents_orig,
            "pyproject.toml": pyproject_contents_latest,
        },
        f"Increased latest version to {next_version_number} [skip ci]",
        dry_run,
    )
    if dry_run:
        d = _get_differences(
            pyproject_contents, pyproject_contents_latest, "pyproject.toml"
        )
        logger.info(f"Changes from release (to latest):\n{d}")

    return running_pipeline.id
