# Setup and Library
import os
import bs4
import pandas as pd
import requests
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords as ss
import nltk
import re

# Data Extraction

# Read the data file
df = pd.read_excel("Input.xlsx")

for index,row in df.iterrows():
    url = row['URL']
    url_id = row['URL_ID']

    #set url
    header = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"}

    try:
        response = requests.get(url,headers=header)
    except:
        print(f'Unable to get url of {url_id}')

    # Beautifulsoup object

    try:
        soup = bs4.BeautifulSoup(response.content,'html.parser')

    except:
        print(f'Unable to get the page of {url_id}')

    # Find the header
    try:
        title = soup.find('h1').get_text()


    except:
        print(f'Unable to get the title of {url_id}')
        continue

    # Find the text

    document = ""
    try:
        for p in soup.find_all('p'):
            document+= p.get_text()

    except:
        print(f'Unable to get the text of {url_id}')

    path ="files"

    file_name = path +str(url_id) + ".txt"
    print("its processing:{}".format(url_id))

    with open(file_name,"w",encoding="utf-8") as file:
        file.write(title+"\n"+document)

#Unable to get the title of blackassign0036
#Unable to get the title of blackassign0049




# Directories
text_dir = 'files'
stopwords_dir = "StopWords"
sentiment_dir = "MasterDictionary"

stopwords = set()

for files in os.listdir(stopwords_dir):
    with open(os.path.join(stopwords_dir, files), 'r', encoding='ISO-8859-1') as f:
        stopwords.update(set(f.read().splitlines()))

text_document = []

for text in os.listdir(text_dir):
    with open(os.path.join(text_dir, text), "r", encoding="utf-8") as f:
        text = f.read()

        # tokenize the given text
        words = word_tokenize(text)

        # filtering without stop words
        filter_text = [word for word in words if word.lower() not in stopwords]
        # add the word into text_document
        text_document.append(filter_text)

# possitive words and negative from the directory

postive = set()
negative = set()

for files in os.listdir(sentiment_dir):
    if files == "positive-words.txt":
        with open(os.path.join(sentiment_dir, files), 'r', encoding='ISO-8859-1') as f:
            postive.update(f.read().splitlines())
    else:
        with open(os.path.join(sentiment_dir, files), 'r', encoding='ISO-8859-1') as f:
            negative.update(f.read().splitlines())

# now collect the positive word and negative from each file
# Calculate the scores from the positive and negative words

positive_words = []
negative_words = []
positive_score = []
negative_score = []
polarity_score = []
subjectivity_score = []

# iterate through the list of docs

for i in range(len(text_document)):
    positive_words.append([word for word in text_document[i] if word.lower() in postive])
    negative_words.append([word for word in text_document[i] if word.lower() in negative])
    positive_score.append(len(positive_words[i]))
    negative_score.append(len(negative_words[i]))
    polarity_score.append((positive_score[i]-negative_score[i]) / (positive_score[i]+negative_score[i]) + 0.000001)
    subjectivity_score.append((positive_score[i] + negative_score[i]) / ((len(text_document[i]))+0.000001))


# Average Sentence Length = the number of words / the number of sentences
# Percentage of Complex words = the number of complex words / the number of words
# Fog Index = 0.4 * (Average Sentence Length + Percentage of Complex words)

avg_sentence_length = []
percentage_of_complex_words = []
fog_index = []
complex_word_count = []
avg_syllable_word_count = []

stopwords = set(ss.words('english'))

def measure(file):
    with open(os.path.join(text_dir,file),'r',encoding="utf-8") as f:
        text = f.read()
# Remove the punctuations
        text = re.sub(r'[^\w\s.]','',text)
# Split the text file into sentence
        sentences = text.split('.')
# Total number of sentences in a file
        num_sentence = len(sentences)
# Total words in the file
        words = [word for word in text.split() if word.lower() not in stopwords]
        num_words = len(words)


# Complex words having syllable count is grater than 2
# Complex words are word in text and contain more than two syllable
        complex_word = []
        for word in words:
            vowels = 'aeiou'
            syllable_count_word = sum(1 for letter in word if letter.lower() in vowels)
            if syllable_count_word > 2:
                complex_word.append(word)
# Syllable Count per Word
# We count the number of syllables in each word of the text by counting the in vowels present in each word
# we also handle some case where the word end with es and ed by not counting the as syllables

        syllable_count = 0
        syllable_words = []
        for word in words:
            if word.endswith('es'):
                word = word[:-2]
            elif word.endswith("ed"):
                word = word[:-2]
            vowels = "aeiou"
            syllable_count_word = sum(1 for letter in word if letter.lower() in vowels)
            if syllable_count_word >=1:
                syllable_words.append(word)
                syllable_count +=syllable_count_word

        ave_sentence_len = num_words/num_sentence
        avg_syllable_word_count = syllable_count/ len(syllable_words)
        percent_complex_word = len(complex_word)/num_words
        Fog_index = 0.4 * (ave_sentence_len + percent_complex_word)

        return ave_sentence_len,percent_complex_word,Fog_index, len(complex_word),avg_syllable_word_count

# Iterate through each file or docs

for file in os.listdir(text_dir):
    x,y,z,a,b = measure(file)
    avg_sentence_length.append(x)
    percentage_of_complex_words.append(y)
    fog_index.append(z)
    complex_word_count.append(a)
    avg_syllable_word_count.append(b)


# we have to count cleaned count and Average word length sum of the total number of each charactor in each word.
# so we need clean the text like ?,!,. and stop words

def cleaned_word(file):
    with open(os.path.join(text_dir,file),"r",encoding="utf-8") as f:
        text = f.read()
        text = re.sub(r'[^\w\s]', '' , text)
        words = [word for word in text.split() if word.lower() not in stopwords]
        length = sum(len(word) for word in words)
        average_word_length = length / len(words)
    return len(words),average_word_length

word_count = []
average_word_length =[]

for file in os.listdir(text_dir):
    x,y = cleaned_word(file)
    word_count.append(x)
    average_word_length.append(y)


# To calculate Personal pronouns in the text
# the counts of the words -"I","we","ours",and "us"

def count_personal_pronouns(file):
    with open(os.path.join(text_dir,file),'r',encoding="utf-8") as f:
        text = f.read()
        personal_pronouns = ["I", "we", "my", "ours", "us"]
        count = 0
        for pronoun in personal_pronouns:
            count += len(re.findall(r"\b" + pronoun + r"\b", text))  # \b is used to match word boundaries
    return count

pp_count = []

for file in os.listdir(text_dir):
    x = count_personal_pronouns(file)
    pp_count.append(x)



# Create excel file for output

output_df = pd.read_excel('Output data structure.xlsx')

# URL_ID 36,49 has 404 error. Therefore, we are going drop

output_df.drop([37,50],axis=0,inplace=True)

# These are the required parameters
variables = [positive_score,
            negative_score,
            polarity_score,
            subjectivity_score,
            avg_sentence_length,
            percentage_of_complex_words,
            fog_index,
            avg_sentence_length,
            complex_word_count,
            word_count,
            avg_syllable_word_count,
            pp_count,
            average_word_length]




# write the values to the dataframe
for i, var in enumerate(variables):


    output_df.iloc[:, i + 2] = var



#now save the dataframe to the disk
output_df.to_excel('Output_Data.xlsx',index=False)


