import pandas as pd
import nltk
import string
import re
import spacy
from nltk import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.corpus import words
from textblob import TextBlob
from collections import Counter
import numpy as np
from scraping_linkeding_jobs import scraping_job_descriptions
import en_core_web_sm



nltk.download('stopwords')
nltk.download('punkt')
nltk.download('wordnet')
nltk.download('omw-1.4')
nltk.download('averaged_perceptron_tagger')
nltk.download('brown')
nltk.download('words')

# Job Descriptions database
data = pd.DataFrame([])
max_n = 400
location = "todo el mundo"
profiles = ["ui ux consultant"]

for profile in profiles:
    profile_search = profile
    results_scraping = scraping_job_descriptions(profile_search, location, max_n)
    if results_scraping is None:
        break
    else:
        data = data.append(pd.DataFrame(results_scraping), ignore_index=True)
        data.to_excel('uiux_descriptions.xlsx')

#C:\VTRoot\HarddiskVolume3\Users\Imagemaker_PC\Documents\frontend_developer2.csv
#data = pd.read_excel('datos_job_postings.xlsx')
#print(data.head())
#list_profiles = ["Data Scientist", "Full Stack Developer"]
#data = data[data.Query.isin(list_profiles)]
#print(data.head())

data = data.drop_duplicates()
print(data.shape)
# Job Descriptions Cleaning
lemmatizer = WordNetLemmatizer()
symbols_to_ignore = ['(', ')', '.', '\\', ':', '%', '’', '[', ']', '/', '//']
to_ignore = stopwords.words('english')
to_ignore.extend(symbols_to_ignore)
#to_ignore = symbols_to_ignore
cleaned_jobs = []
for job in data.Description:
    # Remove URL
    lower_job = re.sub('http://\S+|https://\S+', '', job)
    cleaned_jobs.append(lower_job.lower())

# Create new df
df = pd.DataFrame({'Query':data.Query, 'Description':cleaned_jobs})
print(df.shape)
# Extract patterns
sp = spacy.load('en_core_web_sm')
#sp = en_core_web_sm.load()

all_stopwords = sp.Defaults.stop_words

match_paterns = []
i = 0
for description in df.Description:
    
    regex1 = re.compile(r'(\bskill(s)?\b|\btool(s)?\b|\btechnique(s)?\b) (like|including)\s+([^.]+)')
    regex2 = re.compile(r'(\bproficiency\b|\bknowdledge\b|\bfamiliarity\b|\bexperience\b) ?(\bin\b|\bof\b|\bwith\b)? ?\s+([^.]+)')
    regex3 = re.compile(r'(\bexperience\b)\s+([^.]+):? ?\s+([^.]+)')

    mo1 = regex1.findall(description)
    mo2 = regex2.findall(description)
    mo3 = regex3.findall(description)

    mo_final = mo1 + mo2 + mo3

    res = list(map(" ".join, mo_final))
    res_final = " ".join(list(set(res)))
    chars = re.escape(string.punctuation)
    text = re.sub('experience|techniques(s)?|tools(s)?|skill(s)?|proficiency|knowledge|familiarity|’', '', res_final)
    profile = df.Query.iloc[i]
    profile_split = profile.lower().split("-")
    text = re.sub(profile.lower(), '', text)
    text_final = re.sub('[,:;\'\(\)?¿%-]', ' ', text)
    text_final = re.sub('machine learning', 'machine_learning', text)
    text_final = re.sub('apis', 'api', text)
    text_final = re.sub('power bi', 'powerbi', text)
    text_final = re.sub('/', ' ', text)


    text_tokens = word_tokenize(text_final)
    words_2 = [lemmatizer.lemmatize(w) for w in text_tokens]
    tokens_without_sw = [word for word in words_2 if not word in all_stopwords]
    tokens_without_sw_final = [word for word in tokens_without_sw if not word in profile_split]

    filtered_sentence = (" ").join(tokens_without_sw_final)

    match_paterns.append(filtered_sentence)
    i += 1
    #print(i)


## Create new df
df_final = pd.DataFrame({'Query': df.Query, 'Description': df.Description, 'Paterns': match_paterns})
print(df_final.Description)
print(df_final.Paterns)

# Remove other stopwords
other_stop_words = ["etc", "startup", "expertise", "prioritize", "cs"]
list_skills = ["ruby", "python", "c", "r", "anaconda"]
english_words = words.words()
english_words = [x for x in english_words if x not in list_skills]

df_final['Paterns'] = df_final['Paterns'].apply(lambda x: " ".join(x for x in x.split() if x not in other_stop_words))
df_final['Paterns'] = df_final['Paterns'].apply(lambda x: " ".join(x for x in x.split() if x not in english_words))

list_tags = ["N", "NNS", "NNP", "NNPS"]
df_final["skills"] = df_final['Paterns'].apply(lambda x: list(set([w for (w, pos) in TextBlob(x).pos_tags if pos[0] in list_tags])))
df_final["skills"] = df_final["skills"].apply(lambda x:  ' '.join([str(elem) for elem in x]))

# Group by profile
jda = df_final.groupby(['Query']).skills.sum().reset_index()

jobs_list = jda.Query.unique().tolist()
jda["skills_count"] = 0

for job in jobs_list:
    # Start with one review:
    text = jda[jda.Query == job].iloc[0].skills
    count_skills = dict(Counter(text.split()).most_common())
    key_to_remove = ["and/or", "-", "”", "“", "/", "youll", "–", "software"]
    count_skills = {key: count_skills[key] for key in count_skills if key not in key_to_remove}
    jda["skills_count"] = np.where(jda["Query"]==job, count_skills, jda["skills_count"])

print(jda)
jda.to_json(r'uiux_skills.json')
