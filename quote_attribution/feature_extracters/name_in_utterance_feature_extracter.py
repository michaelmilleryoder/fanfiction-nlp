# -*- coding: utf-8 -*-

from . import BaseFeatureExtracter, register_extracter


@register_extracter('nameinuttr')
class NameInUttrFeatureExtracter(BaseFeatureExtracter):
    """Name in utterance feature extracter."""
    
    def __init__(self):
        super(NameInUttrFeatureExtracter, self).__init__()

    @classmethod
    def extract(self, ret, paragraph_num, paragraph_has_quote, 
                paragraph_quote_token_id, character_appear_token_id, 
                character_num, characters, **kargs):
        """
        Extract name in utterance feature
        """
        for i in range(paragraph_num):
            if paragraph_has_quote[i]:
                for j in range(character_num):
                    char = characters.keys()[j]
                    appear = 0
                    pid = 0
                    while pid < len(paragraph_quote_token_id[i]):
                        startId = paragraph_quote_token_id[i][pid]
                        endId = paragraph_quote_token_id[i][pid+1]
                        for cid in character_appear_token_id[char]:
                            if (startId <= cid and endId >= cid):
                                appear = 1
                        pid += 2
                    ret[i][j]['nameinuttr'] = appear
