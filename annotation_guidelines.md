# Annotation guidelines
These are annotation guidelines used to annotate character mentions for coreference resolution, as well as attributing quotes to characters.

## Character coreference annotation
Identify and group all mentions of singular characters, including all pronouns. 
In the following bullet points, examples are given in quotes with the parts annotated as entity mentions in italics. For example, in the example phrase “the woman who caused the hubbub”, *the woman* is annotated as an entity mention and “who caused the hubbub” is not.

### **Do** annotate
* *they/them/their/theirs* if it refers to a singular character
* *you know* and other vague expressions if the *you* probably refers to an actual character
* Common nouns, including with adjectives, such as “*her friend*” or “*a tall man*” or “*young Ben*”
* Entity mentions that span multiple tokens, such as “*Tom Riddle*”
* In the case of possessive prepositional phrases, such as “*his father*”, annotate *his* as the person that *his* is referring to, and the entire phrase as the father.
It is okay to have a single token be part of multiple entity mentions. In this way the mentions are nested.
* Prepositional phrases attached to nouns, like “*the woman in the car*” or “*an old friend of my parents*”
* Possessive pronouns (*his/her/theirs/its*)
* *Sir, ma’am*, other references, address terms or honorifics. This includes literal mention of them, such as “Can I call you *father*?”
* Determiners such as “*the wolf*”, “*that Mary*”, “*a tall stag*”, or “*a man*”
* Appositives, such as “*Jaina*, *a friend* and *fellow Jedi*” or “*our son Ben*”
* Animals if they have more than 1 mention (if they are more of a character than just the setting/background).
* Names, such as “*she* had introduced *herself* as *Bilbo Baggins*” or “*My* name is *Bilbo Baggins*”.

### **Don't** annotate
* *they/them/their/theirs* if it refers to multiple characters
* *you know*, *someone*, *one of them* and other vague expressions if they don't refer to a particular character (including song lyrics)
* After a copula, like “*he* was a trickster”. Only annotate the pronoun in this case
* *Who* and anything that comes in a relative clause after it. For example, “*Harry*, who took the bite”, or “*Jaina*, who was a friend and fellow Jedi”. Another example:  “*a social cripple* who doesn’t even know friendship and who would never get a girl with his types of tobacco ash”.
* Relative clauses that omit *that* or *who*. For example, “*the woman* sitting up and looking absolutely, horrifying, identical to *him*”
* Inanimate objects, even personified as in “the lamp screamed open me”
* Entity mentions split across words, such as “male and female Bilbos” or “*my* mum and dad’s”. The only entity mentions contiguous across words here is the entire phrase, which refers to multiple characters.

## Quote attribution annotation

### **Do** annotate
* Utterances that aren’t said in the moment, but referenced in the past
* Verbatim reported that characters write, for example in letters (because that would capture characters’ voices).
* Characters quoting other characters as quotes for both the characters (overlapping and/or nesting quotes are okay)
* Quotation marks surrounding the quote (arbitrary decision)

### **Don't** annotate
* Words placed in quotes that aren’t actually said. Example with no annotations: In our house the rule felt like “the stranger the book looks the more Mum will want to read it.”
* Quotes that are indirectly reported, like “she said that I was a stupid git”
* Hypothetical quotes that aren’t actually said. Example with no annotations: As he left , part of me wanted to call out to him , to say Albus , could you stop by the library and pick up some books about our parents ?
* Thoughts in characters’ heads (since they are not spoken, though they do say something about characterization). Even if it’s the characters telling themselves something.
* Quotatives between split quotes. Example: “What do you…” he said, “think about that.” would be 2 separate quotes.
* Things said by more than one character together
