# Copyright (c) OpenMMLab. All rights reserved.

from click.testing import CliRunner

from mim.commands.install import cli as install
from mim.commands.search import cli as search
from mim.commands.uninstall import cli as uninstall


def setup_module():
    runner = CliRunner()
    result = runner.invoke(uninstall, ['onedl-mmcv', '--yes'])
    assert result.exit_code == 0, result.output
    result = runner.invoke(uninstall, ['onedl-mmpretrain', '--yes'])
    assert result.exit_code == 0, result.output


def test_search():
    runner = CliRunner()
    result = runner.invoke(install, ['onedl-mmpretrain', '--yes'])
    assert result.exit_code == 0, result.output

    # mim search onedl-mmpretrain
    result = runner.invoke(search, ['onedl-mmpretrain'])
    assert result.exit_code == 0, result.output

    # mim search onedl-mmpretrain --remote
    # search master branch
    result = runner.invoke(search, ['onedl-mmpretrain', '--remote'])
    assert result.exit_code == 0, result.output
    # mim search mmsegmentation --remote
    result = runner.invoke(search, ['onedl-mmsegmentation', '--remote'])
    assert result.exit_code == 0, result.output
    # mim search mmaction2 --remote
    result = runner.invoke(search, ['mmaction2', '--remote'])
    assert result.exit_code == 0, result.output

    # mim search onedl-mmpretrain==0.24.0 --remote
    result = runner.invoke(search, ['onedl-mmpretrain==1.3.0rc0', '--remote'])
    assert result.exit_code == 0, result.output

    # always test latest onedl-mmpretrain
    result = runner.invoke(uninstall, ['onedl-mmpretrain', '--yes'])
    assert result.exit_code == 0, result.output

    result = runner.invoke(install, ['onedl-mmpretrain', '--yes'])
    assert result.exit_code == 0, result.output

    # mim search onedl-mmpretrain --model res
    # invalid model
    result = runner.invoke(search, ['onedl-mmpretrain', '--model', 'res'])
    assert result.exit_code == 1
    # mim search onedl-mmpretrain --model resnet
    result = runner.invoke(search, ['onedl-mmpretrain', '--model', 'resnet'])
    assert result.exit_code == 0, result.output

    # mim search onedl-mmpretrain --valid-config
    result = runner.invoke(search, ['onedl-mmpretrain', '--valid-config'])
    assert result.exit_code == 0, result.output

    # mim search onedl-mmpretrain --config resnet18_b16x8_cifar1
    # invalid config
    result = runner.invoke(
        search, ['onedl-mmpretrain', '--config', 'resnet18_b16x8_cifar1'])
    assert result.exit_code == 1
    # mim search onedl-mmpretrain --config resnet18_b16x8_cifar10
    result = runner.invoke(
        search, ['onedl-mmpretrain', '--config', 'resnet18_8xb16_cifar10'])
    assert result.exit_code == 0, result.output

    # mim search onedl-mmpretrain --dataset cifar-1
    # invalid dataset
    result = runner.invoke(search,
                           ['onedl-mmpretrain', '--dataset', 'cifar-1'])
    assert result.exit_code == 1

    # mim search onedl-mmpretrain --dataset cifar-10
    result = runner.invoke(search,
                           ['onedl-mmpretrain', '--dataset', 'cifar-10'])
    assert result.exit_code == 0, result.output

    # mim search onedl-mmpretrain --condition 'batch_size>45,epochs>100'
    result = runner.invoke(
        search,
        ['onedl-mmpretrain', '--condition', 'batch_size>45,epochs>100'])
    assert result.exit_code == 0, result.output

    # mim search onedl-mmpretrain --condition 'batch_size>45 epochs>100'
    result = runner.invoke(
        search,
        ['onedl-mmpretrain', '--condition', 'batch_size>45 epochs>100'])
    assert result.exit_code == 0, result.output

    # mim search onedl-mmpretrain --condition '128<batch_size<=256'
    result = runner.invoke(
        search, ['onedl-mmpretrain', '--condition', '128<batch_size<=256'])
    assert result.exit_code == 0, result.output

    # mim search onedl-mmpretrain --sort epoch
    result = runner.invoke(search, ['onedl-mmpretrain', '--sort', 'epoch'])
    assert result.exit_code == 0, result.output
    # mim search onedl-mmpretrain --sort epochs
    result = runner.invoke(search, ['onedl-mmpretrain', '--sort', 'epochs'])
    assert result.exit_code == 0, result.output

    # mim search onedl-mmpretrain --sort batch_size epochs
    result = runner.invoke(
        search, ['onedl-mmpretrain', '--sort', 'batch_size', 'epochs'])
    assert result.exit_code == 0, result.output

    # mim search onedl-mmpretrain --field epoch
    result = runner.invoke(search, ['onedl-mmpretrain', '--field', 'epoch'])
    assert result.exit_code == 0, result.output
    # mim search onedl-mmpretrain --field epochs
    result = runner.invoke(search, ['onedl-mmpretrain', '--field', 'epochs'])
    assert result.exit_code == 0, result.output


def teardown_module():
    runner = CliRunner()
    result = runner.invoke(uninstall, ['onedl-mmcv', '--yes'])
    assert result.exit_code == 0, result.output
    result = runner.invoke(uninstall, ['onedl-mmpretrain', '--yes'])
    assert result.exit_code == 0, result.output
