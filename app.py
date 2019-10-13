# -*- coding: utf-8 -*-

from scripts import tabledef
from scripts import forms
from scripts import helpers
from flask import Flask, redirect, url_for, render_template, request, session
import logging
import json
import sys
import os
import unicodedata
import time
import re
import pandas
import numpy as np
import matplotlib.pyplot as plt
import math
import itertools
import ast
import nltk
from nltk.stem.wordnet import *
from nltk.corpus import stopwords
from nltk.tag.perceptron import PerceptronTagger
from nltk.stem.porter import PorterStemmer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction import DictVectorizer
from scipy import sparse
import stripe

app = Flask(__name__)
app.secret_key = b'\xfe\xc1Z\x89\xb6\xb4\xfco\xa1(\xa9\xa2'#os.urandom(12)  # Generic key for dev purposes only
app.logger.addHandler(logging.StreamHandler(sys.stdout))
app.logger.setLevel(logging.ERROR)

# Heroku
from flask_heroku import Heroku
heroku = Heroku(app)

#Stripe info
stripe_keys = {
  'secret_key': 'sk_test_p0wapFDbjIuNPA2HLHJSao9n00CB0hSEyt',
  'publishable_key': 'pk_test_iLDTkTXOBsqmeIKupSLGYhHQ00SAHfIA4d'
}
stripe.api_key = stripe_keys['secret_key']

# Load Google word2vec model
from gensim.models.keyedvectors import KeyedVectors
basedir = os.path.abspath(os.path.dirname(__file__))
model_path = 'GoogleNews-vectors-negative300-SLIM.bin.gz'
w2v_model = KeyedVectors.load_word2vec_format(os.path.join(basedir, model_path), binary=True, limit=100000)
from DocSim import DocSim
ds = DocSim(w2v_model)

# ======== Routing =========================================================== #
# -------- Login ------------------------------------------------------------- #
@app.route('/', methods=['GET', 'POST'])
def login():
    if not session.get('logged_in'):
        form = forms.LoginForm(request.form)
        if request.method == 'POST':
            username = request.form['username'].lower()
            password = request.form['password']
            if form.validate():
                if helpers.credentials_valid(username, password):
                    session['logged_in'] = True
                    session['username'] = username
                    return json.dumps({'status': 'Login successful'})
                return json.dumps({'status': 'Invalid user/pass'})
            return json.dumps({'status': 'Both fields required'})
        return render_template('login.html', form=form)
    project_list = helpers.get_project_list()
    return render_template('home.html', project_list=project_list,project_exemple=helpers.project_exemple)


@app.route("/logout")
def logout():
    session['logged_in'] = False
    return redirect(url_for('login'))


# -------- Signup ---------------------------------------------------------- #
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if not session.get('logged_in'):
        form = forms.LoginForm(request.form)
        if request.method == 'POST':
            username = request.form['username'].lower()
            password = helpers.hash_password(request.form['password'])
            email = request.form['email']
            if form.validate():
                if not helpers.username_taken(username):
                    helpers.add_user(username, password, email)
                    session['logged_in'] = True
                    session['username'] = username
                    return json.dumps({'status': 'Signup successful'})
                return json.dumps({'status': 'Username taken'})
            return json.dumps({'status': 'User/Pass required'})
        return render_template('login.html', form=form)
    return redirect(url_for('login'))

# -------- Add Project Front Page ---------------------------------------------------------- #
@app.route('/offer', methods=['GET', 'POST'])
def offer():
    if not session.get('logged_in'):
        form = forms.LoginForm(request.form)
        return render_template('login.html', form=form)
    if request.args:
        if not helpers.get_pay():
            return redirect(url_for('purchase'))
        return redirect(url_for('login'))
    message = "This functionnality is disabled, please purchase before using otherwise the offer will not be added."
    if helpers.get_pay():
        message = ""
        return render_template('offer.html',  message=message)
    return render_template('offer_disabled.html',  message=message)

@app.route('/purchase')
def purchase():
    if not session.get('logged_in'):
        form = forms.LoginForm(request.form)
        return render_template('login.html', form=form)
    message = "To have unlimited ability to add new offers please buy for $1.00 only."
    if helpers.get_pay():
        message = "Thank you for purchasing, you can now add new offers. You can also support us by purchassing again ;)"
    return render_template('purchase.html', key=stripe_keys['publishable_key'], message=message)

