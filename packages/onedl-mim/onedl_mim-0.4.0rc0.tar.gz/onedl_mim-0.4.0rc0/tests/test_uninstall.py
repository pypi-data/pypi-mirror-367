# Copyright (c) OpenMMLab. All rights reserved.
from click.testing import CliRunner

from mim.commands.install import cli as install
from mim.commands.list import list_package
from mim.commands.uninstall import cli as uninstall


def setup_module():
    runner = CliRunner()
    result = runner.invoke(uninstall, ['onedl-mmcv', '--yes'])
    assert result.exit_code == 0, result.output
    result = runner.invoke(uninstall, ['onedl-mmpretrain', '--yes'])
    assert result.exit_code == 0, result.output
    result = runner.invoke(uninstall, ['onedl-mmsegmentation', '--yes'])
    assert result.exit_code == 0, result.output


def test_uninstall():
    runner = CliRunner()

    # mim install onedl-mmsegmentation --yes
    result = runner.invoke(install, ['onedl-mmsegmentation', '--yes'])
    assert result.exit_code == 0, result.output

    # check if install success
    result = list_package()
    installed_packages = [item[0] for item in result]
    assert 'onedl-mmsegmentation' in installed_packages
    assert 'onedl-mmcv' in installed_packages

    # mim uninstall onedl-mmsegmentation --yes
    result = runner.invoke(uninstall, ['onedl-mmsegmentation', '--yes'])
    assert result.exit_code == 0, result.output

    # check if uninstall success
    result = list_package()
    installed_packages = [item[0] for item in result]
    assert 'onedl-mmsegmentation' not in installed_packages

    # mim uninstall onedl-mmpretrain onedl-mmcv --yes
    result = runner.invoke(uninstall,
                           ['onedl-mmpretrain', 'onedl-mmcv', '--yes'])
    assert result.exit_code == 0, result.output

    # check if uninstall success
    result = list_package()
    installed_packages = [item[0] for item in result]
    assert 'onedl-mmpretrain' not in installed_packages
    assert 'onedl-mmcv' not in installed_packages


def teardown_module():
    runner = CliRunner()
    result = runner.invoke(uninstall, ['onedl-mmcv', '--yes'])
    assert result.exit_code == 0, result.output
    result = runner.invoke(uninstall, ['onedl-mmpretrain', '--yes'])
    assert result.exit_code == 0, result.output
    result = runner.invoke(uninstall, ['onedl-mmsegmentation', '--yes'])
    assert result.exit_code == 0, result.output
