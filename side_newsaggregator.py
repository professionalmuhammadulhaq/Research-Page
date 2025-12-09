from bs4 import BeautifulSoup
import requests
from transformers import pipeline
from datetime import datetime
import time
import random
import pandas as pd
import random
import csv

# Translator library
from googletrans import Translator as GoogleTrans
from deep_translator import (GoogleTranslator, MyMemoryTranslator,
                             PonsTranslator, LingueeTranslator)
import argostranslate.package
import argostranslate.translate
import mtranslate

# Translator Function

# ------------------------
# TRANSLATOR FUNCTIONS
# ------------------------

def googletrans_translate(text):
    try:
        translator = GoogleTrans()
        res = translator.translate(text, dest='en').text
        return res if res else None
    except Exception:
        return None

def deep_google(text):
    try:
        return GoogleTranslator(source='id', target='en').translate(text)
    except Exception:
        return None

def deep_mymemory(text):
    try:
        return MyMemoryTranslator(source='id', target='en').translate(text)
    except Exception:
        return None

def mtranslate_translate(text):
    try:
        res = mtranslate.translate(text, 'en', 'auto')
        return res if res and res.strip() != '' else None
    except Exception:
        return None

# Ordered from most reliable → least reliable
translators = [
    deep_google,
    googletrans_translate,
    deep_mymemory,
    mtranslate_translate,
]

def safe_translate(text):
    for t in translators:
        try:
            output = t(text)
            if output:
                return output
        except Exception:
            continue
    return text  # final fallback



pipe = pipeline("sentiment-analysis", model="StephanAkkerman/FinTwitBERT-sentiment")
translator = GoogleTranslator(source='id', target='en')

# Controls
keywords = [
    #"bbca",  # PT Bank Central Asia Tbk
    #"bbri",  # PT Bank Rakyat Indonesia (Persero) Tbk
    #"bmri",  # PT Bank Mandiri (Persero) Tbk
    #"bbni",  # PT Bank Negara Indonesia (Persero) Tbk
    "bris",  # PT Bank Syariah Indonesia Tbk
]
year_start, month_start, day_start = map(int, '2025,10,12'.split(',')) # Year, Month, Day # Most Recent
year_end, month_end, day_end = map(int, '2024,11,20'.split(',')) # Past

# Initialization Variables (Dont Change it)
start_date = datetime(year_start, month_start, day_start).date() # Year, Month, Day
end_date = datetime(year_end, month_end, day_end).date()
i = 1
df = pd.DataFrame(columns=['date', 'symbol', 'title', 'link', 'text', 'label']) # I ADD THIS
mapping = {
    'BULLISH': 1,
    'BEARISH': -1,
    'NEUTRAL': 0
}

with open('valid_proxies.csv', 'r') as f:
    valid_proxies = [row[0] for row in csv.reader(f)]

def get_with_proxy(url, valid_proxies, max_attempts=5):
    attempts = 0

    while attempts < max_attempts:
        proxy = random.choice(valid_proxies)

        try:
            res = requests.get(
                url,
                proxies={"http": proxy, "https": proxy},
                timeout=15
            )

            if res.status_code == 200:
                return res   # success

        except Exception:
            pass  # proxy failed, try next

        attempts += 1  # count failed attempt

    # Fallback: try without proxy
    try:
        res = requests.get(url, timeout=10)
        if res.status_code == 200:
            return res
    except Exception:
        return None  # Last fallback failed

    return None

def main():
    for keyword in keywords:
        
        stop = False
        page = 1
        next_link = ''

        while True:
            # Loop per search page
            if page == 1:
                url = f'https://www.cnbcindonesia.com/search?query={keyword}&fromdate={year_end}%2F{month_end}%2F{day_end}&todate={year_start}%2F{month_start}%2F{day_start}'
            elif page > 1:
                url = next_link
            
            req = get_with_proxy(url, valid_proxies=valid_proxies, max_attempts=5)

            soup = BeautifulSoup(req.text, 'lxml')
            popups = soup.find_all('div', class_='nhl-list flex flex-col gap-6')

            # Loop per news popups
            for popup in popups:
                # Get the 'header'
                title = popup.article.a["dtr-ttl"]
                link = popup.article.a["href"]

                # Get the ''
                sub_req = requests.get(link)
                sub_soup = BeautifulSoup(sub_req.text, 'lxml')
                dates = sub_soup.find('div', class_='text-cm text-gray').text
                dt = datetime.strptime(dates, "%d %B %Y %H:%M").date()
                if dt < end_date:
                    stop = True
                    break

                paragraphs = sub_soup.find_all('p')

                columns = []
                # if keyword not in article's text, we go
                if any(keyword in p.get_text().lower() for p in paragraphs):   # <-- FIXED
                    columns.append(dt) # I ADD THIS
                    columns.append(keyword)
                    columns.append(title) # I ADD THIS
                    columns.append(link) # I ADD THIS

                    print(keyword.upper(), ' - ', dates)
                else:
                    continue 

                # Get the text per news popup
                text_list = [] # I ADD THIS
                results = [] # results per page (bull, bear, neutral)
                for paragraph in paragraphs:
                    if keyword in paragraph.get_text().lower():
                        paragraph_text = paragraph.text
                        sentences = [s.strip().lower() for s in paragraph_text.split('.')]
                        for sentence in sentences:
                            if keyword in sentence:
                                #print(sentence)
                                text_list.append(sentence) # I ADD THIS
                                text_en = safe_translate(sentence)
                                result = pipe(text_en)[0]['label']
                                results.append(result)

                text = ' '.join(text_list) # I ADD THIS
                columns.append(text) # I ADD THIS
                if results:
                    final_result = max(results, key=results.count)
                    final_result = mapping[final_result]
                    columns.append(final_result) # I ADD THIS
                else:
                    print(f'No \'{keyword}\' found in the article')

                df.loc[len(df)] = columns

                # set timer per page
                delay = random.uniform(2.5, 4.0) 
                time.sleep(delay)

            # Getting the link of the next page
            page_num_holder = soup.find('div', class_='flex gap-1 items-center justify-center m-0')
            try:
                next_link = page_num_holder.find('a', {'dtr-act': 'halaman selanjutnya'})['href']
            except Exception:
                stop = True

            if stop:
                break

            page += 1

if __name__ == "__main__":
    error_message = None
    try:
        main()
    except Exception as e:
        error_message = str(e)
        print(f'Error: {error_message}')
    finally:
        df.to_csv('mined_data_8.csv', index=False)
        if error_message:
            print(f'CSV saved after error: {error_message}')
        else:
            print('CSV saved successfully (no error).')