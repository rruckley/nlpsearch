#!/usr/bin/python3

from flask import Flask
from flask import request
import json

import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords

app = Flask(__name__)

def extract_ne(sent):
    words = word_tokenize(sent,language="english")
    tags = nltk.pos_tag(words)
    tree = nltk.ne_chunk(tags,binary=True)
    return tree

# nltk.download('omw-1.4')
lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words('english'))

def process_content(sent):
    try:
        words = nltk.word_tokenize(sent)
        filtered = [w for w in words if not w in stop_words]
        fixed = [lemmatizer.lemmatize(w) for w in filtered ]
        tagged = nltk.pos_tag(fixed)
        tree = nltk.ne_chunk(tagged,binary=True)
        chunkGram = r"""Chunk: {<RB.?>*<VB.?>*<NNP>+<NN>?}"""
        chunkParser = nltk.RegexpParser(chunkGram)
        chunked = chunkParser.parse(tree)
        return chunked
    except Exception as e:
        print(str(e))

##sent = "I want to open a new ticket for Router01"
##sent = "Show me the performance graph for our Sydney office"
#sent = "I want to look up the list of services we have in New South Wales"
##sent = "Show me the bandwidth graph for Newcastle Warehouse"
#sent = "I need to raise a ticket about the performance issues we've been having at the Lane Cove office"
#sent = "please create an incident for the Belrose site. It has a performance issue."
#sent = "open the ticket OBCS234983"

@app.route('/')
def root():
    qs = request.args.get('q')
    return json.dumps(process_content(qs))

if __name__ == '__main__':
    app.run()
