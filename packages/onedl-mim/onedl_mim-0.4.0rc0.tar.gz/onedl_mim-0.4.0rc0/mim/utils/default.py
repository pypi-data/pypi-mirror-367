# Copyright (c) OpenMMLab. All rights reserved.
import os
import os.path as osp

USER = 'vbti-development'
DEFAULT_URL = f'https://github.com/{USER}'

DEFAULT_MMCV_BASE_URL = 'https://mmwheels.onedl.ai'

RAW_GITHUB_URL = 'https://raw.githubusercontent.com/{owner}/{repo}/{branch}'

OFFICIAL_MODULES = [
    'onedl-mmpretrain', 'onedl-mmdet', 'mmdet3d', 'mmseg', 'mmaction2',
    'mmtrack', 'mmpose', 'mmedit', 'mmocr', 'mmgen', 'mmselfsup', 'mmrotate',
    'mmflow', 'mmyolo', 'mmagic'
]

PKG2PROJECT = {
    'onedl-mmcv': 'mmcv',
    'onedl-mmpretrain': 'mmpretrain',
    'onedl-mmdet': 'mmdetection',
    'mmdet3d': 'mmdetection3d',
    'onedl-mmsegmentation': 'mmsegmentation',
    'mmaction2': 'mmaction2',
    'mmtrack': 'mmtracking',
    'mmpose': 'mmpose',
    'mmedit': 'mmediting',
    'mmocr': 'mmocr',
    'mmgen': 'mmgeneration',
    'mmselfsup': 'mmselfsup',
    'mmrotate': 'mmrotate',
    'mmflow': 'mmflow',
    'mmyolo': 'mmyolo',
    'mmagic': 'mmagic',
}
# TODO: Should directly infer MODULE name from PKG info
PKG2MODULE = {
    'onedl-mmcv': 'mmcv',
    'mmaction2': 'mmaction',
    'onedl-mmsegmentation': 'mmseg',
}
MODULE2PKG = {
    'mmaction': 'mmaction2',
    'mmseg': 'onedl-mmsegmentation',
}

HOME = osp.expanduser('~')
DEFAULT_CACHE_DIR = osp.join(HOME, '.cache', 'mim')
if not osp.exists(DEFAULT_CACHE_DIR):
    os.makedirs(DEFAULT_CACHE_DIR)
