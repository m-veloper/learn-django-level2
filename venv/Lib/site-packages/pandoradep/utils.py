# -*- coding: utf-8 -*-

import sys
import os
import subprocess
import warnings
from time import sleep

from subprocess import check_call
from string import Template

import yaml
import requests
import click
import catkin_pkg.packages

from pandoradep.config import (PANDORA_REPO, INSTALL_TEMPLATE_SSH,
                               INSTALL_TEMPLATE_HTTPS, GIT_TEMPLATE_SSH,
                               GIT_TEMPLATE_HTTPS, COLORS, MASTER_BRANCH)


def get_dependencies(directory, excluded=None, force=False):
    """ Fetches all the run and build dependencies """

    depends = []
    dep_pool = []

    pkgs = catkin_pkg.packages.find_packages(directory, excluded)
    repos = fetch_upstream()

    for pkg in pkgs:
        dep_pool = pkgs[pkg].build_depends + pkgs[pkg].exec_depends
        dep_pool += pkgs[pkg].test_depends

        for dep in dep_pool:
            if pandora_lookup(dep.name, repos, with_name=False):

                if dep.version_eq is None:
                    dep.version_eq = MASTER_BRANCH
                current_dep = {'name': dep.name,
                               'version': dep.version_eq,
                               'repo': pandora_lookup(dep.name, repos,
                                                      with_name=True)
                               }
                depends = resolve_conflicts(depends, current_dep, pkg, force)

    return depends


def pandora_lookup(package_name, repo_list, with_name=False):
    """ Checks if a package belongs to PANDORA.

        Arguments:
        package_name -- The package we want to examine.
        repo_list    -- The list with the PANDORA repos.
        with_name    -- If True returns the name of the repo that
                        "package_name" belongs.
        Returns:
        True or a repo name if the package_name is in the list.
        False or None if the package_name ins't in the list.
    """

    for repo in repo_list.keys():
        if package_name in repo_list[repo]:
            if with_name:
                return repo
            else:
                return True
    if with_name:
        return None
    else:
        return False


def resolve_conflicts(old_dep_list, new_dep, package, force=False):
    """ Checks for conflicts between old and new dependencies

        Arguments:
        old_dep_list -- Dictionaries representing PANDORA packages
                        already stored.
        new_dep      -- A package ready to be stored.

        Returns:
        The updated old_dep_list
    """

    to_add = True

    if not old_dep_list:
        old_dep_list.append(new_dep)
        return old_dep_list

    for old_dep in old_dep_list:
        if old_dep['repo'] == new_dep['repo']:
            if old_dep['version'] != new_dep['version']:

                if new_dep['version'] == MASTER_BRANCH:
                    pass
                else:
                    if not force and old_dep['version'] != MASTER_BRANCH:
                        show_warnings(old_dep, new_dep, package)
                        sys.exit(1)
                    old_dep['version'] = new_dep['version']
            to_add = False

    if to_add:
        old_dep_list.append(new_dep)

    return old_dep_list


def show_warnings(old_dep, new_dep, package):
    """ Displays warnings and debug info about conflicts. """

    click.echo("Package conflict in " + package + " from the same repo [" +
               new_dep['repo'] + "].", err=True)
    click.echo('', err=True)
    click.echo(str(old_dep['name']) + '@' + str(old_dep['version']), err=True)
    click.echo(str(new_dep['name']) + '@' + str(new_dep['version']), err=True)
    click.echo('', err=True)
    click.echo('Try again with --force to ignore this warning.', err=True)


def fetch_upstream():
    """ Returns the current pandora dependencies. """

    with warnings.catch_warnings():

        # Ignores InsecurePlatformWarning from urllib3
        warnings.simplefilter('ignore')
        response = requests.get(PANDORA_REPO)

    return yaml.safe_load(response.text)


def print_repos(depends, http):
    """ Prints dependencies using rosinstall templates. """

    if http:
        template = Template(INSTALL_TEMPLATE_HTTPS)
    else:
        template = Template(INSTALL_TEMPLATE_SSH)

    for dep in depends:
        temp = template.substitute(name=dep['repo'], version=dep['version'])
        click.echo(click.style(temp, fg=COLORS['success']))


def update_upstream(output_file, content, env_var):
    """ Updates upstream yaml file. """

    scripts_path = os.getenv(env_var)

    if not scripts_path:
        raise ValueError('$' + env_var + ' is not set properly.')
    try:
        os.chdir(scripts_path)
    except OSError as err:
        click.echo(click.style(str(err), fg=COLORS['error']), err=True)
        click.echo(click.style('Make sure your env is set properly.',
                               fg=COLORS['debug']), err=True)
        sys.exit(1)

    with open(output_file, 'w') as file_handler:
        file_handler.write(yaml.dump(content))

    git_commands = ["git add -u",
                    "git commit -m 'Update repos.yml'",
                    "git push origin master"
                    ]

    for cmd in git_commands:
        click.echo(click.style('+ ' + cmd, fg=COLORS['debug']))
        try:
            check_call(cmd, shell=True)
        except subprocess.CalledProcessError as err:
            click.echo(click.style(str(err), fg=COLORS['error']), err=True)
            sys.exit(1)


def download(repos, http=False):
    """ Dowloads PANDORA's packages and their dependencies. """

    for repo in repos:
        if download_package(repo, http):

            # Check if the repo has dependencies that are not included.
            dependencies = [dep['repo'] for dep in get_dependencies(repo)]
            for item in dependencies:
                if item not in repos:
                    repos.append(item)


def download_package(name, http):
    """ Download a PANDORA's package. """

    if http:
        template = Template(GIT_TEMPLATE_HTTPS)
    else:
        template = Template(GIT_TEMPLATE_SSH)

    git_repo = template.substitute(name=name)
    if os.path.isdir(name):
        click.echo(str(name) + click.style(' ✔', fg=COLORS['success']))
        sleep(0.1)
        return False
    else:
        click.echo(click.style('⬇ ' + str(name), fg=COLORS['info']))
        check_call(['git', 'clone', '-b', MASTER_BRANCH, git_repo])
        return True
