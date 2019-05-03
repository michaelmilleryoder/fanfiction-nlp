# -*- coding: utf-8 -*-


class BaseFeatureExtracter(object):
    """Base class for feature extracter."""
    
    def __init__(self, **kargs):
        super(BaseFeatureExtracter, self).__init__(**kargs)

    def extract(self, ret, **kargs):
        raise NotImplementedError('FeatureExtracters must implement the extract method')

    @classmethod
    def build_extracter(cls, args):
        """Build a new feature extracter instance."""
        raise NotImplementedError('FeatureExtracters must implement the build_extracter method')

    @staticmethod
    def add_args(parser):
        """Add feature-extracter-specific arguments to the parser."""
        pass
