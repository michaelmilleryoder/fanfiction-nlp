# -*- coding: utf-8 -*-
import os
import argparse
import importlib
from collections import OrderedDict
from .base_feature_extracter import BaseFeatureExtracter


EXTRACTER_REGISTRY = {}


def build_feature_extracters(args):
    """Build feature extracters from registered extracters.
    
    Args:
        args: The parsed CLI arguments object.

    Return:
        A sequence of feature extracters.
    """
    features = []
    for feat in args.features:
        features.append(EXTRACTER_REGISTRY[feat].build_extracter(args))
    return features


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
    """Add arguments of registerd extracters to the parser.

    Args:
        parser: The CLI parser.
    """
    for extracter_name in EXTRACTER_REGISTRY:
        group_args = parser.add_argument_group('Arguments for feature extracter: {}'.format(extracter_name))
        EXTRACTER_REGISTRY[extracter_name].add_args(group_args)


# automatically import any Python files in the models/ directory
for file in os.listdir(os.path.dirname(__file__)):
    if file.endswith('.py') and not file.startswith('_'):
        extracter_name = file[:file.find('.py')]
        extracter = importlib.import_module('feature_extracters.' + extracter_name)
