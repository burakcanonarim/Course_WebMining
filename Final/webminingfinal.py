# -*- coding: utf-8 -*-
"""WebMiningFinal.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/16Yy47O7i4N_av6Se4tedgppBEYIBb6DK
"""

pip install transformers # colab da olmadığı için indirdik.

import random
import warnings
from datetime import datetime
import requests
import nltk
from bs4 import BeautifulSoup as bs
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import torch
import json
from keras.callbacks import EarlyStopping
from keras.layers import Dense, Dropout
from keras.models import Sequential
from keras.optimizers import Adagrad
from sklearn.decomposition import PCA
from sklearn.metrics import classification_report, f1_score
from sklearn.utils import class_weight
from tqdm import tqdm
from transformers import AutoModel, AutoTokenizer

# CRAWLER
site = 'https://eksisozluk.com/ask-101--2232943'

headers = {   #İlgili websitesi botlar için engelleme koymuş ihtimaline karşı
    'User-Agent': (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
        'AppleWebKit/537.36 (KHTML, like Gecko)'
        'Chrome/83.0.4103.61 Safari/537.36')
    }
dizi_baslangic = datetime(2020, 4, 24)
dizi_yorumlari = []
for i in range(212):
  sayfa = '?p=' + str(i+1) 
  r = requests.get(site + sayfa, headers=headers)
  if r.status_code != 200:
    print('bu başlıkta aradığınız kriterlere uygun giriş bulunamadı.')
  else:
    soup = bs(r.content, 'html.parser')
    entryler = soup.find(id='entry-item-list').find_all('li', limit=10)
    for num, entry in enumerate(entryler, 1):
      yazar = entry.find(class_='entry-author').get_text(strip=True)
      tarih = entry.find(class_='entry-date').get_text(strip=True)
      icerik = entry.find(class_='content').get_text(strip=True)
      if '~' in tarih: # güncellenen yorumları almak için
        zamanlar = tarih.split(' ~ ')
        if '.' in zamanlar[1]:
          tarih_object = datetime.strptime(zamanlar[1], '%d.%m.%Y %H:%M')
          if tarih_object > dizi_baslangic:
            dizi_yorumlari.append(icerik)
          else:
            continue
        else:
          tarih_object = datetime.strptime(zamanlar[0], '%d.%m.%Y %H:%M')
          if tarih_object > dizi_baslangic:
            dizi_yorumlari.append(icerik)
          else:
            continue
      else:
        tarih_object = datetime.strptime(tarih, '%d.%m.%Y %H:%M')
        if tarih_object > dizi_baslangic:
          dizi_yorumlari.append(icerik)
        else:
          continue
outF = open("dizi_yorumlari.txt", "w")
for line in dizi_yorumlari:
  # write line to output file
  outF.write(line)
  outF.write('\n')
outF.close()

train_path = '/content/test.json'
test_path = '/content/train.json'
validation_path = '/content/validation.json'
ask101_path = '/content/dizi_yorumlari.txt'
device = 'cuda'

def filter(text):
    final_text = ''
    for word in text.split():
      final_text += word + ' '
      
    return final_text

tokenizer = AutoTokenizer.from_pretrained("dbmdz/bert-base-turkish-128k-uncased")
bert = AutoModel.from_pretrained("dbmdz/bert-base-turkish-128k-uncased").to(device)

def feature_extraction(text):
    x = tokenizer.encode(filter(text))
    with torch.no_grad():
        x, _ = bert(torch.stack([torch.tensor(x)]).to(device))
        return list(x[0][0].cpu().numpy())

with open(train_path, 'r') as f:
    train = json.load(f)
with open(validation_path, 'r') as f:
    validation = json.load(f)
with open(test_path, 'r') as f:
    test = json.load(f)

mapping = {'negative':0, 'neutral':1, 'positive':2}

def data_prep(dataset):
  X = []
  y = []
  
  for element in tqdm(dataset):
    X.append(feature_extraction(element['sentence']))
    y_val = np.zeros(3)
    y_val[mapping[element['value']]] = 1
    y.append(y_val)
  return np.array(X), np.array(y)

X_train, y_train = data_prep(train)
X_val, y_val = data_prep(validation)
X_test, y_test = data_prep(test)

class_weights = class_weight.compute_class_weight(
    'balanced', np.unique(np.argmax(y_train, 1)), np.argmax(y_train, 1))
#es = EarlyStopping(monitor='val_loss', mode='min', verbose=1, patience=50)

model = Sequential()
model.add(Dense(512, activation='tanh', input_shape=(768,)))
model.add(Dropout(0.5))
model.add(Dense(128, activation='tanh'))
model.add(Dropout(0.5))
model.add(Dense(32, activation='tanh'))
model.add(Dropout(0.5))
model.add(Dense(3, activation='softmax'))

model.summary()

model.compile(loss='categorical_crossentropy',
              optimizer=Adagrad(),
              metrics=['accuracy'])

history = model.fit(np.array(X_train), np.array(y_train),
                    batch_size=64,
                    epochs=500,
                    verbose=1,
                    validation_data=(X_val, y_val),
                    class_weight=class_weights,
                    #callbacks = [es]
                    )

y_true, y_pred = np.argmax(y_test, 1), np.argmax(model.predict(X_test), 1)
print(classification_report(y_true, y_pred, digits=3))

"""### ***AŞK 101 ANALYSIS***"""

netflix_df = pd.read_fwf('/content/dizi_yorumlari.txt', header = None)
for i in range(66):
  del netflix_df[i+1]

netflix_df.columns = ['icerik']
netflix_df['value'] = 0

# -1 negative 0 neutral 1 positive
for idx, row in tqdm(netflix_df.iterrows()):
  X = feature_extraction(row['icerik'])
  netflix_df.at[idx, 'value'] = np.argmax(
      model.predict(np.array(X).reshape(1, -1)))-1

count_row = netflix_df.shape[0]
count_pozitif = 0
count_negatif = 0
count_notr = 0

for i in range(count_row):
  if netflix_df['value'][i] == -1:
    count_negatif += 1
  elif netflix_df['value'][i] == 0:
    count_notr += 1
  elif netflix_df['value'][i] == 1:
    count_pozitif += 1

begeni = count_pozitif - count_negatif
if begeni > 0:
  print("Ekşi sözlüğe göre Aşk101: FEVKALADENİN FEVKİNDE")
elif begeni == 0:
  print("Ekşi sözlüğe göre Aşk101: BANA NE DİZİDEN")
else:
  print("Ekşi sözlüğe göre Aşk101: BUNDAN KÖTÜSÜNÜ ANCAK AYNI KİŞİLER YAPABİLİR")

print(begeni, 'entry farkıyla bu dizinin beğenildiği sonucuna varılmıştır.')
print(count_negatif, 'enrty içerisinde dizinin berbat olduğu belirtilmiştir.')
print(count_notr, 'enrty içerisinde dizi umursanmamıştır.')
print(count_pozitif, 'enrty içerisinde dizinin fevkalade olduğu belirtilmiştir.')