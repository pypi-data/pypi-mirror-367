# Copyright (c) OpenMMLab. All rights reserved.
import os
import os.path as osp
import subprocess
import tempfile

import pytest
from click.testing import CliRunner

from mim.commands.install import cli as install
from mim.commands.install import extract_package_name, modify_install_args
from mim.commands.uninstall import cli as uninstall


def test_third_party():
    runner = CliRunner()
    # mim install fire
    result = runner.invoke(install, ['fire'])
    assert result.exit_code == 0, result.output

    # mim uninstall fire --yes
    result = runner.invoke(uninstall, ['fire', '--yes'])
    assert result.exit_code == 0, result.output


def test_mmcv_install():
    runner = CliRunner()
    # mim install onedl-mmcv --yes
    # install latest version
    result = runner.invoke(install, ['onedl-mmcv', '--yes'])
    assert result.exit_code == 0, result.output

    # mim install onedl-mmcv==2.3.0 --yes
    result = runner.invoke(install, ['onedl-mmcv==2.3.0rc0', '--yes'])
    assert result.exit_code == 0, result.output

    # mim uninstall onedl-mmcv --yes
    result = runner.invoke(uninstall, ['onedl-mmcv', '--yes'])
    assert result.exit_code == 0, result.output

    # version should be less than latest version
    # mim install onedl-mmcv==100.0.0 --yes
    result = runner.invoke(install, ['onedl-mmcv==100.0.0', '--yes'])
    assert result.exit_code == 1


def test_mmrepo_install():
    runner = CliRunner()

    # install local repo
    with tempfile.TemporaryDirectory() as temp_root:
        repo_root = osp.join(temp_root, 'mmclassification')
        subprocess.check_call([
            'git', 'clone',
            'https://github.com/vbti-development/onedl-mmpretrain.git',
            repo_root
        ])

        # mim install .
        current_root = os.getcwd()
        os.chdir(repo_root)
        result = runner.invoke(install, ['.', '--yes'])
        assert result.exit_code == 0, result.output

        os.chdir('..')

        # mim install ./mmclassification
        result = runner.invoke(install, ['./mmclassification', '--yes'])
        assert result.exit_code == 0, result.output

        # mim install -e ./mmclassification
        result = runner.invoke(install, ['-e', './mmclassification', '--yes'])
        assert result.exit_code == 0, result.output

        os.chdir(current_root)

    # mim install git+https://github.com/vbti-development/onedl-mmpretrain.git
    result = runner.invoke(
        install,
        ['git+https://github.com/vbti-development/onedl-mmpretrain.git'])
    assert result.exit_code == 0, result.output

    # mim install onedl-mmpretrain --yes
    result = runner.invoke(install, ['onedl-mmpretrain', '--yes'])
    assert result.exit_code == 0, result.output

    # mim install onedl-mmpretrain==1.3.0rc0 --yes
    result = runner.invoke(install, ['onedl-mmpretrain==1.3.0rc0', '--yes'])
    assert result.exit_code == 0, result.output

    result = runner.invoke(uninstall, ['onedl-mmcv', '--yes'])
    assert result.exit_code == 0, result.output

    result = runner.invoke(uninstall, ['onedl-mmpretrain', '--yes'])
    assert result.exit_code == 0, result.output


@pytest.mark.parametrize(
    'package_spec,expected_name,expected_extras,expected_version',
    [
        # Test simple package name
        ('onedl-mmpretrain', 'onedl-mmpretrain', None, ''),
        # Test package with extras
        ('onedl-mmpretrain[mminstall]', 'onedl-mmpretrain', 'mminstall', ''),
        # Test package with multiple extras
        ('onedl-mmpretrain[mminstall,dev]', 'onedl-mmpretrain',
         'mminstall,dev', ''),
        # Test package with version specifier
        ('onedl-mmpretrain>=1.0.0', 'onedl-mmpretrain', None, '>=1.0.0'),
        # Test package with extras and version specifier
        ('onedl-mmpretrain[mminstall]>=1.0.0', 'onedl-mmpretrain', 'mminstall',
         '>=1.0.0'),
        # Test package with complex version specifier
        ('onedl-mmpretrain>=1.0.0,<2.0.0', 'onedl-mmpretrain', None,
         '>=1.0.0,<2.0.0'),
        # Test package with extras and complex version specifier
        ('onedl-mmpretrain[mminstall,dev]>=1.0.0,<2.0.0', 'onedl-mmpretrain',
         'mminstall,dev', '>=1.0.0,<2.0.0'),
        # Test package with release candidate version
        ('onedl-mmpretrain==1.3.0rc0', 'onedl-mmpretrain', None, '==1.3.0rc0'),
        # Test package with extras and release candidate version
        ('onedl-mmpretrain[mminstall]==1.3.0rc0', 'onedl-mmpretrain',
         'mminstall', '==1.3.0rc0'),
        # Test package with underscores and numbers
        ('package_name123', 'package_name123', None, ''),
        # Test package with hyphens
        ('my-package-name', 'my-package-name', None, ''),
        # Test package with dots
        ('package.name', 'package.name', None, ''),
        # Test package with mixed characters
        ('my_package-name123', 'my_package-name123', None, ''),
    ])
