# -*- coding: utf-8 -*-

import copy
from . import BaseFeatureExtracter, register_extracter


@register_extracter('neighboring')
class NeighboringFeatureExtracter(BaseFeatureExtracter):
    """Neighboring feature extracter."""
    
    def __init__(self, neighboring_before, neighboring_after, **kargs):
        super(NeighboringFeatureExtracter, self).__init__(**kargs)
        self.neighboring_before = neighboring_before
        self.neighboring_after = neighboring_after

    def extract(self, ret, paragraph_has_quote, **kargs):
        """
        Extract neighboring feature
        """
        before = self.neighboring_before
        after = self.neighboring_after
        newfeatures = copy.deepcopy(ret)
        for i in range(len(ret)):
            for j in range(len(ret[i])):
                pointer = i - 1
                kk = 0
                nowkeys = copy.deepcopy(list(newfeatures[i][j].keys()))
                while pointer >= 0 and kk < before:
                    if paragraph_has_quote[pointer]:
                        for key in nowkeys:
                            newkey = key+'-'+str(1+kk)
                            newfeatures[i][j][newkey] = ret[pointer][j][key]
                        kk += 1
                    pointer -= 1
                if kk != before:
                    for k in range(kk, before):
                        for key in nowkeys:
                            newkey = key+'-'+str(1+k)
                            newfeatures[i][j][newkey] = 0.0
                pointer = i + 1
                kk = 0
                while pointer < len(ret) and kk < after:
                    if paragraph_has_quote[pointer]:
                        for key in nowkeys:
                            newkey = key+'+'+str(1+kk)
                            newfeatures[i][j][newkey] = ret[pointer][j][key]
                        kk += 1
                    pointer += 1
                if kk != after:
                    for k in range(kk, before):
                        for key in nowkeys:
                            newkey = key+'+'+str(1+k)
                            newfeatures[i][j][newkey] = 0.0
        for i in range(len(ret)):
            for j in range(len(ret[i])):
                ret[i][j] = copy.deepcopy(newfeatures[i][j])

    @classmethod
    def build_extracter(cls, args):
        """Build a new NeighboringFeatureExtracter instance."""
        return cls(args.neighboring_before, args.neighboring_after)

    @staticmethod
    def add_args(parser):
        """Add model-specific arguments to the parser."""
        # fmt: off
        parser.add_argument('--neighboring-before', type=int, default=0,
                            help='number of utterances before the current one '
                                 'to be incorporated in neighboring (default: 0)')
        parser.add_argument('--neighboring-after', type=int, default=0,
                            help='number of utterances after the current one '
                                 'to be incorporated in neighboring (default: 0)')
