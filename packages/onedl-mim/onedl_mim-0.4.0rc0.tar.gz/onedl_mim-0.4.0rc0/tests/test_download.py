# Copyright (c) OpenMMLab. All rights reserved.
import pytest
from click.testing import CliRunner

from mim.commands.download import download
from mim.commands.install import cli as install
from mim.commands.uninstall import cli as uninstall


def setup_module():
    runner = CliRunner()
    result = runner.invoke(uninstall, ['onedl-mmcv', '--yes'])
    assert result.exit_code == 0, result.output
    result = runner.invoke(uninstall, ['onedl-mmengine', '--yes'])
    assert result.exit_code == 0, result.output
    result = runner.invoke(uninstall, ['onedl-mmpretrain', '--yes'])
    assert result.exit_code == 0, result.output


def test_download(tmp_path):
    runner = CliRunner()
    result = runner.invoke(install, ['onedl-mmcv', '--yes'])
    assert result.exit_code == 0, result.output
    result = runner.invoke(install, ['onedl-mmengine', '--yes'])
    assert result.exit_code == 0, result.output

    with pytest.raises(ValueError):
        # version is not allowed
        download('onedl-mmpretrain==0.11.0', ['resnet18_8xb16_cifar10'])

    with pytest.raises(RuntimeError):
        # onedl-mmpretrain is not installed
        download('onedl-mmpretrain', ['resnet18_8xb16_cifar10'])

    with pytest.raises(ValueError):
        # invalid config
        download('onedl-mmpretrain==0.11.0', ['resnet18_b16x8_cifar1'])

    runner = CliRunner()
    # mim install onedl-mmpretrain --yes
    result = runner.invoke(install, [
        'onedl-mmpretrain', '--yes', '-f',
        'https://github.com/vbti-development/onedl-mmpretrain.git'
    ])
    assert result.exit_code == 0, result.output

    # mim download onedl-mmpretrain --config resnet18_8xb16_cifar10
    checkpoints = download('onedl-mmpretrain', ['resnet18_8xb16_cifar10'])
    assert checkpoints == ['resnet18_b16x8_cifar10_20210528-bd6371c8.pth']
    checkpoints = download('onedl-mmpretrain', ['resnet18_8xb16_cifar10'])

    # mim download onedl-mmpretrain --config resnet18_8xb16_cifar10
    #  --dest tmp_path
    checkpoints = download('onedl-mmpretrain', ['resnet18_8xb16_cifar10'],
                           tmp_path)
    assert checkpoints == ['resnet18_b16x8_cifar10_20210528-bd6371c8.pth']


def teardown_module():
    runner = CliRunner()
    result = runner.invoke(uninstall, ['onedl-mmcv', '--yes'])
    assert result.exit_code == 0, result.output
    result = runner.invoke(uninstall, ['onedl-mmengine', '--yes'])
    assert result.exit_code == 0, result.output
    result = runner.invoke(uninstall, ['onedl-mmpretrain', '--yes'])
    assert result.exit_code == 0, result.output