def test_extract_package_name(package_spec, expected_name, expected_extras,
                              expected_version):
    """Test the extract_package_name function with various package
    specifications."""
    package_name, extras, version_spec = extract_package_name(package_spec)
    assert package_name == expected_name
    assert extras == expected_extras
    assert version_spec == expected_version


@pytest.mark.parametrize(
    'invalid_spec',
    [
        '',  # Empty string
        '[mminstall]',  # Missing package name
        '>=1.0.0',  # Missing package name
        '[]',  # Empty brackets
        '[',  # Unclosed bracket
        ']',  # Only closing bracket
    ])
def test_extract_package_name_invalid(invalid_spec):
    """Test the extract_package_name function with invalid package
    specifications."""
    package_name, extras, version_spec = extract_package_name(invalid_spec)
    assert package_name == invalid_spec
    assert extras is None
    assert version_spec == ''


@pytest.mark.parametrize(
    'input_args,expected_output',
    [
        # Test simple OpenMMLab package
        (['onedl-mmpretrain'], ['onedl-mmpretrain[mminstall]']),
        # Test OpenMMLab package with version specifier
        (['onedl-mmpretrain>=1.0.0'], ['onedl-mmpretrain[mminstall]>=1.0.0']),
        # Test OpenMMLab package with existing extras
        (['onedl-mmpretrain[dev]'], ['onedl-mmpretrain[dev,mminstall]']),
        # Test OpenMMLab package with existing extras and version
        (['onedl-mmpretrain[dev]>=1.0.0'
          ], ['onedl-mmpretrain[dev,mminstall]>=1.0.0']),
        # Test OpenMMLab package that already has mminstall extra
        (['onedl-mmpretrain[mminstall]'], ['onedl-mmpretrain[mminstall]']),
        # Test OpenMMLab package with mminstall and other extras
        (['onedl-mmpretrain[dev,mminstall,test]'
          ], ['onedl-mmpretrain[dev,mminstall,test]']),
        # Test non-OpenMMLab package
        (['numpy'], ['numpy']),
        # Test onedl-mmcv (should be excluded)
        (['onedl-mmcv'], ['onedl-mmcv']),
        # Test multiple packages
        (['onedl-mmpretrain', 'numpy', 'onedl-mmdet'],
         ['onedl-mmpretrain[mminstall]', 'numpy', 'onedl-mmdet[mminstall]']),
        # Test with pip options/flags
        (['-r', 'requirements.txt', 'onedl-mmpretrain', '--upgrade'], [
            '-r', 'requirements.txt', 'onedl-mmpretrain[mminstall]',
            '--upgrade'
        ]),
        # Test with complex version specifiers
        (['onedl-mmpretrain>=1.0.0,<2.0.0'
          ], ['onedl-mmpretrain[mminstall]>=1.0.0,<2.0.0']),
        # Test with release candidate version
        (['onedl-mmpretrain==1.3.0rc0'
          ], ['onedl-mmpretrain[mminstall]==1.3.0rc0']),
        # Test empty list
        ([], []),
        # Test only flags
        (['--upgrade', '-v'], ['--upgrade', '-v']),
        # Test mixed OpenMMLab and non-OpenMMLab packages with flags
        (['-v', 'onedl-mmpretrain', 'torch', '--upgrade', 'onedl-mmdet[dev]'
          ], [
              '-v', 'onedl-mmpretrain[mminstall]', 'torch', '--upgrade',
              'onedl-mmdet[dev,mminstall]'
          ]),
        # Test package with multiple existing extras including mminstall
        (['onedl-mmpretrain[dev,mminstall]'
          ], ['onedl-mmpretrain[dev,mminstall]']),
        # Test different OpenMMLab packages
        (['onedl-mmdet'], ['onedl-mmdet[mminstall]']),
        (['onedl-mmsegmentation'], ['onedl-mmsegmentation[mminstall]']),
        # Test packages with exact version
        (['onedl-mmpretrain==1.2.3'], ['onedl-mmpretrain[mminstall]==1.2.3']),
        # Test packages with inequality operators
        (['onedl-mmpretrain<2.0'], ['onedl-mmpretrain[mminstall]<2.0']),
        (['onedl-mmpretrain!=1.0'], ['onedl-mmpretrain[mminstall]!=1.0']),
    ],
    ids=lambda input_args: str(input_args))
def test_modify_install_args(input_args, expected_output):
    """Test the modify_install_args function with various install arguments."""
    result = modify_install_args(input_args)
    assert result == expected_output
