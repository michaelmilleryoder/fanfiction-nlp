# -*- coding: utf-8 -*-

import math
from . import BaseFeatureExtracter, register_extracter


@register_extracter('spkappcnt')
class SpkAppCntFeatureExtracter(BaseFeatureExtracter):
    """Speaker appearance count feature extracter."""
    
    def __init__(self):
        super(SpkAppCntFeatureExtracter, self).__init__()

    @classmethod
    def extract(self, ret, paragraph_num, paragraph_has_quote, 
                character_appear_token_id, character_num, characters, **kargs):
        """
        Extract speaker appearance count features
        """
        for i in range(paragraph_num):
            if paragraph_has_quote[i]:
                for j in range(character_num):
                    char = characters.keys()[j]
                    count = len(character_appear_token_id[char])
                    ret[i][j]['spkappcnt'] = math.log(count+0.0001)
