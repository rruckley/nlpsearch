#!/usr/bin/python3

import json
import re

from flask import Flask
from flask import request

import nltk
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
from nltk.tree import Tree

app = Flask(__name__)

## TODO: Take output verbs / action words and run them over a list of available actions
## TODO: Handle multi-sentence input
## TODO: Improve grammer for chunking

## Extract Named entities
def extract_ne(sent):
    words = word_tokenize(sent,language="english")
    tags = nltk.pos_tag(words)
    tree = nltk.ne_chunk(tags,binary=True)
    return tree

# nltk.download('omw-1.4')
lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words('english'))

# Process query string
def process_query(sent):
    try:
        words = nltk.word_tokenize(sent,language="english")
        # Remove stop words
        ## filtered = [w for w in words if not w in stop_words]
        fixed = [lemmatizer.lemmatize(w) for w in words ]
        tagged = nltk.pos_tag(fixed)
        tree = nltk.ne_chunk(tagged,binary=True)
        ## Simplistic grammer, could be improved
        chunk_gram = r"""Chunk: {<RB.?>*<VB.?>*<NNP>+<NN>?}"""
        chunk_parser = nltk.RegexpParser(chunk_gram)
        chunked = chunk_parser.parse(tree)
        ## print(tree)
        return tree
    except Exception as exception:
        print(str(exception))

def extract_information(tree):
    entity = ""
    verb = ""
    noun = []
    adjective = ""
    qs = request.args.get('q')
    tree = process_query(qs)
    for leaf in tree:
        if type(leaf) is tuple:
            (value,pos) = leaf
            ## print(pos,':',value)
            ## Use regular expressions to catch all varients of verbs
            if re.match(r'VB.?',pos):
                verb = value
            if pos == "NN" or pos == "NNS":
                noun.append(value)
            if pos == "JJ" or pos == "JJS":
                adjective = value
        if type(leaf) == Tree:
            ## print(leaf.label())
            if leaf.label() == 'NE':
                for j in leaf:
                    (value,pos) = j
                    entity += value + " "
                    ## print(pos,':',value)
    json_output = "{}"
    json_obj = json.loads(json_output)
    json_obj["entity"] = entity
    json_obj["verb"] = verb
    json_obj["noun"] = noun
    json_obj["adjective"] = adjective
    return json_obj

## Sample sentences
##sent = "I want to open a new ticket for Router01"
##sent = "Show me the performance graph for our Sydney office"
##sent = "I want to look up the list of services we have in New South Wales"
##sent = "Show me the bandwidth graph for Newcastle Warehouse"
##sent = "I need to raise a ticket about the performance issues at the Lane Cove office"
##sent = "please create an incident for the Belrose site. It has a performance issue."
##sent = "open the ticket OBCS234983"


## For now we assume only a single sentence as input.
@app.route('/')
def root():
    query_string = request.args.get('q')
    tree = process_query(query_string)
    json_obj = extract_information(tree)
    return json.dumps(json_obj)

if __name__ == '__main__':
    app.run()
