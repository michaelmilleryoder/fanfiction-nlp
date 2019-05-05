# -*- coding: utf-8 -*-

from . import BaseFeatureExtracter, register_extracter


@register_extracter('disttoutter')
class UttrDistFeatureExtracter(BaseFeatureExtracter):
    """`Utterance distance' feature extracter.
    
    This feature captures the distance between the mention of the character and 
    the utterance. The intuition is that near character is likely to be the 
    speaker.

    This feature will be represented as $1 / (dist + 1)$.
    """
    
    def __init__(self, **kargs):
        super(UttrDistFeatureExtracter, self).__init__(**kargs)

    @classmethod
    def extract(self, ret, tokens, paragraph_num, paragraph_has_quote, 
                paragraph_quote_token_id, paragraph_quote_type, 
                character_appear_token_id, character_num, characters, **kargs):
        """Extract `utterance distance' features for a chapter.
        
        Args:
            ret: 2-D list of directories to save features.
            tokens: List of tokens.
            paragraph_num: Number of paragraphs.
            paragraph_has_quote: Whether the paragraph contains a quote.
            paragraph_quote_token_id: Start and end token IDs of quotes in paragraphs. Stored alternatively by start and end ids.
            paragraph_quote_type: The type of quotes in the paragraph. This argument will be modified in extracting features.
            character_appear_token_id: The token IDs of character mentions.
            character_num: Number of characters.
            characters: Characters of the chapter
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
                            if tokens[cid].in_quotation == 'O':
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
