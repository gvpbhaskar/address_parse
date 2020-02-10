"""
Routes and views for the flask application.
"""

from datetime import datetime
from flaskwebapp import app
import os
from flask import Flask, render_template, request, jsonify,make_response
import pandas as pd
from postal.parser import parse_address
import re
import numpy as np
# creating and saving some model

app = Flask(__name__)

@app.route('/isAlive/')
def index():
    return "true"

@app.route("/",methods=['GET','POST'])
def home():
    if(request.method == 'GET'):
        data = {
        'status' : 'success',
        'version': "v0.0.1",
        'message': 'Address Parsing API',
        'author' : 'Engineering Innovation'
        }
        return make_response(jsonify(data), 200)

    else:
        data = {
        'status' : 'error',
        'message': 'HTTP method not allowed'
        }
        return make_response(jsonify(data), 200)



@app.route('/parse/', methods=['POST','GET'])
def get_prediction():
    feature = request.args.get('f')
    if len(feature)> 0:
        pred = address_parse(feature)
        return jsonify({"status" : "success", "Parsed Address": pred}) #render_template("Result",address_match=address_match)
    else:
        return jsonify({"status" : "failed ", "Message": "Got empty input"})

def address_parse(mystr):
	final_lst=[]
	mystr = mystr.replace('\n',',')
	st = re.sub('[^a-zA-Z0-9 \@\:\.]', ' ', str(mystr))
	token = st.split(' ')
	print(token)
	s=' '
	flag=0
	for i in range(len(token)):
		if(token[i].find('@')!=-1):
			#print(token[i])
			token.remove(token[i])
			break
		#print(token[i])
		#token[i] = re.sub('[^a-zA-Z]','',token[i])
		if(token[i].lower() in ['email','email:','tel','tel.','tel:','fax','fax:','uen','uen:','tax','phone','phone:','vat','t:','contact','tin','zip','ein'] ):
			s = s.join(token[0:i])
			print(s)
			flag=1
			break
	l = len(token)-1
	#for j in range(l,0,-1):
		#if token[j]:
			#if token[j].isdigit():
				#token.remove(token[j])
	if flag==0:
		s =s.join(token)
	print("final String: " + s)
	op= parse_address(s)
	print(op)
	final_lst.append(op)

	df1 = pd.DataFrame(final_lst)
	print(df1.shape)
	df1.to_csv('out_put.txt',index=False)

	data=pd.DataFrame(columns=['house','housenumber','building','road','suburb','city','citydistrict','state','statedistrict','country','postcode'],index= range(1))
	data['country']=data.country.replace(np.nan,'',regex = True)
	data['building']=data.building.replace(np.nan,'',regex = True)
	data['city']=data.city.replace(np.nan,'',regex = True)
	data['state']=data.state.replace(np.nan,'',regex = True)
	data['house']=data.house.replace(np.nan,'',regex = True)
	data['housenumber']=data.housenumber.replace(np.nan,'',regex = True)
	data['road']=data.road.replace(np.nan,'',regex = True)
	data['suburb']=data.suburb.replace(np.nan,'',regex = True)
	data['citydistrict']=data.citydistrict.replace(np.nan,'',regex = True)
	data['statedistrict']=data.statedistrict.replace(np.nan,'',regex = True)
	data['postcode']=data.postcode.replace(np.nan,'',regex = True)

	df_ctry = pd.read_csv('country_addvers.txt',sep=',')
	for i in range(df1.shape[0]):
		for j in df1.columns:
			st = re.sub('[^a-zA-Z0-9\,\ \.]', '', str(df1[j][i]))
			if st!='nan':
				st = st.replace("'","")
				lst = st.split(',')
				if len(lst) > 1:
					if(lst[1].strip() in data.columns):
						if data.loc[i][lst[1].strip()] =='':
							data.loc[i][lst[1].strip()] = lst[0]
							ctry = lst[0].strip().replace('.','')
							if lst[1].strip()=='country' and len(ctry) ==2:
								#print(ctry)
								data.loc[i][lst[1].strip()] = df_ctry.loc[df_ctry['Abbrev'] == ctry].Country.values[0]
						elif data.loc[i][lst[1].strip()] !='':
							data.loc[i][lst[1].strip()] = data.loc[i][lst[1].strip()] + " | " + lst[0]
					elif lst[1].strip() not in data.columns:
						data[lst[1].strip()]=''
						data.loc[i][lst[1].strip()] = lst[0]
	df_cities = pd.read_csv('world-cities.txt',sep=',')
	#data.to_csv('first_data.txt',index=False)
	for i in range(data.shape[0]):
		st =str(data['house'][i])
		if st.find('limited')>0  :
			st = re.sub('limited', 'limited#', st)
			token = st.split('#')
			data['house'][i] = token[0]
			data['building'][i] = token[1]
		if st.find('ltd')>0:
			st = re.sub('ltd', 'ltd#', st)
			token = st.split('#')
			data['house'][i] = token[0]
			data['building'][i] = token[1]
		if st.find('sdn bdh') >0:
			st = re.sub('sdn bdh', 'sdn bdh#', st)
			token = st.split('#')
			data['house'][i] = token[0]
			data['building'][i] = token[1]
		if st.startswith('pt.') or st.startswith('pt '):
			if len(str(data['country'][i])) ==0 :
				data['country'][i]='indonesia'
		if data['country'][i]=='':
			if data['city'][i]!='':
				city=str(data['city'][i].strip().lower())
				state=str(data['state'][i].strip().lower())
				#print('City: '+ city + ' STate : ' +state )
				try:
					if city!='':
						if df_cities.loc[df_cities['name'] == city].country.values[0] !='' :
							data['country'][i] = df_cities.loc[df_cities['name'] == city].country.values[0]
							print(data['country'][i])
				except IndexError:
					print("An error occurred City name")
			if data['state'][i]!='':
				try:
					if state!='':
						if df_cities.loc[df_cities['name'] == state].country.values[0] !='' :
							data['country'][i] = df_cities.loc[df_cities['name'] ==state].country.values[0]
							print(data['country'][i])
				except IndexError:
					print("An error occurred state name")
	#data.to_csv('data.txt',index=False)
	x = data.loc[0].to_string(header=False,index=False).split('\n')
	vals = [' '.join(ele.split()) for ele in x]
	fst = ' '.join(vals)
	return fst