import sqlite3
from datetime import datetime
from facebook_scraper import get_posts
import pandas as pd
import shutil
import time
import re
from textblob import Blobber
from textblob_fr import PatternTagger, PatternAnalyzer
#c.execute(f"INSERT INTO sources VALUES (?,?)",(source,0))
def add_sentiment():
    conn = sqlite3.connect('socmint.db')
    c = conn.cursor()
    c.execute('SELECT * FROM posts')
    data = c.fetchall()
    for i in range(len(data)):
        firstDelPos=None
        secondDelPos=None
        first=None
        second=None


        blob2=data[i][1]
        if data[i][8]==None:
            firstDelPos=blob2.find('"') # get the position of [
            secondDelPos=blob2.find('"',firstDelPos+1,-1) # get the position of ]
            first = blob2.find('«')
            second = blob2.find('»',firstDelPos+1,-1)
            if firstDelPos!=None and secondDelPos!=None:
                try:
                    blob2 = blob2.replace(blob2[firstDelPos:secondDelPos], "")
                except:
                    pass
            if first!=None and second!=None:
                try:
                    blob2 = blob2.replace(blob2[first:second], "")
                except:
                    pass
            blob2 = blob2.replace('Show','')
            blob2 = blob2.replace('Play','')
            blob2 = blob2.replace('Video','')
            blob2 = blob2.replace('cliquant','')
            blob2 = blob2.replace('ici','')
            blob2 = blob2.replace('minutes','')
            blob2 = blob2.replace('lecture','')
            blob2 = blob2.replace('Like','')
            blob2 = blob2.replace('cette','')
            blob2 = blob2.replace('plus','')
            blob2 = blob2.replace('pays','')
            blob2 = blob2.replace('more','')

            print('----------------------------------------------------------------------------------------------')
            print(blob2)

            tb = Blobber(pos_tagger=PatternTagger(), analyzer=PatternAnalyzer())
            blob2 = tb(blob2)
            blob2 = blob2.sentiment
            print(blob2)

            c.execute("""UPDATE posts SET polarity = ? WHERE rowid = ?""",(blob2[0],i))
            c.execute("""UPDATE posts SET subjectivity = ? WHERE rowid = ?""",(blob2[1],i))
    conn.commit()
    conn.close()
            
    
def scrape_and_save(source):

    print(f'++++++++++++++++++++++Checking {source}')
    for posts in get_posts(source, pages=5, options={"comments": False,"allow_extra_requests": False}):
        print(f'---- New post')
        add = True
        post_id = str(posts['post_id'])
        conn = sqlite3.connect('socmint.db')
        c = conn.cursor()
        c.execute(f"SELECT * FROM posts")
        current_table = c.fetchall()
        
        for i in range(len(current_table)):
            #print(f'-----------------------------------------------------------------------------{current_table[i][2]}')
            #print(f'-----------------------------------------------------------------------------{post_id}')
            if str(current_table[i][2]) == str(post_id):
                add = False
                print(f'---------------add is {add}')



        if add == True:
            time = posts['time']
            #time = int(datetime.timestamp(posts['time']))
            #print(time)
            text = str(posts['text'])
            last_space =0
            for j in range(len (text)):
                if text[j]==" ":
                    last_space = j
                    print(f'last_space: {last_space}')
                if 20<j-last_space:
                    break
            text = text[:last_space]
            #print(text)
            """        
            text = text.replace(' ', '_')
            text = text.replace("'", '_appostr_')
            text = text.replace(":", '_eq_')
            text = text.replace("/", '_slash_')
            """
            post_id = str(posts['post_id'])
            #print(post_id)

            post_comments = int(posts['comments'])

            #print(post_comments)
            post_url = str(posts['post_url'])
            """
            post_url = post_url.replace(' ', '_')
            post_url = post_url.replace("'", '_appostr_')
            post_url = post_url.replace(":", '_eq_')
            post_url = post_url.replace("/", '_slash_')
            """
            #print(post_url)

            author = str(posts['username'])
            """
            author = author.replace(' ', '_')
            author = author.replace("'", '_appostr_')
            author = author.replace(":", '_eq_')
            author = author.replace("/", '_slash_')
            """
            author = author[:20]
            #print(author)
            image = str(posts['image'])
            """
            image = image.replace(' ', '_')
            image = image.replace("'", '_appostr_')
            image = image.replace(":", '_eq_')
            image = image.replace("/", '_slash_')
            """
            #print(image)
            if image == None:
                image ="none"
            target = str(source)
            #c.execute(f'SELECT * FROM {table} WHERE Timestamp=? AND Text=? AND post_id=? AND post_comments=? AND post_url=? AND author=? AND image=?', (time,text,post_id,post_comments,post_url,author,image))
            if 0<len(text):
                a = None
                b = None
                c.execute(f"INSERT INTO posts VALUES (?,?,?,?,?,?,?,?,?,?)",(time,text,post_id,post_comments,post_url,author,image,target,a,b))
            conn.commit()

                    # close the connection
            conn.close()
    
    
    
    
def scrape_forever():
    while True :
        try:
            while True:
                
                original = r'to_scrape.csv'
                target = r'to_scrape_copy.csv'
                shutil.copyfile(original, target)


                status = pd.read_csv('to_scrape.csv')
                to_scrape = status['to_scrape'].to_list()
                print(to_scrape)
                for i in range(len(to_scrape)):                
                    scrape_and_save(to_scrape[i])
                    time.sleep(600)
                time.sleep(3600)
       
        except:
            pass

scrape_forever()