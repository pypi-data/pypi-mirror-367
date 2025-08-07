# Copyright (c) OpenMMLab. All rights reserved.
import pytest
import torch
from click.testing import CliRunner

from mim.commands.install import cli as install
from mim.commands.test import cli as test
from mim.commands.uninstall import cli as uninstall


def setup_module():
    runner = CliRunner()
    result = runner.invoke(uninstall, ['onedl-mmcv', '--yes'])
    assert result.exit_code == 0, result.output
    result = runner.invoke(uninstall, ['onedl-mmpretrain', '--yes'])
    assert result.exit_code == 0, result.output


@pytest.mark.parametrize('device', [
    'cpu',
    pytest.param(
        'cuda',
        marks=pytest.mark.skipif(
            not torch.cuda.is_available(), reason='requires CUDA support')),
])
def test_test(device):
    runner = CliRunner()
    result = runner.invoke(install, ['onedl-mmpretrain>=1.0.0rc0', '--yes'])
    assert result.exit_code == 0, result.output
    result = runner.invoke(install, ['onedl-mmengine', '--yes'])
    assert result.exit_code == 0, result.output
    result = runner.invoke(install, ['onedl-mmcv>=2.0.0rc0', '--yes'])
    assert result.exit_code == 0, result.output

    result = runner.invoke(test, [
        'onedl-mmpretrain', 'tests/data/lenet5_mnist_2.0.py', '--checkpoint',
        'tests/data/epoch_1.pth'
    ])
    assert result.exit_code == 0, result.output
    result = runner.invoke(test, [
        'onedl-mmpretrain', 'tests/data/xxx.py', '--checkpoint',
        'tests/data/epoch_1.pth'
    ])
    assert result.exit_code != 0
    result = runner.invoke(test, [
        'onedl-mmpretrain', 'tests/data/lenet5_mnist_2.0.py', '--checkpoint',
        'tests/data/xxx.pth'
    ])
    assert result.exit_code != 0


def teardown_module():
    runner = CliRunner()
    result = runner.invoke(uninstall, ['onedl-mmcv', '--yes'])
    assert result.exit_code == 0, result.output
    result = runner.invoke(uninstall, ['onedl-mmpretrain', '--yes'])
    assert result.exit_code == 0, result.output
