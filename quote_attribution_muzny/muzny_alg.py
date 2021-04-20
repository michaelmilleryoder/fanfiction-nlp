import sys, re, argparse
import pdb
from collections import Counter
from tqdm import tqdm

def read_ents(path):
    entities={}
    with open(path, encoding="utf-8") as file:
        for line in file:
            cols=line.rstrip().split("\t")
            cid=int(cols[0])
            name=cols[1]
            start=int(cols[2])
            end=int(cols[3])

            if start not in entities:
                entities[start]={}
            entities[start][end]=cid, name

    return entities

def read_tokens(path):

    children={}

    tokens=[]

    with open(path, encoding="utf-8") as file:
        file.readline()
        for line in file:
            #cols=line.rstrip().split("\t")
            cols=line.replace('\n', '').split("\t")
            if len(cols) < 14:
                #tqdm.write('messed up line')
                continue
            tokens.append(cols)
            tid=int(cols[2])
            head=int(cols[6])
            if head not in children:
                children[head]=[]
            children[head].append(tid)
    return tokens, children



validpos={"NN":1, "NNP":1, "NNS":1, "NNPS":1, "DT":1, "PRP$":1, "PRP":1, "JJ":1, "JJR":1, "JJS":1, "POS":1}

def find_entities_containing_position(position, entities, tokens):
    cands=[]

    start=position-10

    for start in range(position-10, position+1):
        if start in entities:
            for e_end in entities[start]:
                # print(start, e_end, tokens[start][8], tokens[e_end][8])
                if position >= start and position <= e_end:
                    if tokens[start][13] == "O":
                        cands.append((start, e_end, entities[start][e_end]))

    cands.sort(key=lambda x: x[1]-x[0], reverse=True)

    return cands


def find_entities_ending_at_position(end, entities, tokens):
    cands=[]

    start=end-10

    for start in range(end-10, end+1):
        if start in entities:
            for e_end in entities[start]:

                if e_end == end:
                    if tokens[start][13] == "O":
                        cands.append((start, e_end, entities[start][e_end]))

    cands.sort(key=lambda x: x[1]-x[0], reverse=True)

    return cands


# MENTION VERB QUOTE
def trigram_matching_before(tokens, tokenStart, entities):
    firstWord=tokens[tokenStart-1]
    word=firstWord[7]
    if word == ",":
        idd=None

        # find the rightmost token in a mention by starting from the quote and working backwords
        for n in range(2,4):

            secondWord=tokens[tokenStart-n]
            word=secondWord[7]
            pos=secondWord[10]
            lemma=secondWord[9]
            ss=secondWord[15]

            if lemma in target_verbs or ss == "B-verb.communication":
                cands=find_entities_ending_at_position(tokenStart-n-1, entities, tokens)
                if len(cands) > 0:
                    return cands[0]



    return None

target_verbs={"say":1, "cry":1, "reply":1, "add":1, "think":1, "observe":1, "call":1, "answer":1, "continue":1}

def get_string(rep, tokens):
    name=[]
    for i in rep:
        name.append(tokens[i][8])
    return ' '.join(name)

def get_descendents(tid, children, tokens):
    left=tid
    right=tid
    if tid in children:
        for child in children[tid]:
            rel=tokens[child][12]
            if rel == "det" or rel == "amod" or rel == "nn":
                if child < left:
                    left=child
                if child > right:
                    child=right
    rep=[]
    for i in range(left, right+1):
        rep.append(i)
    return rep

