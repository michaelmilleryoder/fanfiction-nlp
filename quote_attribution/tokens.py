#!/usr/bin/env python3 -u
# -*- coding: utf-8 -*-

from html.parser import HTMLParser

class Token(object):
    """Class for tokens.

    Args:
        chapter_id, paragraph_id, token_id: should match annotations. Token IDs restart every paragraph.

    """

    def __init__(self, chapter_id, paragraph_id, 
                story_token_id, paragraph_token_id, word, 
                 in_quotation, characters):
        super(Token, self).__init__()
        self.chapter_id = int(chapter_id)
        self.paragraph_id = int(paragraph_id)
        self.story_token_id = int(story_token_id) 
        self.paragraph_token_id = int(paragraph_token_id) 
        self.word = word
        self.in_quotation = in_quotation
        self.characters = characters # list


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


class Mention(object):
    """ Class for annotating a span of text """

    def __init__(self, begin_token_id, end_token_id, annotation, text=''):           
        self.begin_token_id = begin_token_id                                         
        self.end_token_id = end_token_id                                             
        self.annotation = annotation 
        
    def __repr__(self):
        return f"{self.begin_token_id}-{self.end_token_id}: {self.annotation}"


class CharacterMentionParser(HTMLParser):
    
    def __init__(self):
        HTMLParser.__init__(self)
        self.character_mentions = [] # ordered list of Mentions
        self.character_tokens = {} # token_id: [characters]
        self.current_token_id = 0
        self.current_characters = [] # stack for holding current characters
        self.start_token_ids = [] # stack for holding tag start token IDs
        self.tokens = [] # the tokens without the tags
    
    def handle_starttag(self, tag, attrs):
        self.current_characters.append(attrs[0][1])
        self.start_token_ids.append(self.current_token_id)
        
    def handle_endtag(self, tag):
        
        start_id = self.start_token_ids.pop()
        exclusive_end_id = self.current_token_id
        character = self.current_characters.pop()
        
        # Add to character_mentions
        self.character_mentions.append(Mention(
            start_id, 
            exclusive_end_id,
            character
        ))
        
        # Add to character_tokens
        for token_id in range(start_id, exclusive_end_id):
            if not token_id in self.character_tokens:
                self.character_tokens[token_id] = []
            self.character_tokens[token_id].append(character)
        
    def handle_data(self, data):
        words = data.split()
        self.tokens += words
        self.current_token_id += len(words)
        
    def get_tokens(self):
        return self.tokens
    
    def get_character_mentions(self):
        return self.character_mentions
    
    def print_character_mentions(self):
        for mention in self.character_mentions:
            print(f"{mention}\n")
            
    def get_character_tokens(self):
        return self.character_tokens
