from flask import Flask, jsonify, request
from flask_cors import CORS
from joblib import load
from bs4 import BeautifulSoup
import requests
import csv
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
import pickle
import PyPDF2
from io import BytesIO


presence_classifier = load(r"C:\Users\PARUL\Desktop\badal dia\urgency_model.pkl")
presence_vect = load(r"C:\Users\PARUL\Desktop\badal dia\vector.pkl")
category_classifier = load(r'C:\Users\PARUL\Desktop\badal dia\category_classifier.joblib')
category_vect = load(r'C:\Users\PARUL\Desktop\badal dia\category_vectorizer.joblib')
pipeline = pickle.load(open(r'C:\Users\PARUL\Desktop\badal dia\logistic_regression_model.pkl', 'rb'))
tfd= pickle.load(open(r'C:\Users\PARUL\Desktop\badal dia\reviewkatldf.pkl', 'rb'))
tandc_model=pickle.load(open(r'C:\Users\PARUL\Desktop\badal dia\tandc.pkl', 'rb'))
tandc_vector_form=pickle.load(open(r'C:\Users\PARUL\Desktop\badal dia\tandcvector.pkl', 'rb'))


app = Flask(__name__)
CORS(app)
def get_spoc(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    hrefs = []

    sponcered = soup.find_all("div", class_="_4HTuuX")
    for spoc in sponcered:
        if spoc.get_text() == "Sponsored":
            links = spoc.find_next('a', class_="s1Q9rs")
            if links:
                href = links.get('href')
                hrefs.append(href)

    return hrefs
def find_prices(url):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        price_elements = soup.find(['span', 'div', 'ul', 'li'],
                                       class_=["sellingPrice", "Price", "price", 'price_div', 'pro-price',
                                               "_30jeq3 _16Jk6d", ])  # Customize the class based on the website's structure
        prices = price_elements.get_text() 
        #print(prices)
        return prices
    return None
def make_request_with_retry(url):
    retries = Retry(total= 3, backoff_factor= 0.5, status_forcelist=[503, 408])
    adapter = HTTPAdapter(max_retries=retries)
    session = requests.Session()
    session.mount('http://', adapter)
    session.mount('https://', adapter)

    try:
        response = session.get(url)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx and 5xx)

        # Continue processing the response if successful
        return response
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None
def review_dhundo(url):
    response = response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    reviews = soup.find_all('div', class_ = "t-ZTKy")
    
    review = [re.get_text() for re in reviews]

    return review

