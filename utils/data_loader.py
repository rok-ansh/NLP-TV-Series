from transformers import pipeline
from nltk import sent_tokenize
import nltk
import torch
from glob import glob
import pandas as pd
import numpy as np


# Load the Data  
scripts = []
episode_num = []
def load_subtitles_dataset(dataset_path):
    file_path = glob.glob(dataset_path + '/*.ass')
    for path in file_path:
        #Read the file 
        with open(path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            # I want to read only after line number 27 as in content above things are useless 
            lines = lines[27:]
            # Now i want the text only so that can be obtain after 9 commas 
            lines = [",".join(line.split(",")[9:]) for line in lines]
            # print("opened the file")

        # In the above output we can see we have \\N in the output 
        lines = [line.replace("\\N", " ") for line in lines]

        # Now lets try to combine the sentence which is seperated by a space 
        script  = " ".join(lines)
        # print("scripts joined")

        # Lets get the episode number 
        episode = int(path[0].split("-")[-1].split(".")[0].strip())
        # print("episode value")

        scripts.append(script)
        episode_num.append(episode)

        df = pd.DataFrame.from_dict({'episode':episode_num, 'script':scripts})
        # print("df value")

    return df

        

