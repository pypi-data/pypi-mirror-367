# Copyright (c) OpenMMLab. All rights reserved.
import pytest
import torch
from click.testing import CliRunner

from mim.commands.install import cli as install
from mim.commands.train import cli as train
from mim.commands.uninstall import cli as uninstall


def setup_module():
    runner = CliRunner()
    result = runner.invoke(uninstall, ['onedl-mmcv', '--yes'])
    assert result.exit_code == 0, result.output
    result = runner.invoke(uninstall, ['onedl-mmpretrain', '--yes'])
    assert result.exit_code == 0, result.output


@pytest.mark.parametrize('gpus', [
    0,
    pytest.param(
        1,
        marks=pytest.mark.skipif(
            not torch.cuda.is_available(), reason='requires CUDA support')),
])
def test_train(gpus, tmp_path):
    runner = CliRunner()
    result = runner.invoke(install, ['onedl-mmpretrain>=1.0.0rc0', '--yes'])
    assert result.exit_code == 0, result.output
    result = runner.invoke(install, ['onedl-mmengine', '--yes'])
    assert result.exit_code == 0, result.output
    result = runner.invoke(install, ['onedl-mmcv>=2.0.0rc0', '--yes'])
    assert result.exit_code == 0, result.output

    result = runner.invoke(train, [
        'onedl-mmpretrain', 'tests/data/lenet5_mnist_2.0.py', f'--gpus={gpus}',
        f'--work-dir={tmp_path}'
    ])
    assert result.exit_code == 0, result.output

    result = runner.invoke(train, [
        'onedl-mmpretrain', 'tests/data/xxx.py', f'--gpus={gpus}',
        f'--work-dir={tmp_path}'
    ])
    assert result.exit_code != 0


def teardown_module():
    runner = CliRunner()
    result = runner.invoke(uninstall, ['onedl-mmcv', '--yes'])
    assert result.exit_code == 0, result.output
    result = runner.invoke(uninstall, ['onedl-mmpretrain', '--yes'])
    assert result.exit_code == 0, result.output
