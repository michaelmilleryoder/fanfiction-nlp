# -*- coding: utf-8 -*-

from . import BaseFeatureExtracter, register_extracter


@register_extracter('disttoutter')
class UttrDistFeatureExtracter(BaseFeatureExtracter):
    """Utterance distance feature extracter."""
    
    def __init__(self):
        super(UttrDistFeatureExtracter, self).__init__()

    @classmethod
    def extract(self, ret, tokens, paragraph_num, paragraph_has_quote, 
                paragraph_quote_token_id, character_appear_token_id, 
                character_num, characters, **kargs):
        """
        Extract utterance distance features
        """
        for i in range(paragraph_num):
            if paragraph_has_quote[i]:
                for j in range(character_num):
                    char = characters.keys()[j]
                    dist = len(tokens)
                    pid = 0
                    while pid < len(paragraph_quote_token_id[i]):
                        startId = paragraph_quote_token_id[i][pid]
                        endId = paragraph_quote_token_id[i][pid+1]
                        for cid in character_appear_token_id[char]:
                            if (not(startId <= cid and endId >= cid)):
                                if abs(startId - cid) < dist:
                                    dist = abs(startId - cid)
                                if abs(endId - cid) < dist:
                                    dist = abs(endId - cid)
                        pid += 2
                    #paragraphFeatures[i][j]['disttoutter'] = math.log(dist+1)
                    ret[i][j]['disttoutter'] = 1.0 / (dist + 1)
