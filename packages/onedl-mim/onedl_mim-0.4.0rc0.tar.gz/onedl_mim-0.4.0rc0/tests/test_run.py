# Copyright (c) OpenMMLab. All rights reserved.
import pytest
import torch
from click.testing import CliRunner

from mim.commands.install import cli as install
from mim.commands.run import cli as run
from mim.commands.uninstall import cli as uninstall


def setup_module():
    runner = CliRunner()
    result = runner.invoke(uninstall, ['onedl-mmcv', '--yes'])
    assert result.exit_code == 0, result.output
    result = runner.invoke(uninstall, ['onedl-mmpretrain', '--yes'])
    assert result.exit_code == 0, result.output


@pytest.mark.parametrize('device,gpus', [
    ('cpu', 0),
    pytest.param(
        'cuda',
        1,
        marks=pytest.mark.skipif(
            not torch.cuda.is_available(), reason='requires CUDA support')),
])
def test_run(device, gpus, tmp_path):
    runner = CliRunner()
    result = runner.invoke(install, ['onedl-mmpretrain>=1.0.0rc0', '--yes'])
    assert result.exit_code == 0, result.output
    result = runner.invoke(install, ['onedl-mmengine', '--yes'])
    assert result.exit_code == 0, result.output
    result = runner.invoke(install, ['onedl-mmcv>=2.0.0rc0', '--yes'])
    assert result.exit_code == 0, result.output

    result = runner.invoke(run, [
        'onedl-mmpretrain', 'train', 'tests/data/lenet5_mnist_2.0.py',
        f'--work-dir={tmp_path}'
    ])
    assert result.exit_code == 0, result.output
    result = runner.invoke(run, [
        'onedl-mmpretrain', 'test', 'tests/data/lenet5_mnist_2.0.py',
        'tests/data/epoch_1.pth'
    ])
    assert result.exit_code == 0, result.output
    result = runner.invoke(run, [
        'onedl-mmpretrain', 'xxx', 'tests/data/lenet5_mnist_2.0.py',
        'tests/data/epoch_1.pth'
    ])
    assert result.exit_code != 0


def teardown_module():
    runner = CliRunner()
    result = runner.invoke(uninstall, ['onedl-mmcv', '--yes'])
    assert result.exit_code == 0, result.output
    result = runner.invoke(uninstall, ['onedl-mmpretrain', '--yes'])
    assert result.exit_code == 0, result.output
