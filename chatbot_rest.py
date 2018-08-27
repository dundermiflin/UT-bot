import pandas as pd
import numpy as np
from nltk.stem.snowball import SnowballStemmer
import webbrowser as wb
import getpass
import requests
import json
from google import google

cust_id=''
user="641052K001"
password=''
URL="API SERVICE HERE"
HEADER= HEADER= {"Content-Type":"application/json", "Accept":"text/plain"}
service=["CISTSALESPERFORMANCEMTD","CISTSALESLAST3MONTHS","CISTSALESDAYWISE"]
response=["Sales performance till date : ","Data for last 3 months: ","Today's sales data: "]
ss= SnowballStemmer("english")

df= pd.read_excel('faqrest.xlsx')
A=[]
Q=[]

for i in df.index:														#Creating a dataframe to hold the data temporarily
	Q.append(df['Q'][i].encode('utf-8').lower())
	A.append(df['A'][i].encode('utf-8'))

vocab=[]

for q in Q:
	temp_words=q.split(' ')
	for i in range(len(temp_words)):
		temp_words[i]=ss.stem(temp_words[i]).encode('utf-8')
	for i in range(len(temp_words)):
		temp_words[i]=ss.stem(temp_words[i]).encode('utf-8')			#Some words require additional stemming, hence they must be passes into the stemmer again
	vocab.extend(temp_words)											#Generating vocabulary by appending words
	temp_bigrams=[]
	for i in range(0,len(temp_words)-1):								#Adding bigrams to vocabulary for better context extraction
		temp_bigrams.append(' '.join([temp_words[i],temp_words[i+1]]))
	if len(temp_words)==1:
		temp_bigrams.append(temp_words[0])
	vocab.extend(temp_bigrams)

vocab= list(set(vocab))

faq_len= len(Q)


def cosine(a,b):
	mod_a=np.sum(a*a)**(0.5)
	mod_b=np.sum(b*b)**(0.5)
	if mod_b==0 or mod_a==0:
		return 0
	dot= np.sum(a*b)
	val= mod_a*mod_b
	return dot/val

def gen_matrix():

	matrix=[]

	for i in range(len(Q)):												# Generation Feature Matrix	
		matrix.append(np.array([0]*len(vocab)))
		words=Q[i].split(' ')
		for j in range(len(words)):
			words[j]=ss.stem(words[j]).encode('utf-8')
		for j in range(len(words)):
			words[j]=ss.stem(words[j]).encode('utf-8')
		bigrams=[]
		for j in range(0,len(words)-1):
			bigrams.append(' '.join([words[j],words[j+1]]))
		if len(words)==1:
			bigrams.append(words[0])
		features=[bg for bg in bigrams]
		features.extend(words)
		features= list(set(features))
		for f in features:
			if f in vocab:
				matrix[i][vocab.index(f)]=1
	
	return (vocab, np.array(matrix))


def bot_response(new_q,matrix):
	'''
		Function to extract bot's response to a question.

		This function first runs the query through the same process as the Questions.
		This is followed by calculating cosine distance between the query feature vector and vectors in
		the feature matrix. The appropriate response is selected and returned as a string.
	'''
	if new_q[-1]=='?':
		new_q= new_q[:-1]

	new_q= new_q.lower()

	q_words= new_q.split(' ')
	
	for i in range(len(q_words)):
		q_words[i]= ss.stem(q_words[i]).encode('utf-8')

	q_bigrams=[]	
	for i in range(0,len(q_words)-1):
		q_bigrams.append(' '.join([q_words[i],q_words[i+1]]))
	if len(q_words)==1:
		q_bigrams.append(q_words[0])
	q_features= [bg for bg in q_bigrams]
	q_features.extend(q_words)
	q_features=list(set(q_features))
	

	new_v=np.zeros(len(vocab))
	for f in q_features:
		if f in vocab:
			new_v[vocab.index(f)]=1


	max_cos=0
	index =-1

	for i in range(len(matrix)):
		cos= cosine(new_v,matrix[i])
		if cos>max_cos:
			max_cos= cos
			index=i

	if index!=-1:
		if index>=faq_len-3:
			option= index+3-faq_len
			PARAMS= {"serviceName":service[option],"USERID":user}										#Parameters for REST API
			response= requests.post(url=URL, data= json.dumps(PARAMS), headers= HEADER, timeout=2)
			if response.ok==True:
				js= response.json()
				if u"selectResponseIn" in js:
					dicts= js[u"selectResponseIn"]														# Parsing the JSON output.
					all_responses=[]
					for d in dicts:
						for x in d:
							all_responses.append(x.encode('utf-8')+": "+ str(d[x]).encode('utf-8')+'\n')
						all_responses.append('\n')
					print(all_responses)
					return ' '.join(all_responses)
				else:
					return "Sorry, the data could not be optained. Try something else!"
			else:
				return "Sorry, the data could not be optained. Try something else!"
		else:
			return A[index]
	else:
		google_results= google.search("Ultratech "+new_q)
		resp= "We couldn't find what you were looking for. Here are a few links that might help:\n"			# If no appropriate response is found, the bot does a google search with Ultratech+ the query
		for result in google_results[:3]:
			resp+=(result.link+"\n")
		return resp+"\nPlease try another question"



