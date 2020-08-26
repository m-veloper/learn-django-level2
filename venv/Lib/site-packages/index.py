# -*- coding: utf-8 -*-

import os
import sys
from pkg_resources import require

import click
import yaml
import catkin_pkg.packages

from pandoradep import utils
from pandoradep.config import COLORS


@click.group(invoke_without_command=True)
@click.option('--version', is_flag=True, help='Return the current version.')
def cli(version):
    """ A tiny cli tool to manage PANDORA's dependencies. """

    if version:
        click.echo(require('pandoradep')[0].version)


@cli.command()
@click.argument('root_of_pkgs', type=click.Path(exists=True, readable=True))
def create(root_of_pkgs):
    """ Create a repos.yml file, mapping each package to
        the corresponding repo. [used by CI]
    """

    package_dirs = {}

    for root, dirs, files in os.walk(root_of_pkgs):
        if '.git' in dirs:
            package_dirs[root] = []

    for repo in package_dirs:
        for root, dirs, files in os.walk(repo):
            if 'package.xml' in files:
                package_dirs[repo].append(os.path.basename(root))

    for repo in package_dirs:
        package_dirs[os.path.basename(repo)] = package_dirs.pop(repo)

    click.echo(package_dirs)

    with open('repos.yml', 'w') as file_handler:
        file_handler.write(yaml.dump(package_dirs))


@cli.command()
@click.argument('root', type=click.Path(exists=True, readable=True))
@click.argument('repo_name', type=click.STRING)
@click.argument('repos_file', type=click.STRING)
@click.option('--env', type=click.STRING, default='JENKINS_SCRIPTS',
              help="""Specify environmental variable for
                      the scripts. The default is JENKINS_SCRIPTS.
                   """)
def update(root, repo_name, repos_file, env):
    """ Update dependencies [used by CI] """

    repos_file = os.path.abspath(repos_file)

    try:
        with open(repos_file, 'r') as file_handler:
            repos = yaml.safe_load(file_handler)
    except IOError as err:
        click.echo(click.style(str(err), fg=COLORS['error']))
        sys.exit(1)

    catkin_output = catkin_pkg.packages.find_packages(root)
    local_pkgs = [pkg.name for pkg in catkin_output.values()]

    try:
        repo_dependencies = set(repos[repo_name])
    except KeyError as err:
        click.echo(click.style(str(err) + ' not found in ' + repos_file,
                               fg=COLORS['error']))
        click.echo(click.style(str(repos.keys()), fg=COLORS['debug']))
        sys.exit(1)

    if repo_dependencies == set(local_pkgs):
        click.echo(click.style('Nothing changed', fg=COLORS['success']))
    else:
        click.echo(click.style('Updating packages...', fg=COLORS['info']))
        repos[repo_name] = local_pkgs
        utils.update_upstream(repos_file, repos, env)


@cli.command()
@click.argument('directory', type=click.Path(exists=True, readable=True))
@click.option('--http', is_flag=True,
              help='Return rosinstall entries with https.')
@click.option('--exclude', '-x', multiple=True, default=None,
              type=click.Path(exists=True, readable=True),
              help='Exclude a directory from the scan.')
@click.option('--force', is_flag=True, help='Use it to suppress warnings.')
def scan(directory, http, exclude, force):
    """ Scans the directory tree for dependencies. By default returns
        rosinstall entries that you can feed into the wstool.
    """

    depends = utils.get_dependencies(directory, exclude, force)
    utils.print_repos(depends, http)


@cli.command()
@click.argument('directory', default='.', type=click.Path(exists=True,
                readable=True))
@click.option('--http', is_flag=True, help='Clone the repos with http.')
def fetch(directory, http):
    """ Fetch PANDORA's dependencies. """

    dependencies = utils.get_dependencies(directory)
    repos = [dep['repo'] for dep in dependencies]
    utils.download(repos, http)


@cli.command()
@click.argument('repo')
@click.option('--without-deps', is_flag=True,
              help="Don't fetch the dependencies.")
@click.option('--http', is_flag=True, help='Clone the repo using http.')
@click.pass_context
def get(ctx, repo, without_deps, http):
    """ Download a PANDORA repo with its dependencies. """

    repo_list = utils.fetch_upstream()
    if not utils.pandora_lookup(repo, repo_list):
        click.echo(click.style('✘ ' + str(repo) + ' is not a PANODRA repo.',
                               fg=COLORS['error']))
        sys.exit(1)

    utils.download_package(repo, http)
    if not without_deps:
        ctx.invoke(fetch, directory=repo, http=http)
