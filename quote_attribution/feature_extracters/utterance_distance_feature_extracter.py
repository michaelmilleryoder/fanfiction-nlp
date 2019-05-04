# -*- coding: utf-8 -*-

from . import BaseFeatureExtracter, register_extracter


@register_extracter('disttoutter')
class UttrDistFeatureExtracter(BaseFeatureExtracter):
    """Utterance distance feature extracter."""
    
    def __init__(self, **kargs):
        super(UttrDistFeatureExtracter, self).__init__(**kargs)

    @classmethod
    def extract(self, ret, tokens, paragraph_num, paragraph_has_quote, 
                paragraph_quote_token_id, paragraph_quote_type, 
                character_appear_token_id, character_num, characters, **kargs):
        """
        Extract utterance distance features
        """
        for i in range(paragraph_num):
            if paragraph_has_quote[i]:
                for j in range(character_num):
                    char = list(characters.keys())[j]
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
                                if tokens[cid].paragraph_id == i and cid > endId and cid - endId <= 3:
                                    paragraph_quote_type[i] = "Explicit"
                                else:
                                    if paragraph_quote_type[i] == "None":
                                        paragraph_quote_type[i] = "Implicit"
                        pid += 2
                    #ret[i][j]['disttoutter'] = math.log(dist+1)
                    ret[i][j]['disttoutter'] = 1.0 / (dist + 1)

    @classmethod
    def build_extracter(cls, args):
        """Build a new UttrDistFeatureExtracter instance."""
        return cls()
