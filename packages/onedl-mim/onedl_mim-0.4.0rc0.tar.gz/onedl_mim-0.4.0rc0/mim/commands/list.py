# Copyright (c) OpenMMLab. All rights reserved.
import importlib.metadata as importlib_metadata
import os.path as osp
from typing import List, Tuple

import click
from tabulate import tabulate

from mim.utils.utils import get_installed_path


@click.command('list')
@click.option(
    '--all',
    is_flag=True,
    help='List packages of OpenMMLab projects or all the packages in the '
    'python environment.')
def cli(all: bool = True) -> None:
    """List packages.

    \b
    Example:
        > mim list
        > mim list --all
    """
    table_header = ['Package', 'Version', 'Source']
    table_data = list_package(all=all)
    click.echo(tabulate(table_data, headers=table_header, tablefmt='simple'))


def list_package(all: bool = False) -> List[Tuple[str, ...]]:
    """List packages.

    List packages of OpenMMLab projects or all the packages in the python
    environment.

    Args:
        all (bool): List all installed packages. If all is False, it just lists
            the packages installed by mim. Default: False.
    """
    pkgs_info: List[Tuple[str, ...]] = []

    # Get all installed distributions using importlib.metadata
    distributions = importlib_metadata.distributions()

    for dist in distributions:
        pkg_name = dist.metadata['Name']
        pkg_version = dist.version

        if all:
            pkgs_info.append((pkg_name, pkg_version))
        else:
            if pkg_name.startswith(
                    'onedl-mmcv') or pkg_name == 'onedl-mmengine':
                is_openmmlab_package = True
            else:
                is_openmmlab_package = False
                try:
                    package_path = get_installed_path(pkg_name)
                    possible_metadata_paths = [
                        osp.join(package_path, '.mim', 'model-index.yml'),
                        osp.join(package_path, 'model-index.yml'),
                        osp.join(package_path, '.mim', 'model_zoo.yml'),
                        osp.join(package_path, 'model_zoo.yml')
                    ]
                    for path in possible_metadata_paths:
                        if osp.exists(path):
                            is_openmmlab_package = True
                            break
                except ValueError:
                    is_openmmlab_package = False

            if is_openmmlab_package:
                # Get home page from metadata
                pkgs_info.append((pkg_name, pkg_version))

    pkgs_info.sort(key=lambda pkg_info: pkg_info[0])
    return pkgs_info
