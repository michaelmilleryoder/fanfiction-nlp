#!/usr/bin/env python3 -u
# -*- coding: utf-8 -*-

class Token(object):
    """Class for tokens.

    Args:
        chapter_id, paragraph_id, token_id: should match annotations. Token IDs restart every paragraph.

    """

    def __init__(self, chapter_id, paragraph_id, 
                story_token_id, paragraph_token_id, word, 
                 in_quotation, character):
        super(Token, self).__init__()
        self.chapter_id = int(chapter_id)
        self.paragraph_id = int(paragraph_id)
        self.story_token_id = int(story_token_id) 
        self.paragraph_token_id = int(paragraph_token_id) 
        self.word = word
        self.in_quotation = in_quotation
        self.character = character


class Token_BookNLP(object):
    """Class for tokens.

    Specialized for book-nlp.

    TODO: Scalability.
    """

    def __init__(self, paragraph_id, sentence_id, token_id, begin_offset, 
                 end_offset, whitespace_after, head_token_id, original_word, 
                 normalized_word, lemma, pos, ner, deprel, in_quotation, 
                 character_id, supersense):
        super(Token, self).__init__()
        self.paragraph_id = int(paragraph_id)
        self.sentence_id = int(sentence_id)
        self.token_id = int(token_id)
        self.begin_offset = int(begin_offset)
        self.end_offset = int(end_offset)
        self.whitespace_after = whitespace_after
        self.head_token_id = int(head_token_id)
        self.original_word = original_word
        self.normalized_word = normalized_word
        self.lemma = lemma
        self.pos = pos
        self.ner = ner
        self.deprel = deprel
        self.in_quotation_booknlp = in_quotation
        self.character_id = int(character_id)
        self.supersense = supersense