def get_dep_parse(tokens, tokenStart, tokenEnd, children, entities):
    num_sents=2
    cur=tokenStart-1
    startSID=int(tokens[cur][1])
    sid=startSID
    if tokens[tokenStart][0] == '':
        pdb.set_trace()
    startPID=int(tokens[tokenStart][0])
    pid=int(tokens[cur][0])

    # go backwards from quote
    while(startSID-sid <= num_sents and cur >= 0 and startPID == pid):
        sid=int(tokens[cur][1])
        ss=tokens[cur][15]
        lemma=tokens[cur][9]
        tid=int(tokens[cur][2])
        inQuote=tokens[cur][13]
        pid=int(tokens[cur][0])

        cur-=1

        # don't cross quotes
        if inQuote != "O":
            break

        if lemma in target_verbs or ss == "B-verb.communication":
            if tid in children:
                for child in children[tid]:
                    if tokens[child][13] == "O" and tokens[child][12]== "nsubj":
                        cands=find_entities_containing_position(child, entities, tokens)
                        if len(cands) > 0:
                            return cands[0]

                        
    cur=tokenEnd+1
    if cur >= len(tokens):
        return

    startSID=int(tokens[cur][1])
    sid=startSID
    pid=int(tokens[cur][0])

    # go forwards from quote
    while(sid-startSID <= num_sents and cur < len(tokens) and startPID == pid):
        sid=int(tokens[cur][1])
        ss=tokens[cur][15]
        lemma=tokens[cur][9]
        tid=int(tokens[cur][2])
        inQuote=tokens[cur][13]
        pid=int(tokens[cur][0])
    
        cur+=1
        if inQuote != "O":
            break

        if lemma in target_verbs or ss == "B-verb.communication":
            if tid in children:
                for child in children[tid]:
                    if tokens[child][13] == "O" and tokens[child][12]== "nsubj":
                        cands=find_entities_containing_position(child, entities, tokens)
                        if len(cands) > 0:
                            return cands[0]

    return None

def single_mention(tokens, tokenStart, tokenEnd, children, entities):

    parid=tokens[tokenStart][0]

    curParid=parid
    cur=tokenStart

    paragraphStartToken=0
    while(curParid == parid and cur >= 0):
        curParid=tokens[cur][0]
        cur-=1
    paragraphStartToken=cur+1

    cur=tokenEnd
    curParid=parid
    while(curParid == parid and cur < len(tokens)):
        curParid=tokens[cur][0]
        cur+=1
    paragraphEndToken=cur-1

    cands=find_entities_in_range(paragraphStartToken, paragraphEndToken, entities, tokens)

    if len(cands) > 0:
        cands.sort(key=lambda x: x[1]-x[0], reverse=True)
        # print(cands)

        return cands[0]

    return None


def find_entities_at_position(start, entities, tokens):
    cands=[]

    if start in entities:
        for e_end in entities[start]:
            if tokens[start][13] == "O":
                cands.append((start, e_end, entities[start][e_end]))

    cands.sort(key=lambda x: x[1]-x[0], reverse=True)

    return cands

def find_entities_in_range_in_quotes_only(start, end, entities, tokens):
    cands=[]
    for i in range(start, end):
        if i in entities:
            for e_end in entities[i]:
                if e_end < end:
                    if tokens[i][13] != "O":
                        cands.append((i, e_end, entities[i][e_end]))

    cands.sort(key=lambda x: x[1]-x[0])

    return cands

def find_entities_in_range(start, end, entities, tokens):
    cands=[]
    for i in range(start, end):
        if i in entities:
            for e_end in entities[i]:
                if e_end < end:
                    if tokens[i][13] == "O":
                        cands.append((i, e_end, entities[i][e_end]))

    cands.sort(key=lambda x: x[1]-x[0])

    return cands

