import time
import speech_recognition as sr
import pyttsx3
import pyaudio
import pandas as pd
import spacy
from nltk.translate import bleu
from nltk.translate.bleu_score import SmoothingFunction

smoothie = SmoothingFunction().method4

listener = sr.Recognizer()
player = pyttsx3.init()
voice = player.getProperty('voices')[0]
player.setProperty('voice', voice.id)


player.setProperty('rate', 135)


def listen():
    with sr.Microphone() as input_device:
        t="Any Questions?"
        print(t)
        print()
        player.say(t)
        player.runAndWait()
        voice_content = listener.listen(input_device)
        time.sleep(3)
        text_command = listener.recognize_google(voice_content)
        text_command = text_command.lower()
        print(text_command)

        return text_command



def load_dataset(filename):
    reader=pd.read_csv(filename).to_dict('records')
    dataset = []
    seen_names = []
    for row in reader:
        # if 'Name' in row and 'Rate' in row and 'Category' in row and 'QTY' in row and row['Qty'] == '1' and row['name'] not in seen_names:
        if row['Name'] not in seen_names:
           if row["Qty"]>=1:
              name=row['Name'].lower()
              rate=row['Rate']
              category=row['Category'].lower()
              dataset.append({'Name': name,'Rate': rate,'Category':category })
              seen_names.append(row['Name'])


    return dataset

dataset2 = load_dataset('Report4.csv')


nlp = spacy.load('en_core_web_sm')

def loop(prod):
    str=""
    for i in prod:
        str=str+i+","
    return str


def chatbot(message):
    doc = nlp(message)
    response = "I'm sorry, I didn't understand your message."
    c=0
    string1=None
    string2=""
    row=[]
    for a in doc:
        row.append(a.pos_)
        if a.pos_=="NOUN" and string1 is None:
           string1=a.text
           c=1
        elif c>=1 and (a.text!="of" and a.text!="?"):
             if c==1:
                string2=a.text+" "
                c=c+1
             else:
                 string2=string2+" "+a.text

    category = None

    for a in dataset2:
        if a['Category'] in doc.text:
           category = a['Category']
           break



    category_collection = []
    category_product = []

    category_collection = []
    category_product = []
    all_product=[]
    for item in dataset2:
        if item['Category'] not in category_collection:
            category_collection.append(item['Category'])

    m=0
    for item in dataset2:

        if item["Category"] not in category_collection:
           category_collection.append(item["Category"])
        if item["Name"] not in all_product:
           all_product.append(item["Name"])
    if (string1 == 'price' or string1 == 'cost'):
       for item in dataset2:
           v=item['Name']
           if (bleu([string2], item['Name'], smoothing_function=smoothie) > m):
              m = bleu([string2], item['Name'], smoothing_function=smoothie)

              response = f"The price of {item['Name']} is {item['Rate']} taka"
    elif (string1 == 'category' or string1 == 'type'):
         for item in dataset2:
             if (bleu([string2], item['Name'], smoothing_function=smoothie) > m):
                m = bleu([string2], item['Name'], smoothing_function=smoothie)
                #print(m)
                response = f"The category of {item['Name']} is {item['Category']}"
    elif ("items" or "products" in doc.text) and ("category" in doc.text) and category != None:
          for item in dataset2:
              if item['Category'] == category and (item['Name'] not in doc.text):
                 category_product.append(item['Name'])
                 response = f"Under the {item['Category']} category,the available products are {loop(category_product)}"
    elif ("category " or "categories" in doc.text ) and "products" not in doc.text and item["Name"] not in doc.text and item["Category"] not in doc.text:
         response = f"Categories of all the products: {loop(category_collection)}"

    elif ("products" or "product" in doc.text) and item["Name"] not in doc.text and item["Category"] not in doc.text:


         all_product.append(item['Name'])
         response = f"The available all the products are: {loop(all_product)}"

    return response




    return response

player.say("Hello sir,Our super shop provides the products of different categories,On the screen you can see those categories and all the available products.")
print("Category of the products:baby care,baby food,beverage,commodities,dairy,electronics and home appliances,home care,kitchen additives,packaged food,perishables,personal care,protein,sweet & fast food,gift and toys,stationeries.")
print()
print(chatbot("All the products"))
print()
player.say("How may i help you?")
print()

while True:
      text=chatbot(listen())
      print(text)
      print()
      player.say(text)
      player.runAndWait()