def next_page_link(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    pages = soup.find('nav', class_= 'yFHi8N')
    next_page = [a.get('href') for a in pages]
    return next_page

def write_to_csv(filepath, list):
    with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
    # with open(filepath, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Review', 'Prediction'])
        for string in list:
            writer.writerow([string])
def read_csv(filename):
    data = []
    with open(filename, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        next(reader, None)
        for row in reader:
            data.append(row)
    return data

def predict_reviews(data):
    predictions = []
    for r in data:
        # Check if the input is a list of strings
        if isinstance(r, list) and all(isinstance(item, str) for item in r):
            # Transform the list of strings using TF-IDF vectorizer
            tfidf_data = tfd.transform(r)
        elif isinstance(r, str):
            # If the input is a single string, transform it to a list and then transform
            tfidf_data = tfd.transform([r])
        else:
            raise ValueError("Input data must be a string or a list of strings")
        
        # Predict using the trained model
        lr_pred = pipeline.predict(tfidf_data)
        predictions.append(lr_pred[0])  # Assuming pipeline.predict() returns a single prediction
    return predictions

def add_column(existing_data, new_column_data):
    if len(existing_data) != len(new_column_data):
        raise ValueError("Lengths of existing data and new column data must match")
    updated_data = []
    for i in range(len(existing_data)):
        updated_data.append(existing_data[i] + [new_column_data[i]])
    return updated_data

def write_csv(filename, updated_data):
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(updated_data)
def output(predictions):
    or_count = 0
    cg_count = 0
    size = len(predictions)
    print(len(predictions))
    for i in predictions:
        if i == 1:
            cg_count += 1
        else:
            or_count += 1
    thr = size *0.40
    print(thr)
    threshold = int(thr)
    print("Computer Generated: ", cg_count)
    print("Original: ", or_count)
    print("Percentage of Computer generated:", threshold,"%")
    sahi = "Product Authentic"
    galat = "Product NOT Authentic"
    if cg_count <= threshold:
        return sahi
    else:
        return galat
@app.route('/', methods=['POST'])
def main():
    if request.method == 'POST':
        output = []
        data = request.get_json().get('tokens')

        for token in data:
            result = presence_classifier.predict(presence_vect.transform([token]))
            if result == 'Dark':
                cat = category_classifier.predict(category_vect.transform([token]))
                output.append(cat[0])
            else:
                output.append(result[0])

        dark = [data[i] for i in range(len(output)) if output[i] == 'Dark']
        for d in dark:
            print(d)
        #print()
        print(len(dark))
        message = '{ \'result\': ' + str(output) + ' }'
        print(message)
        url = "https://www.flipkart.com/computers/storage/ssd/pr?sid=6bo%2Cjdy%2Cdus&p%5B%5D=facets.brand%255B%255D%3DSanDisk&sort=popularity&param=34567&hpid=cO5m4Oh8Ao_ji8Ag-0t33ap7_Hsxr70nj65vMAAFKlc%3D&ctx=eyJjYXJkQ29udGV4dCI6eyJhdHRyaWJ1dGVzIjp7InZhbHVlQ2FsbG91dCI6eyJtdWx0aVZhbHVlZEF0dHJpYnV0ZSI6eyJrZXkiOiJ2YWx1ZUNhbGxvdXQiLCJpbmZlcmVuY2VUeXBlIjoiVkFMVUVfQ0FMTE9VVCIsInZhbHVlcyI6WyJGcm9tIOKCuTUsNzk5Il0sInZhbHVlVHlwZSI6Ik1VTFRJX1ZBTFVFRCJ9fSwiaGVyb1BpZCI6eyJzaW5nbGVWYWx1ZUF0dHJpYnV0ZSI6eyJrZXkiOiJoZXJvUGlkIiwiaW5mZXJlbmNlVHlwZSI6IlBJRCIsInZhbHVlIjoiQUNDR1NZWkVaS0pZRVFYQyIsInZhbHVlVHlwZSI6IlNJTkdMRV9WQUxVRUQifX0sInRpdGxlIjp7Im11bHRpVmFsdWVkQXR0cmlidXRlIjp7ImtleSI6InRpdGxlIiwiaW5mZXJlbmNlVHlwZSI6IlRJVExFIiwidmFsdWVzIjpbIlNhbmRpc2sgRXh0cmVtZSBQb3J0YWJsZSJdLCJ2YWx1ZVR5cGUiOiJNVUxUSV9WQUxVRUQifX19fX0%3D"
        ads = get_spoc(url)
        true_links = ["https://www.flipkart.com" + ad for ad in ads]
        products_with_prices = []
        for u in true_links:
         prices = find_prices(u)
         name = u.split('/')
        #  product_name = ' '.join(name[3].split("-"))
        #  products_with_prices[product_name] = prices
         products_with_prices.append(prices)
         #print(prices)  # Print the prices here
        # mini=products_with_prices[0]
        # print(mini)
        # s="{}".format(mini)
        # x= '{ \'result\': \" '+str(products_with_prices) +  '\" }'
        # print(x)
        # x=x.replace("\'",'"')
        # print(x)
        # print("the x:",x)
        # y=jsonify(x)
        # print("y is",y)
        json = jsonify(message)
        return json
@app.route('/authenticity', methods=['OPTIONS'])
def authentic():
    if request.method == 'OPTIONS':
     #Sample URL
     url = "https://www.flipkart.com/sandisk-e30-800-mbs-window-mac-os-android-portable-type-c-enabled-usb-3-2-1-tb-external-solid-state-drive-ssd/product-reviews/itmf25597135f901?pid=ACCGSYZEZKJYEQXC&lid=LSTACCGSYZEZKJYEQXC4H2UTK&marketplace=FLIPKART"
    # make_request_with_retry(url)
     filepath = r"C:\Users\PARUL\Desktop\badal dia\example.csv"
     href = next_page_link(url)
     us = []
     all_review = []
     for ref in href:
        reviews = review_dhundo("https://www.flipkart.com" + ref)
        us.append(reviews)
     for i in us:
      for u in i:
       u = u.replace("READ MORE", " ")
       all_review.append(u)
    filepath = r'C:\Users\PARUL\Desktop\badal dia\example.csv'
    write_to_csv(filepath, all_review)
    # for p in all_review:
        # print(p)
    filepath = r'C:\Users\PARUL\Desktop\badal dia\example.csv'
    data = read_csv(filepath)
    predictions = predict_reviews(data)
    print(predictions)
    updated_data = add_column(data, predictions)
    write_csv(filepath,updated_data)
    m=output(predictions)
    print(m)
    mess = str(m)
    auth = jsonify(mess)
    print(auth)
    return auth

@app.route('/fetch_prices',methods=['POST'])
def fetch_product_prices():
    if request.method == 'POST':
     #Sample URL
     url = "https://www.flipkart.com/computers/storage/ssd/pr?sid=6bo%2Cjdy%2Cdus&p%5B%5D=facets.brand%255B%255D%3DSanDisk&sort=popularity&param=34567&hpid=cO5m4Oh8Ao_ji8Ag-0t33ap7_Hsxr70nj65vMAAFKlc%3D&ctx=eyJjYXJkQ29udGV4dCI6eyJhdHRyaWJ1dGVzIjp7InZhbHVlQ2FsbG91dCI6eyJtdWx0aVZhbHVlZEF0dHJpYnV0ZSI6eyJrZXkiOiJ2YWx1ZUNhbGxvdXQiLCJpbmZlcmVuY2VUeXBlIjoiVkFMVUVfQ0FMTE9VVCIsInZhbHVlcyI6WyJGcm9tIOKCuTUsNzk5Il0sInZhbHVlVHlwZSI6Ik1VTFRJX1ZBTFVFRCJ9fSwiaGVyb1BpZCI6eyJzaW5nbGVWYWx1ZUF0dHJpYnV0ZSI6eyJrZXkiOiJoZXJvUGlkIiwiaW5mZXJlbmNlVHlwZSI6IlBJRCIsInZhbHVlIjoiQUNDR1NZWkVaS0pZRVFYQyIsInZhbHVlVHlwZSI6IlNJTkdMRV9WQUxVRUQifX0sInRpdGxlIjp7Im11bHRpVmFsdWVkQXR0cmlidXRlIjp7ImtleSI6InRpdGxlIiwiaW5mZXJlbmNlVHlwZSI6IlRJVExFIiwidmFsdWVzIjpbIlNhbmRpc2sgRXh0cmVtZSBQb3J0YWJsZSJdLCJ2YWx1ZVR5cGUiOiJNVUxUSV9WQUxVRUQifX19fX0%3D"
     ads = get_spoc(url)
     true_links = ["https://www.flipkart.com" + ad for ad in ads]
     products_with_prices = []
     for u in true_links:
         prices = find_prices(u)
         prices = prices[1: ]
         name = ' '.join(u.split('/')[3].split("-"))

         product_info = {"name": name, "price": prices}

        #  product_name = ' '.join(name[3].split("-"))
        #  products_with_prices[product_name] = prices
         products_with_prices.append(product_info)
        #  formatted_response = "\n".join([f"{item['name']}: {item['price']}" for item in products_with_prices])

     x= products_with_prices
    #  message = '{ \'result\': ' + str(output) + ' }'
    #  print(x)
    #  x=x.replace("\'",'"')
    #  print(x)
     print("the x:",x)
     y=jsonify(x)
     print("y is",y)
     # json = jsonify(m)
     return y
@app.route('/tandc',methods=['POST'])
def tandc():
    if request.method == 'POST':
        #Sample URL
        url = "https://www.starhealth.in/accident-insurance/family/"
        hrefs = []
        
        # Scrape the website to get the link
        response = requests.get(url)
        soup = BeautifulSoup(response.content, "html.parser")
        a_tag = soup.find_all('div', class_='health-insurance-features_custom-card__qsyt5')

        # Extract the href attribute
        for tag in a_tag:
            a =  tag.find('a')
            href = a.get("href")
            hrefs.append(href)

        for h in hrefs:
            if 'PolicyClause' in h:
                link = h
                print(link)
                print(type(link))
                break

        # Extract text from the PDF
        text = extract_text_from_pdf_url(link)

        # Now 'text' contains the extracted text from the PDF.
        # You can do further processing or print it as needed.

        print(text)

        return "Text extraction completed."

def extract_text_from_pdf_url(pdf_url):
    # Download the PDF file
    response = requests.get(pdf_url)
    response.raise_for_status()  # Raise an exception if download fails
    
    # Open the PDF file from the response content
    pdf_file = BytesIO(response.content)
    
    # Extract text from the PDF file
    text = ""
    reader = PyPDF2.PdfReader(pdf_file)
    for page_number in range(len(reader.pages)):
        page = reader.pages[page_number]
        text += page.extract_text()
    
    return text
if __name__ == '__main__':
    app.run(threaded=True, debug=True)