def trigram_matching_after(tokens, tokenStart, maxLength, lastChar, entities):
    if lastChar == ".":
        return None
    if lastChar != ",":
        firstWord=tokens[tokenStart]
        word=firstWord[7]
        pos=firstWord[10]

        if word.lower() != word:
            return None
    mention=None

    # QUOTE MENTION VERB
    for i in range(tokenStart, tokenStart+maxLength):

        if i >= len(tokens):
            break

        word=tokens[i][7]
        pos=tokens[i][10]
        lemma=tokens[i][9]
        inQuote=tokens[i][13]
        ss=tokens[i][15]

        if inQuote != "O":
            break
        
        # find verb after quotation
        if lemma in target_verbs or ss == "B-verb.communication":
            mention=[]

            # find mention between quote and found verb
            cands=find_entities_in_range(tokenStart, i, entities, tokens)
            if len(cands) > 0:
                return cands[0]

    # QUOTE VERB MENTION
    for vidx in range(3):
        if len(tokens) <= tokenStart + vidx:
            continue
        if len(tokens[tokenStart+vidx]) < 11:
            pdb.set_trace()
        pos=tokens[tokenStart+vidx][10]
        lemma=tokens[tokenStart+vidx][9]
        ss=tokens[tokenStart+vidx][15]
        # find verb, skipping adverbs and modals
        if pos == "RB" or pos == "RBR" or pos == "MD":
            continue

        if lemma in target_verbs or ss == "B-verb.communication":
            mention=[]

            cands=find_entities_at_position(tokenStart+vidx+1, entities, tokens)

            if len(cands) > 0:
                return cands[0]



    return None

def getQuotes(tokens):
    quotes=[]
    start=None
    for idx,cols in enumerate(tokens):
        inQuote=cols[13]

        if (inQuote == "B-QUOTE" or inQuote == "O") and start != None:
            quotes.append((start, idx-1))
            start=None

        if inQuote == "B-QUOTE":
            start=idx

    if start != None:
        quotes.append((start, len(tokens)))

    return quotes

def attribute(tokens, start, end, lastChar, entities):
    mention=None
    fin=end+1
    if fin < len(tokens):
        mention=trigram_matching_after(tokens, fin, 5, lastChar, entities)

    if mention== None:
        mention=trigram_matching_before(tokens, start, entities)
    return mention

def get_turns(quotes):

    """ Get sets of quotations separated by some minimum window of non-quotations (here, 100) """

    window=100 # words
    lastEnd=None
    turns=[]
    current=[]
    for (start,end) in quotes:
        if lastEnd != None:
            if start-lastEnd > window:
                turns.append(current)
                current=[]
        current.append((start,end))
        lastEnd=end
    if len(current) > 0:
        turns.append(current)
    return turns

def get_vocatives(tokens, start, end, entities):

    # quotation marks
    start=start+1
    end=end-1

    cands=find_entities_in_range_in_quotes_only(start, end, entities, tokens)
    vocs=[]
    for s, e, cid in cands:
        # entities at the start of the quote followed by a comma
        if (s == start or (s > 0 and tokens[s-1][7] == ",")) and (e == end or tokens[e+1][7] == "," or tokens[e+1][7] == "!" or tokens[e+1][7] == "?"):
            vocs.append((s,e,cid))

    return vocs

def get_top_entities(tokens, quoteStart, quoteEnd, entities):


    ents=Counter()
    start=quoteStart-2000
    if start < 0:
        start=0
    end=quoteEnd+500
    if end >= len(tokens):
        end=len(tokens)

    cands=find_entities_in_range(start, end, entities, tokens)
    for (start, end, (charid, name)) in cands:
        ents[charid]+=1

    return ents

def get_previous_in_diff_par(mentions, quotes, idx, tokens):
    cand=idx-1
    par=int(tokens[quotes[idx]][0])
    cand_par=int(tokens[quotes[cand]][0])
    while par-cand_par <= 2 and cand >= 0:
        if par-cand_par == 2:
            if mentions[cand] is not None:
                return mentions[cand]

        cand-=1
        cand_par=int(tokens[quotes[cand]][0])


    return None

