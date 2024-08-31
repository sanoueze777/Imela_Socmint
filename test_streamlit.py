# DB
import sqlite3
import streamlit as st
import pandas as pd
import numpy as np
from streamlit_autorefresh import st_autorefresh
from io import BytesIO
from pyxlsb import open_workbook as open_xlsb
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
import matplotlib.pyplot as plt
from streamlit_option_menu import option_menu
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import nltk
from datetime import datetime
##########################################################################     refresh
# Run the autorefresh about every 2000 milliseconds (2 seconds) and stop
# after it's been refreshed 100 times.
count = st_autorefresh(interval=120000, limit=100, key="fizzbuzzcounter")

##########################################################################     hide watermark
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True) 

##########################################################################
conn = sqlite3.connect('socmint.db')
c = conn.cursor()
#st.set_option('deprecation.showPyplotGlobalUse', False)



def to_excel(df):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index=False, sheet_name='Sheet1')
    workbook = writer.book
    worksheet = writer.sheets['Sheet1']
    format1 = workbook.add_format({'num_format': '0.00'}) 
    worksheet.set_column('A:A', None, format1)  
    writer.save()
    processed_data = output.getvalue()
    return processed_data





# Functions
def create_table():
	c.execute('CREATE TABLE IF NOT EXISTS blogtable(author TEXT,title TEXT,article TEXT,postdate DATE)')

def add_data(author,title,article,postdate):
	c.execute('INSERT INTO blogtable(author,title,article,postdate) VALUES (?,?,?,?)',(author,title,article,postdate))
	conn.commit()

def view_all_notes():
	c.execute('SELECT * FROM posts ORDER BY Timestamp DESC')
	data = c.fetchall()
	return data

def view_all_titles():
	c.execute('SELECT DISTINCT title FROM posts')
	data = c.fetchall()
	return data


def get_blog_by_title(title):
	title = ('%'+title+'%',)
	c.execute('SELECT * FROM posts WHERE text LIKE ? ORDER BY Timestamp DESC',title)
	data = c.fetchall()
	return data
def get_blog_by_author(author):
	author = ('%'+author+'%',)
	c.execute('SELECT * FROM posts WHERE text LIKE ? ORDER BY Timestamp DESC',author)
	data = c.fetchall()
	return data

def delete_data(title):
	c.execute('DELETE FROM posts WHERE title="{}"'.format(title))
	conn.commit()









# Layout Templates
html_temp = """
<div style="background-color:{};padding:10px;border-radius:10px">
<h1 style="color:{};text-align:center;">MONITORING DES MEDIAS FACEBOOK </h1>
</div>
"""
title_temp ="""
<div style="background-color:#B2D9E2;padding:10px;border-radius:10px;margin:10px;box-shadow: 1px 1px 10px grey;">
<h4 style="color:white;text-align:center;">{}</h1>
<img src="https://www.w3schools.com/howto/img_avatar.png" alt="Avatar" style="vertical-align: middle;float:left;width: 50px;height: 50px;border-radius: 50%;" >
<h6>Post :{}</h6>
<br/>
<p style="text-align:justify">{}</p>
<br/> 
<a href={}>voir l'article sur facebook</a>
<br/> 
</div>
"""
article_temp ="""
<div style="background-color:#AEF1F4;padding:10px;border-radius:5px;margin:10px;box-shadow: 5px 10px;">
<h4 style="color:white;text-align:center;">{}</h1>
<h6>Post :{}</h6> 
<h6>Post Date: {}</h6>
<img src="https://www.w3schools.com/howto/img_avatar.png" alt="Avatar" style="vertical-align: middle;width: 50px;height: 50px;border-radius: 50%;" >
<br/>
<br/>
<p style="text-align:justify">{}</p>
</div>
"""
head_message_temp ="""
<div style="background-color:#B2D9E2;padding:10px;border-radius:5px;margin:10px;box-shadow: 1px 1px 10px grey;">
<h4 style="color:white;text-align:center;">{}</h1>
<img src="https://www.w3schools.com/howto/img_avatar.png" alt="Avatar" style="vertical-align: middle;float:left;width: 50px;height: 50px;border-radius: 50%;">
<h6>Post :{}</h6> 
<h6>{}</h6> 
<br/> 
<a href={}>voir l'article sur facebook</a>
</div>
"""
full_message_temp ="""
<div style="background-color:silver;overflow-x: auto; padding:10px;border-radius:5px;margin:10px;">
<p style="text-align:justify;color:black;padding:10px">{}</p>
</div>
"""







