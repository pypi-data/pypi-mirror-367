# MIM: MIM Installs OpenMMLab Packages

MIM provides a unified interface for launching and installing OpenMMLab projects and their extensions, and managing the OpenMMLab model zoo.

## Major Features

- **Package Management**

  You can use MIM to manage OpenMMLab codebases, install or uninstall them conveniently.

- **Model Management**

  You can use MIM to manage OpenMMLab model zoo, e.g., download checkpoints by name, search checkpoints that meet specific criteria.

- **Unified Entrypoint for Scripts**

  You can execute any script provided by all OpenMMLab codebases with unified commands. Train, test and inference become easier than ever. Besides, you can use `gridsearch` command for vanilla hyper-parameter search.

## License

This project is released under the [Apache 2.0 license](LICENSE).

## Changelog

v0.1.1 was released in 13/6/2021.

## Customization

You can use `.mimrc` for customization. Now we support customize default values of each sub-command. Please refer to [customization.md](docs/en/customization.md) for details.

## Build custom projects with MIM

We provide some examples of how to build custom projects based on OpenMMLAB codebases and MIM in [MIM-Example](https://github.com/open-mmlab/mim-example).
Without worrying about copying codes and scripts from existing codebases, users can focus on developing new components and MIM helps integrate and run the new project.

## Installation

Please refer to [installation.md](docs/en/installation.md) for installation.

## Command

<details>
<summary>1. install</summary>

- command

  ```bash
  # install latest version of onedl-mmcv
  > mim install onedl-mmcv  # wheel
  # install 2.3.0
  > mim install onedl-mmcv==2.3.0

  # install latest version of onedl-mmpretrain
  > mim install onedl-mmpretrain
  # install master branch
  > mim install git+https://github.com/vbti-development/onedl-mmpretrain.git
  # install local repo
  > git clone https://github.com/vbti-development/onedl-mmpretrain.git
  > cd mmclassification
  > mim install .

  # install extension based on OpenMMLab
  mim install git+https://github.com/xxx/onedl-mmpretrain-project.git
  ```

- api

  ```python
  from mim import install

  # install mmcv
  install('onedl-mmcv')

  # install onedl-mmpretrain will automatically install mmcv if it is not installed
  install('onedl-mmpretrain')

  # install extension based on OpenMMLab
  install('git+https://github.com/xxx/onedl-mmpretrain-project.git')
  ```

</details>

<details>
<summary>2. uninstall</summary>

- command

  ```bash
  # uninstall mmcv
  > mim uninstall onedl-mmcv

  # uninstall onedl-mmpretrain
  > mim uninstall onedl-mmpretrain
  ```

- api

  ```python
  from mim import uninstall

  # uninstall mmcv
  uninstall('onedl-mmcv')

  # uninstall onedl-mmpretrain
  uninstall('onedl-mmpretrain')
  ```

</details>

<details>
<summary>3. list</summary>

- command

  ```bash
  > mim list
  > mim list --all
  ```

- api

  ```python
  from mim import list_package

  list_package()
  list_package(True)
  ```

</details>

<details>
<summary>4. search</summary>

- command

  ```bash
  > mim search onedl-mmpretrain
  > mim search onedl-mmpretrain==0.23.0 --remote
  > mim search onedl-mmpretrain --config resnet18_8xb16_cifar10
  > mim search onedl-mmpretrain --model resnet
  > mim search onedl-mmpretrain --dataset cifar-10
  > mim search onedl-mmpretrain --valid-field
  > mim search onedl-mmpretrain --condition 'batch_size>45,epochs>100'
  > mim search onedl-mmpretrain --condition 'batch_size>45 epochs>100'
  > mim search onedl-mmpretrain --condition '128<batch_size<=256'
  > mim search onedl-mmpretrain --sort batch_size epochs
  > mim search onedl-mmpretrain --field epochs batch_size weight
  > mim search onedl-mmpretrain --exclude-field weight paper
  ```

- api

  ```python
  from mim import get_model_info

  get_model_info('onedl-mmpretrain')
  get_model_info('onedl-mmpretrain==0.23.0', local=False)
  get_model_info('onedl-mmpretrain', models=['resnet'])
  get_model_info('onedl-mmpretrain', training_datasets=['cifar-10'])
  get_model_info('onedl-mmpretrain', filter_conditions='batch_size>45,epochs>100')
  get_model_info('onedl-mmpretrain', filter_conditions='batch_size>45 epochs>100')
  get_model_info('onedl-mmpretrain', filter_conditions='128<batch_size<=256')
  get_model_info('onedl-mmpretrain', sorted_fields=['batch_size', 'epochs'])
  get_model_info('onedl-mmpretrain', shown_fields=['epochs', 'batch_size', 'weight'])
  ```

</details>

<details>
<summary>5. download</summary>

- command

  ```bash
  > mim download onedl-mmpretrain --config resnet18_8xb16_cifar10
  > mim download onedl-mmpretrain --config resnet18_8xb16_cifar10 --dest .
  ```

- api

  ```python
  from mim import download

  download('onedl-mmpretrain', ['resnet18_8xb16_cifar10'])
  download('onedl-mmpretrain', ['resnet18_8xb16_cifar10'], dest_root='.')
  ```

</details>

<details>
<summary>6. train</summary>

- command

  ```bash
  # Train models on a single server with CPU by setting `gpus` to 0 and
  # 'launcher' to 'none' (if applicable). The training script of the
  # corresponding codebase will fail if it doesn't support CPU training.
  > mim train onedl-mmpretrain resnet101_b16x8_cifar10.py --work-dir tmp --gpus 0
  # Train models on a single server with one GPU
  > mim train onedl-mmpretrain resnet101_b16x8_cifar10.py --work-dir tmp --gpus 1
  # Train models on a single server with 4 GPUs and pytorch distributed
  > mim train onedl-mmpretrain resnet101_b16x8_cifar10.py --work-dir tmp --gpus 4 \
      --launcher pytorch
  # Train models on a slurm HPC with one 8-GPU node
  > mim train onedl-mmpretrain resnet101_b16x8_cifar10.py --launcher slurm --gpus 8 \
      --gpus-per-node 8 --partition partition_name --work-dir tmp
  # Print help messages of sub-command train
  > mim train -h
  # Print help messages of sub-command train and the training script of onedl-mmpretrain
  > mim train onedl-mmpretrain -h
  ```

- api

  ```python
  from mim import train

  train(repo='onedl-mmpretrain', config='resnet18_8xb16_cifar10.py', gpus=0,
        other_args=('--work-dir', 'tmp'))
  train(repo='onedl-mmpretrain', config='resnet18_8xb16_cifar10.py', gpus=1,
        other_args=('--work-dir', 'tmp'))
  train(repo='onedl-mmpretrain', config='resnet18_8xb16_cifar10.py', gpus=4,
        launcher='pytorch', other_args=('--work-dir', 'tmp'))
  train(repo='onedl-mmpretrain', config='resnet18_8xb16_cifar10.py', gpus=8,
        launcher='slurm', gpus_per_node=8, partition='partition_name',
        other_args=('--work-dir', 'tmp'))
  ```

</details>

<details>
<summary>7. test</summary>

- command

  ```bash
  # Test models on a single server with 1 GPU, report accuracy
  > mim test onedl-mmpretrain resnet101_b16x8_cifar10.py --checkpoint \
      tmp/epoch_3.pth --gpus 1 --metrics accuracy
  # Test models on a single server with 1 GPU, save predictions
  > mim test onedl-mmpretrain resnet101_b16x8_cifar10.py --checkpoint \
      tmp/epoch_3.pth --gpus 1 --out tmp.pkl
  # Test models on a single server with 4 GPUs, pytorch distributed,
  # report accuracy
  > mim test onedl-mmpretrain resnet101_b16x8_cifar10.py --checkpoint \
      tmp/epoch_3.pth --gpus 4 --launcher pytorch --metrics accuracy
  # Test models on a slurm HPC with one 8-GPU node, report accuracy
  > mim test onedl-mmpretrain resnet101_b16x8_cifar10.py --checkpoint \
      tmp/epoch_3.pth --gpus 8 --metrics accuracy --partition \
      partition_name --gpus-per-node 8 --launcher slurm
  # Print help messages of sub-command test
  > mim test -h
  # Print help messages of sub-command test and the testing script of onedl-mmpretrain
  > mim test onedl-mmpretrain -h
  ```

- api

  ```python
  from mim import test
  test(repo='onedl-mmpretrain', config='resnet101_b16x8_cifar10.py',
       checkpoint='tmp/epoch_3.pth', gpus=1, other_args=('--metrics', 'accuracy'))
  test(repo='onedl-mmpretrain', config='resnet101_b16x8_cifar10.py',
       checkpoint='tmp/epoch_3.pth', gpus=1, other_args=('--out', 'tmp.pkl'))
  test(repo='onedl-mmpretrain', config='resnet101_b16x8_cifar10.py',
       checkpoint='tmp/epoch_3.pth', gpus=4, launcher='pytorch',
       other_args=('--metrics', 'accuracy'))
  test(repo='onedl-mmpretrain', config='resnet101_b16x8_cifar10.py',
       checkpoint='tmp/epoch_3.pth', gpus=8, partition='partition_name',
       launcher='slurm', gpus_per_node=8, other_args=('--metrics', 'accuracy'))
  ```

</details>

<details>
<summary>8. run</summary>

- command

  ```bash
  # Get the Flops of a model
  > mim run onedl-mmpretrain get_flops resnet101_b16x8_cifar10.py
  # Publish a model
  > mim run onedl-mmpretrain publish_model input.pth output.pth
  # Train models on a slurm HPC with one GPU
  > srun -p partition --gres=gpu:1 mim run onedl-mmpretrain train \
      resnet101_b16x8_cifar10.py --work-dir tmp
  # Test models on a slurm HPC with one GPU, report accuracy
  > srun -p partition --gres=gpu:1 mim run onedl-mmpretrain test \
      resnet101_b16x8_cifar10.py tmp/epoch_3.pth --metrics accuracy
  # Print help messages of sub-command run
  > mim run -h
  # Print help messages of sub-command run, list all available scripts in
  # codebase onedl-mmpretrain
  > mim run onedl-mmpretrain -h
  # Print help messages of sub-command run, print the help message of
  # training script in onedl-mmpretrain
  > mim run onedl-mmpretrain train -h
  ```

- api

  ```python
  from mim import run

  run(repo='onedl-mmpretrain', command='get_flops',
      other_args=('resnet101_b16x8_cifar10.py',))
  run(repo='onedl-mmpretrain', command='publish_model',
      other_args=('input.pth', 'output.pth'))
  run(repo='onedl-mmpretrain', command='train',
      other_args=('resnet101_b16x8_cifar10.py', '--work-dir', 'tmp'))
  run(repo='onedl-mmpretrain', command='test',
      other_args=('resnet101_b16x8_cifar10.py', 'tmp/epoch_3.pth', '--metrics accuracy'))
  ```

</details>

<details>
<summary>9. gridsearch</summary>

- command

  ```bash
  # Parameter search on a single server with CPU by setting `gpus` to 0 and
  # 'launcher' to 'none' (if applicable). The training script of the
  # corresponding codebase will fail if it doesn't support CPU training.
  > mim gridsearch onedl-mmpretrain resnet101_b16x8_cifar10.py --work-dir tmp --gpus 0 \
      --search-args '--optimizer.lr 1e-2 1e-3'
  # Parameter search with on a single server with one GPU, search learning
  # rate
  > mim gridsearch onedl-mmpretrain resnet101_b16x8_cifar10.py --work-dir tmp --gpus 1 \
      --search-args '--optimizer.lr 1e-2 1e-3'
  # Parameter search with on a single server with one GPU, search
  # weight_decay
  > mim gridsearch onedl-mmpretrain resnet101_b16x8_cifar10.py --work-dir tmp --gpus 1 \
      --search-args '--optimizer.weight_decay 1e-3 1e-4'
  # Parameter search with on a single server with one GPU, search learning
  # rate and weight_decay
  > mim gridsearch onedl-mmpretrain resnet101_b16x8_cifar10.py --work-dir tmp --gpus 1 \
      --search-args '--optimizer.lr 1e-2 1e-3 --optimizer.weight_decay 1e-3 \
      1e-4'
  # Parameter search on a slurm HPC with one 8-GPU node, search learning
  # rate and weight_decay
  > mim gridsearch onedl-mmpretrain resnet101_b16x8_cifar10.py --work-dir tmp --gpus 8 \
      --partition partition_name --gpus-per-node 8 --launcher slurm \
      --search-args '--optimizer.lr 1e-2 1e-3 --optimizer.weight_decay 1e-3 \
      1e-4'
  # Parameter search on a slurm HPC with one 8-GPU node, search learning
  # rate and weight_decay, max parallel jobs is 2
  > mim gridsearch onedl-mmpretrain resnet101_b16x8_cifar10.py --work-dir tmp --gpus 8 \
      --partition partition_name --gpus-per-node 8 --launcher slurm \
      --max-jobs 2 --search-args '--optimizer.lr 1e-2 1e-3 \
      --optimizer.weight_decay 1e-3 1e-4'
  # Print the help message of sub-command search
  > mim gridsearch -h
  # Print the help message of sub-command search and the help message of the
  # training script of codebase onedl-mmpretrain
  > mim gridsearch onedl-mmpretrain -h
  ```

- api

  ```python
  from mim import gridsearch

  gridsearch(repo='onedl-mmpretrain', config='resnet101_b16x8_cifar10.py', gpus=0,
             search_args='--optimizer.lr 1e-2 1e-3',
             other_args=('--work-dir', 'tmp'))
  gridsearch(repo='onedl-mmpretrain', config='resnet101_b16x8_cifar10.py', gpus=1,
             search_args='--optimizer.lr 1e-2 1e-3',
             other_args=('--work-dir', 'tmp'))
  gridsearch(repo='onedl-mmpretrain', config='resnet101_b16x8_cifar10.py', gpus=1,
             search_args='--optimizer.weight_decay 1e-3 1e-4',
             other_args=('--work-dir', 'tmp'))
  gridsearch(repo='onedl-mmpretrain', config='resnet101_b16x8_cifar10.py', gpus=1,
             search_args='--optimizer.lr 1e-2 1e-3 --optimizer.weight_decay'
                         '1e-3 1e-4',
             other_args=('--work-dir', 'tmp'))
  gridsearch(repo='onedl-mmpretrain', config='resnet101_b16x8_cifar10.py', gpus=8,
             partition='partition_name', gpus_per_node=8, launcher='slurm',
             search_args='--optimizer.lr 1e-2 1e-3 --optimizer.weight_decay'
                         ' 1e-3 1e-4',
             other_args=('--work-dir', 'tmp'))
  gridsearch(repo='onedl-mmpretrain', config='resnet101_b16x8_cifar10.py', gpus=8,
             partition='partition_name', gpus_per_node=8, launcher='slurm',
             max_workers=2,
             search_args='--optimizer.lr 1e-2 1e-3 --optimizer.weight_decay'
                         ' 1e-3 1e-4',
             other_args=('--work-dir', 'tmp'))
  ```

</details>

## Contributing

We appreciate all contributions to improve mim. Please refer to [CONTRIBUTING.md](https://github.com/vbti-development/onedl-mmcv/blob/master/CONTRIBUTING.md) for the contributing guideline.

## License

This project is released under the [Apache 2.0 license](LICENSE).

## Projects in VBTI-development

- [OneDL-MMEngine](https://github.com/vbti-development/onedl-onedl-mmengine): OpenMMLab foundational library for training deep learning models.
- [MMCV](https://github.com/vbti-development/onedl-mmcv): OpenMMLab foundational library for computer vision.
- [MMPreTrain](https://github.com/vbti-development/onedl-mmpretrain): OpenMMLab pre-training toolbox and benchmark.
- [MMDetection](https://github.com/vbti-development/onedl-mmdetection): OpenMMLab detection toolbox and benchmark.
- [MMRotate](https://github.com/vbti-development/onedl-mmrotate): OpenMMLab rotated object detection toolbox and benchmark.
- [MMSegmentation](https://github.com/vbti-development/onedl-mmsegmentation): OpenMMLab semantic segmentation toolbox and benchmark.
- [MMDeploy](https://github.com/vbti-development/onedl-mmdeploy): OpenMMLab model deployment framework.
- [MIM](https://github.com/vbti-development/onedl-mim): MIM installs OpenMMLab packages.

## Projects in OpenMMLab

- [MMagic](https://github.com/open-mmlab/mmagic): Open**MM**Lab **A**dvanced, **G**enerative and **I**ntelligent **C**reation toolbox.
- [MMDetection3D](https://github.com/open-mmlab/mmdetection3d): OpenMMLab's next-generation platform for general 3D object detection.
- [MMYOLO](https://github.com/open-mmlab/mmyolo): OpenMMLab YOLO series toolbox and benchmark.
- [MMOCR](https://github.com/open-mmlab/mmocr): OpenMMLab text detection, recognition, and understanding toolbox.
- [MMPose](https://github.com/open-mmlab/mmpose): OpenMMLab pose estimation toolbox and benchmark.
- [MMHuman3D](https://github.com/open-mmlab/mmhuman3d): OpenMMLab 3D human parametric model toolbox and benchmark.
- [MMSelfSup](https://github.com/open-mmlab/mmselfsup): OpenMMLab self-supervised learning toolbox and benchmark.
- [MMRazor](https://github.com/open-mmlab/mmrazor): OpenMMLab model compression toolbox and benchmark.
- [MMFewShot](https://github.com/open-mmlab/mmfewshot): OpenMMLab fewshot learning toolbox and benchmark.
- [MMAction2](https://github.com/open-mmlab/mmaction2): OpenMMLab's next-generation action understanding toolbox and benchmark.
- [MMTracking](https://github.com/open-mmlab/mmtracking): OpenMMLab video perception toolbox and benchmark.
- [MMFlow](https://github.com/open-mmlab/mmflow): OpenMMLab optical flow toolbox and benchmark.
- [MMEditing](https://github.com/open-mmlab/mmediting): OpenMMLab image and video editing toolbox.
- [MMGeneration](https://github.com/open-mmlab/mmgeneration): OpenMMLab image and video generative models toolbox.
- [MMEval](https://github.com/open-mmlab/mmeval): A unified evaluation library for multiple machine learning libraries.
- [Playground](https://github.com/open-mmlab/playground): A central hub for gathering and showcasing amazing projects built upon OpenMMLab.
