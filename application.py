from flask import Flask,request,render_template,jsonify
from flask_cors import CORS,cross_origin
import requests
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as uReq
import pymongo
import base64
app = Flask(__name__)

@app.route('/',methods=["GET"])
@cross_origin()
def homePage():
    return render_template("index.html")



@app.route('/review',methods=["GET","POST"])
@cross_origin()
def index():

    if request.method == 'POST':
        try:
            searchString = request.form['content'].replace(" ","")
            flipkart_url = "https://www.flipkart.com/search?q=" + searchString
            uClient = uReq(flipkart_url)
            flipkart_page = uClient.read()
            uClient.close()
            flipkart_html = bs(flipkart_page,'html.parser')
            bigboxes = flipkart_html.findAll("div", {"class": "_1AtVbE col-12-12"})
            del bigboxes[0:3]
            box = bigboxes[0]
            product_link = "https://www.flipkart.com" + box.div.div.div.a['href']
            prodreq = requests.get(product_link)
            prodreq.encoding = 'utf-8'
            prodhtml = bs(prodreq.text,'html.parser')
            print(prodhtml)
            commentboxes = prodhtml.find_all('div', {'class': "_16PBlm"})
            filename = searchString + '.csv'
            fw = open(filename, "w")
            headers = "Product, Customer Name, Rating, Heading, Comment \n"
            fw.write(headers)
            reviews = []
            for comment in commentboxes:
                try:
                    name = comment.div.div.find_all('p', {'class': '_2sc7ZR _2V5EHH'})[0].text
                except:
                    name = 'No Name'

                try:
                     #rating.encode(encoding='utf-8')
                    rating = comment.div.div.div.div.text


                except:
                    rating = 'No Rating'

                try:
                    #commentHead.encode(encoding='utf-8')
                    commentHead = comment.div.div.div.p.text

                except:
                    commentHead = 'No Comment Heading'
                try:
                    comtag = comment.div.div.find_all('div', {'class': ''})
                    #custComment.encode(encoding='utf-8')
                    custComment = comtag[0].div.text
                except Exception as e:
                    print("Exception while creating dictionary: ",e)

                
                mydict = {"Product": searchString, "Name": name, "Rating": rating, "CommentHead": commentHead,
                          "Comment": custComment}

                reviews.append(mydict)
                
            client = pymongo.MongoClient(f"mongodb+srv://sid:{base64.b64decode('cHdza2lsbHM=').decode('utf-8')}@cluster0.vd7avyx.mongodb.net/?retryWrites=true&w=majority")
            db = client['scrapping_password']
            collection = db['flipkart_scrape_data']
            collection.insert_many(reviews)

                
            return render_template("results.html",reviews = reviews[0:(len(reviews)-1)])
        
        except Exception as e:
            print('The Exception message is: ',e)
            return 'something is wrong'
    else:
        return render_template('index.html')

if __name__ == "__main__":
    app.run(host='127.0.0.1',port=8000,debug=True)