# -------- Add Project ---------------------------------------------------------- #
@app.route('/project', methods=['POST'])
def project():
    if helpers.get_pay():
        form = forms.ProjectForm(request.form)
        if request.method == 'POST':
            username =  session['username']
            description = request.form['description']
            title = request.form['title']
            if form.validate():
                helpers.add_project(username, title, description)
                return json.dumps({'status': 'Added'})
            return json.dumps({'status': 'Issue with form'})
    return render_template('home.html')

# -------- Add Project ---------------------------------------------------------- #
@app.route('/analyze', methods=['POST'])
def analyze():
    if request.method == 'POST':
        data = request.form
        df = pandas.DataFrame(data.to_dict(flat=False)).T.reset_index()
        df.columns = ["File name","text"]
        df["File name"] = df["File name"].apply(lambda x : x[x.find("[")+1 : x.find("]")] if x != "__offer__" else x)
        #preprocessing
        def lower_remove_punct(text):
            import string
            punct = set(string.punctuation)
            for c in punct:
                text = text.replace(c," ")
            text = text.replace("\n"," ").replace("\r"," ").replace("\t"," ").replace("  "," ")
            return text.lower()
        def extract_words_remove_stopwords(text):
            import itertools, nltk, string
            punct = set(string.punctuation)
            stop_words = set(nltk.corpus.stopwords.words('english')) | set(nltk.corpus.stopwords.words('french')) | set(nltk.corpus.stopwords.words('spanish'))
            candidates = nltk.word_tokenize(text.lower())
            return [cand for cand in candidates
                    if cand not in stop_words and not all(char in punct for char in cand) and len(cand) > 1]
        def stemming(str_input):
            porter_stemmer = PorterStemmer()
            words = [porter_stemmer.stem(word) for word in str_input]
            return words
        df["text"] = df["text"].apply(lower_remove_punct)
        w2v_source_doc = df[df["File name"]=="__offer__"].iloc[0].text
        w2v_target_docs = list(df.text)
        df["text"] = df["text"].apply(extract_words_remove_stopwords)
        df["text"] = df["text"].apply(stemming)
        df["text"] = df["text"].apply(lambda x: x + list(map("_".join, nltk.ngrams(x,n=2))))
        df["text"] = df["text"].apply(lambda x : " ".join(x))
        #transformation
        text_matrix = TfidfVectorizer(min_df=1, norm = None).fit_transform(df["text"])
        #data mining
        offer_index = df[df["File name"]=="__offer__"].index[0]
        dist_bow = cosine_similarity(text_matrix, text_matrix[offer_index])
        dist_w2v = [result['score'] for result in ds.calculate_similarity(w2v_source_doc, w2v_target_docs)]
        df["Score Bow"] = dist_bow
        df["Score W2v"] = dist_w2v
        df["Score"] = (df["Score Bow"] + df["Score W2v"])/2
        df = df.sort_values("Score", ascending = False).tail(-1).reset_index(drop = True)
        df["Rank"] = df.index
        df["Rank"] = df["Rank"] + 1
        df = df[["Rank","File name","Score"]]
        html_result = df.to_html(index=False, classes="table is-bordered is-striped is-narrow is-hoverable is-fullwidth")
        return json.dumps({'status': 'Added', "data":html_result})
    return render_template('home.html')

# -------- Settings ---------------------------------------------------------- #
@app.route('/settings', methods=['GET', 'POST'])
def settings():
    if session.get('logged_in'):
        if request.method == 'POST':
            password = request.form['password']
            if password != "":
                password = helpers.hash_password(password)
            email = request.form['email']
            helpers.change_user(password=password, email=email)
            return json.dumps({'status': 'Saved'})
        user = helpers.get_user()
        return render_template('settings.html', user=user)
    return redirect(url_for('login'))

# -------- Charge ---------------------------------------------------------- #
@app.route('/charge', methods=['POST'])
def charge():
    try:
        # amount in cents
        amount = 100
        customer = stripe.Customer.create(
            email='sample@customer.com',
            source=request.form['stripeToken']
        )
        stripe.Charge.create(
            customer=customer.id,
            amount=amount,
            currency='usd',
            description='Flask Charge'
        )
        helpers.add_pay(session['username'])
        return redirect(url_for('login'))
    except stripe.error.StripeError:
        return redirect(url_for('login'))

# ======== Main ============================================================== #
if __name__ == "__main__":
    app.run(debug=True, use_reloader=True)
