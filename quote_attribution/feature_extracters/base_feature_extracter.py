# -*- coding: utf-8 -*-


class BaseFeatureExtracter(object):
    """Base class for feature extracter."""
    
    def __init__(self):
        super(BaseFeatureExtracter, self).__init__()

    @classmethod
    def extract(self, ret, **kargs):
        raise NotImplementedError

    @staticmethod
    def add_args(parser):
        """Add feature-extracter-specific arguments to the parser."""
        pass
