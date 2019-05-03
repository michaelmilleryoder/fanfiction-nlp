# -*- coding: utf-8 -*-
import os
import argparse
import importlib
from collections import OrderedDict
from .base_feature_extracter import BaseFeatureExtracter


EXTRACTER_REGISTRY = {}


def build_feature_extracters(args):
    """Build feature extracters from registered extracters."""
    features = []
    for feat in args.features:
        features.append(EXTRACTER_REGISTRY[feat].build_extracter(args))
    return features


def extract_features(features, input):
    paragraph_num = input['paragraph_num']
    character_num = input['character_num']
    ret = []
    for i in range(paragraph_num):
        ret.append([])
        for j in range(character_num):
            ret[-1].append(OrderedDict())
    for feat in features:
        print('Extracting {} ...'.format(feat))
        if feat not in EXTRACTER_REGISTRY:
            print('Feature {} do not exist!!!!!!!'.format(feat))
            continue
        EXTRACTER_REGISTRY[feat].extract(ret, **input)
        print('Done')
    return ret


def register_extracter(name):
    """
    New feature extracter can be added to quote attributer with the :func:`register_extracter`
    function decorator.
    For example::
        @register_extracter('disttoutter')
        class ExtracterDisttoutter(BaseFeatureExtracter):
            (...)
    .. note:: All extracters must implement the :class:`BaseFeatureExtracter` interface.

    Args:
        name (str): the name of the feature extracter
    """

    def register_extracter_cls(cls):
        if name in EXTRACTER_REGISTRY:
            raise ValueError('Cannot register duplicate extracter ({})'.format(name))
        if not issubclass(cls, BaseFeatureExtracter):
            raise ValueError('Model ({}: {}) must extend BaseFeatureExtracter'.format(name, cls.__name__))
        EXTRACTER_REGISTRY[name] = cls
        return cls

    return register_extracter_cls


def add_extracter_args(parser):
    for extracter_name in EXTRACTER_REGISTRY:
        group_args = parser.add_argument_group('Arguments for feature extracter: {}'.format(extracter_name))
        EXTRACTER_REGISTRY[extracter_name].add_args(group_args)


# automatically import any Python files in the models/ directory
for file in os.listdir(os.path.dirname(__file__)):
    if file.endswith('.py') and not file.startswith('_'):
        extracter_name = file[:file.find('.py')]
        extracter = importlib.import_module('feature_extracters.' + extracter_name)