def main():
	"""MONITORING DES MEDIAS FACEBOOK"""
	st.sidebar.image("Armoiries-1.jpg", use_column_width=False)
	st.markdown(html_temp.format('royalblue','white'),unsafe_allow_html=True)

	#menu = ["Accueil","Rechercher","Statistiques"]
	#choice = st.sidebar.selectbox("Menu",menu)
	with st.sidebar:
		choice = option_menu(None,["Accueil", 'Rechercher',"Statistiques"], 
	icons=['house','list-task','gear'], default_index=0,styles={
        "nav-link-selected": {"background-color": "blue"},
    })
		

	if choice == "Accueil":
		st.subheader("Toutes les publications")
		result = view_all_notes()
		#print(f'result ======================== {result}')
		for i in result:
			b_author = i[7]
			b_link = i[4]
			b_article = str(i[1])#[:200]+'...'
			b_post_date = i[0]
			st.markdown(title_temp.format(b_author,b_article,b_post_date,b_link),unsafe_allow_html=True)

	elif choice == "Base de données":
		st.subheader("Toutes les publications")
		all_titles = [i[0] for i in view_all_titles()]
		postlist = st.sidebar.selectbox("View Posts",all_titles)
		post_result = get_blog_by_title(postlist)
		for i in post_result:
			b_author = i[0]
			b_title = i[1]
			b_article = i[2]
			b_post_date = i[3]
			st.text("Reading Time:{}".format(readingTime(b_article)))
			st.markdown(head_message_temp.format(b_title,b_author,b_post_date),unsafe_allow_html=True)
			st.markdown(full_message_temp.format(b_article),unsafe_allow_html=True)



	elif choice == "Add Posts":
		st.subheader("Add Articles")
		create_table()
		blog_author = st.text_input("Enter Author Name",max_chars=50)
		blog_title = st.text_input("Enter Post Title")
		blog_article = st.text_area("Post Article Here",height=200)
		blog_post_date = st.date_input("Date")
		if st.button("Add"):
			add_data(blog_author,blog_title,blog_article,blog_post_date)
			st.success("Post:{} saved".format(blog_title))	




	elif choice == "Rechercher":
		st.subheader("Rechercher les publications")
		search_term = st.text_input('Entrez le terme de recherche')
		search_choice = st.radio("Rechercher par",("contenu","auteur"))
		
		if st.button("Rechercher"):

			if search_choice == "contenu":
				article_result = get_blog_by_title(search_term)
			elif search_choice == "auteur":
				article_result = get_blog_by_author(search_term)
                
			for i in article_result:
				b_author = i[7]
				b_link = i[4]
				b_article = str(i[1])#[:200]+'...'
				b_post_date = i[0]
				#st.text("Reading Time:{}".format(readingTime(b_article)))
				st.markdown(head_message_temp.format(b_author,b_article,b_post_date,b_link),unsafe_allow_html=True)
				#st.markdown(full_message_temp.format(b_article),unsafe_allow_html=True)




	elif choice == "Statistiques":
		st.subheader("Statistiques")
		period = st.slider(
        "Sélectionnez la période:",
        value=(datetime(2022, 1, 1, 9, 30), datetime(2023, 2, 10, 9, 30)), format="MM/DD/YY - hh:mm")
		result = view_all_notes()
		clean_db = pd.DataFrame(result,columns=["Date","Texte","post_id","Nombre de commentaires","url du post","auteur","image","source","polarité","subjectivité"])
		new_df = clean_db
		start = period[0]
		end = period[1]
		print(start)
		print(end)
		for i in range(len(new_df)):
			if new_df.loc[i,'Date']==None:
				new_df = new_df.drop(i, axis =0)
			else:
				comp =datetime.strptime(new_df.loc[i,'Date'], '%Y-%m-%d %H:%M:%S')
				if comp<start:
					new_df = new_df.drop(i, axis =0)
				if end<comp:
					new_df = new_df.drop(i, axis =0) 
		if st.checkbox("Métriques"):
			
			new_df['Taille_du_post'] = new_df['Texte'].str.len()
			df_xlsx = to_excel(new_df)
			st.download_button(label='📥 Télécharger en format Excel',
                                data=df_xlsx ,
                                file_name= 'publications_fb.xlsx')
			st.dataframe(new_df)


			st.subheader("nombre de posts par média")
			new_df["source"].value_counts().plot(kind='bar')
			st.pyplot()

			st.subheader("proportion des commentaires par média")
			new_df['source'].value_counts().plot.pie(autopct="%1.1f%%")
			st.pyplot()

		if st.checkbox("Nuage de mots"):
			# text = new_df['Articles'].iloc[0]
			text = ','.join(new_df['Texte'])
			#nltk.download('stopwords')
			#nltk.download('punkt')
			stop_words = set(stopwords.words('french'))
			word_tokens = word_tokenize(text)
			# converts the words in word_tokens to lower case and then checks whether
			#they are present in stop_words or not
			filtered_sentence = [w for w in word_tokens if not w.lower() in stop_words]
			print(filtered_sentence)
			#text = pd.to_numeric(text.astype(float).str[:-1], errors='coerce')
			filtered_sentence = ','.join(filtered_sentence)
			filtered_sentence = filtered_sentence.replace('Show','')
			filtered_sentence = filtered_sentence.replace('Play','')
			filtered_sentence = filtered_sentence.replace('Video','')
			filtered_sentence = filtered_sentence.replace('cliquant','')
			filtered_sentence = filtered_sentence.replace('ici','')
			filtered_sentence = filtered_sentence.replace('minutes','')
			filtered_sentence = filtered_sentence.replace('lecture','')
			filtered_sentence = filtered_sentence.replace('Like','')
			filtered_sentence = filtered_sentence.replace('cette','')
			filtered_sentence = filtered_sentence.replace('plus','')
			filtered_sentence = filtered_sentence.replace('pays','')
			wordcloud = WordCloud().generate(filtered_sentence)
			plt.imshow(wordcloud,interpolation='bilinear')
			plt.axis("off")
			st.pyplot()
		

if __name__ == '__main__':
	main()
