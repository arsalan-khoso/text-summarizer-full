from __future__ import print_function
import array
import string
import operator
import random  # Added for generating random user IDs
import os  # Added for managing user data

# Natural Language Processing Libraries
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.probability import FreqDist
from flask import Flask, render_template, request, session, redirect, url_for  # Updated imports

# Webscrapping using BeautifulSoup, not yet implemented
import bs4 as bs  # beautifulsource4
import urllib3

import nltk

# Download the NLTK stopwords resource
nltk.download('stopwords')

# Now you can use the stopwords resource in your code
from nltk.corpus import stopwords

# Example usage:
stop_words = set(stopwords.words('english'))


class summarize:

	def get_summary(self, input, max_sentences):
		sentences_original = sent_tokenize(input)

		#Remove all tabs, and new lines
		if (max_sentences > len(sentences_original)):
			print ("Error, number of requested sentences exceeds number of sentences inputted")
			#Should implement error schema to alert user.
		s = input.strip('\t\n')
		
		#Remove punctuation, tabs, new lines, and lowercase all words, then tokenize using words and sentences 
		words_chopped = word_tokenize(s.lower())
		
		sentences_chopped = sent_tokenize(s.lower())

		stop_words = set(stopwords.words("english"))
		punc = set(string.punctuation)

		#Remove all stop words and punctuation from word list. 
		filtered_words = []
		for w in words_chopped:
			if w not in stop_words and w not in punc:
				filtered_words.append(w)
		total_words = len(filtered_words)
		
		#Determine the frequency of each filtered word and add the word and its frequency to a dictionary (key - word,value - frequency of that word)
		word_frequency = {}
		output_sentence = []

		for w in filtered_words:
			if w in word_frequency.keys():
				word_frequency[w] += 1.0 #increment the value: frequency
			else:
				word_frequency[w] = 1.0 #add the word to dictionary

		#Weighted frequency values - Assign weight to each word according to frequency and total words filtered from input:
		for word in word_frequency:
			word_frequency[word] = (word_frequency[word]/total_words)

		#Keep a tracker for the most frequent words that appear in each sentence and add the sum of their weighted frequency values. 
		#Note: Each tracker index corresponds to each original sentence.
		tracker = [0.0] * len(sentences_original)
		for i in range(0, len(sentences_original)):
			for j in word_frequency:
				if j in sentences_original[i]:
					tracker[i] += word_frequency[j]

		#Get the highest weighted sentence and its index from the tracker. We take those and output the associated sentences.
		
		for i in range(0, len(tracker)):
			
			#Extract the index with the highest weighted frequency from tracker
			index, value = max(enumerate(tracker), key = operator.itemgetter(1))
			if (len(output_sentence)+1 <= max_sentences) and (sentences_original[index] not in output_sentence): 
				output_sentence.append(sentences_original[index])
			if len(output_sentence) > max_sentences:
				break
			
			#Remove that sentence from the tracker, as we will take the next highest weighted freq in next iteration
			tracker.remove(tracker[index])
		
		sorted_output_sent = self.sort_sentences(sentences_original, output_sentence)
		return (sorted_output_sent)

	# @def sort_senteces:
	# From the output sentences, sort them such that they appear in the order the input text was provided.
	# Makes it flow more with the theme of the story/article etc..
	def sort_sentences (self, original, output):
		sorted_sent_arr = []
		sorted_output = []
		for i in range(0, len(output)):
			if(output[i] in original):
				sorted_sent_arr.append(original.index(output[i]))
		sorted_sent_arr = sorted(sorted_sent_arr)

		for i in range(0, len(sorted_sent_arr)):
			sorted_output.append(original[sorted_sent_arr[i]])
		print (sorted_sent_arr)
		return sorted_output





from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'arslanasdkjksdfhhhhfahsdjkhajksdfhj'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'  # SQLite database URI
db = SQLAlchemy(app)

app.secret_key = 'arslanasdkjksdfhhhh'  # Change this to a strong, random secret key

# Store user data in a dictionary (for demo purposes, you should use a database in a real app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)


@app.route('/templates', methods=['POST'])
def original_text_form():
    title = "Summarizer"
    text = request.form['input_text']  # Get text from HTML
    max_value = sent_tokenize(text)
    num_sent = int(request.form['num_sentences'])  # Get the number of sentences required in summary
    sum1 = summarize()
    summary = sum1.get_summary(text, num_sent)
    print(summary)
    return render_template("index.html", title=title, original_text=text, output_summary=summary,
                           num_sentences=max_value)




@app.route('/')
def homepage():
	return render_template("index.html", title = "Text Summarizer | FYP Project")
    	
@app.route('/summarizer', methods=['GET', 'POST'])
def summarizer():
    if 'username' in session:
        return render_template("summarizer.html", title = "Text Summarizer")
    else:
        return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            session['username'] = username
            return redirect(url_for('/summarizer'))

        return 'Invalid username or password'

    return render_template('login.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():

	
    if request.method == 'POST':
		
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(password, method='sha256')  # Hash the password

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return 'Username already exists, please choose another username.'

        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
		
        return redirect(url_for('login'))
		
    return render_template('signup.html',  title="Sign-up")

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))





if __name__ == "__main__":
    with app.app_context():  # Enter the application context
        db.create_all()  # Create the database tables
    app.run(debug=True)