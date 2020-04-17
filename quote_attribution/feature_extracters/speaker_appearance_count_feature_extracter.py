# -*- coding: utf-8 -*-

import math
import pdb
from . import BaseFeatureExtracter, register_extracter


@register_extracter('spkappcnt')
class SpkAppCntFeatureExtracter(BaseFeatureExtracter):
    """`Speaker mention count' feature extracter.
    
    Speaker Mention Count (represented as frequency). This feature is the 
    count of the mention of the character in the text, which could be considered 
    as the prior probability that the character speaks.
    """
    
    def __init__(self, **kargs):
        super(SpkAppCntFeatureExtracter, self).__init__(**kargs)

    @classmethod
    def extract(self, ret, paragraph_num, paragraph_has_quote, 
                character_appear_token_id, character_num, characters, **kargs):
        """Extract `speaker appearance count' features for a chapter.
        
        Args:
            ret: 2-D list of directories to save features.
            paragraph_num: Number of paragraphs.
            paragraph_has_quote: Whether the paragraph contains a quote.
            character_appear_token_id: The token IDs of character mentions.
            character_num: Number of characters.
            characters: Characters of the chapter
        """
        sum_count = 0
        for c in character_appear_token_id:
            sum_count += len(character_appear_token_id[c])
        for i in range(paragraph_num):
            if paragraph_has_quote[i]:
                for j in range(character_num):
                    char = list(characters.keys())[j]
                    if not char in character_appear_token_id:
                        pdb.set_trace()
                    count = len(character_appear_token_id[char])
                    ret[i][j]['spkappcnt'] = float(count) / float(sum_count)

    @classmethod
    def build_extracter(cls, args):
        """Build a new SpkAppCntFeatureExtracter instance."""
        return cls()