def attribute_quotes(filename, tokens, children, entities):

    attributed=[]

    # get raw quotes
    quotes=getQuotes(tokens)

    # aggregate quotes into quotation segments
    turns=get_turns(quotes)

    lastMention=None
    lastParid=None
    lastlastChar=None
    noneCount=0.
    total=0
    vocs=[]

    new_ent_id=0
    seen_ents={}

    all_char_mentions=[]
    quote_starts=[]

    for quotes in turns:
        all_mentions=[]
        mentions=Counter()
        for (start, end) in quotes:
            quote_starts.append(start)

            quote=[]
            parid=None
            for j in range(start,end+1):
                if j < len(tokens):
                    quote.append(tokens[j][8])
                    parid=tokens[j][0]

            lastChar=tokens[end-1][7]

            # attribute using trigram matching (QUOTE-MENTION-VERB etc.)
            mention=None
            mention=attribute(tokens, start, end, lastChar, entities)
            # print("mention", mention)
            if mention is None:
                mention=get_dep_parse(tokens, start, end, children, entities)

            if mention is None:
                mention=single_mention(tokens, start, end, children, entities)

            # if that fails and we're within the same paragraph as the last quote, then the mention is the last mention
            if parid == lastParid and mention is None:
                mention=lastMention
        
            # if the quote ends in a question and there is a vocative, make the last vocative the speaker
            if mention == None and lastlastChar == "?" and len(vocs) > 0:
                mention=vocs[-1]

            # if that fails, make the last vocative the speaker
            if mention == None and len(vocs) > 0:
                mention=vocs[-1]


            # if mention is not None:
            if lastParid != parid:
                vocs=[]

            lastMention=mention
            lastParid=parid
            lastlastChar=lastChar
            all_mentions.append(mention)

            # get the vocatives for the current quote to help attribute for the next quote
            for voc in get_vocatives(tokens, start, end, entities):
                vocs.append(voc)

            total+=1
            if mention == None:
                noneCount+=1

            charid=None

            if mention is not None:

                m_start, m_end, (charid, name)=mention

                attributed.append([start, end, m_start, m_end, name, charid])

            else:

                charid=None

                # if there is no mention, try to assign the label of the quote 2 quotes back
                if len(all_char_mentions) >= 2:
                    cand=get_previous_in_diff_par(all_char_mentions, quote_starts, len(quote_starts)-1, tokens)
                    if cand is not None:
                        charid=cand
                
                        attributed.append([start, end, None, None, None, charid])

                    else:
                        attributed.append([start, end, None, None, None, None])
            
                else:
                    attributed.append([start, end, None, None, None, None])

            all_char_mentions.append(charid)

        lastMention=None
        lastParid=None
        lastlastChar=None
        vocs=[]

    c=0

    for quotes in turns:
        for (start, end) in quotes:
            if attributed[c][5] == None:
                # if that doesn't work, assign the majority entity in the context
                ents=get_top_entities(tokens, start, end, entities)

                charid=None
                if len(ents) > 0:
                    top=ents.most_common()[0][0]
                    charid=top

                attributed[c]=[start, end, None, None, None, charid]

            c+=1
    
    ratio=0
    if total > 0:
        ratio=noneCount/total
    #sys.stderr.write ("%s, None: %.3f (%s/%s)\n" % (filename, ratio, noneCount, total))

    return attributed

def get_char_id(start, end, tokens):

    name=[]
    for tok in range(start, end+1):
        name.append(tokens[tok][8])
    
    name=' '.join(name)

    for token in range(end+1, start-1, -1):
        if tokens[token][14] != "-1":
            if tokens[token][10] != "PRP$":
                return tokens[token][14]

    return None

def write_attributed(filename, attributed):
    with open(filename, "w", encoding="utf-8") as out:
        out.write('\t'.join(["quote_start", "quote_end", "mention_start", "mention_end", "mention_phrase", "char_id"]) + "\n")

        for line in attributed:
            out.write('\t'.join(str(x) for x in line) + "\n")
    
    out.close()

def proc_one(tokensFile, entFile, outFile):
    tokens, children=read_tokens(tokensFile)
    entities=read_ents(entFile)
    attributed=attribute_quotes(outFile, tokens, children, entities)
    write_attributed(outFile, attributed)


if __name__ == "__main__":

    tokenFile=sys.argv[1]
    idd=re.sub(".tokens$", "", tokenFile.split("/")[-1])
    entFile=sys.argv[2]
    outFile=sys.argv[3]

    proc_one(tokenFile, entFile, outFile)
