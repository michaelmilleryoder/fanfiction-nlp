# -*- coding: utf-8 -*-

from . import BaseFeatureExtracter, register_extracter


@register_extracter('spkcntpar')
class SpkCntParFeatureExtracter(BaseFeatureExtracter):
    """Speaker mention count in paragraph feature extracter."""
    
    def __init__(self, **kargs):
        super(SpkCntParFeatureExtracter, self).__init__(**kargs)

    @classmethod
    def extract(self, ret, paragraph_num, paragraph_has_quote, 
                paragraph_start_token_id, paragraph_end_token_id,
                paragraph_quote_token_id, character_appear_token_id, 
                character_num, characters, **kargs):
        """
        Extract speaker mention count in paragraph feature
        """
        for i in range(paragraph_num):
            if paragraph_has_quote[i]:
                parStart = paragraph_start_token_id[i]
                parEnd = paragraph_end_token_id[i]
                for j in range(character_num):
                    char = list(characters.keys())[j]
                    parCnt = 0
                    quoCnt = 0
                    pid = 0
                    for cid in character_appear_token_id[char]:
                        if (parStart <= cid and parEnd >= cid):
                            parCnt += 1
                    while pid < len(paragraph_quote_token_id[i]):
                        startId = paragraph_quote_token_id[i][pid]
                        endId = paragraph_quote_token_id[i][pid+1]
                        for cid in character_appear_token_id[char]:
                            if (startId <= cid and endId >= cid):
                                quoCnt += 1
                        pid += 2
                    ret[i][j]['spkcntpar'] = parCnt - quoCnt

    @classmethod
    def build_extracter(cls, args):
        """Build a new SpkCntParFeatureExtracter instance."""
        return cls()
