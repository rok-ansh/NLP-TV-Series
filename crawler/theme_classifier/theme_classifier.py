import torch
from transformers import pipeline
from nltk import sent_tokenize
import numpy as np 
import pandas as pd
# we want to use the load_subtitles_dataset function what is in utils 
import os
import sys
import pathlib
# I want to go back one file and wanted to go utils 
# folder_path -> current folder we are in 
folder_path = pathlib.Path(__file__).parent.resolve()
# lets append this folder path to our sys 
# sys.path.append(str(folder_path)+'../') -> this might crash
sys.path.append(os.path.join(folder_path,'../'))
from utils import load_subtitles_dataset
import nltk
nltk.download('punkt')
nltk.download('punkt_tab')

class ThemeClassifier:
    def __init__(self, theme_list):
        self.model_name = 'facebook/bart-large-mnli',
        self.device = 0 if torch.cuda.is_available() else 'cpu'
        self.theme_list = theme_list
        self.theme_classifier = self.load_model(self.device)

    def load_model(self, device):
    # theme_classifier is library form hugging face 
        theme_classifier = pipeline(
            "zero-shot-classification",
            model=self.model_name,
            device=device
        )
        return theme_classifier
    
    # Run the model 
    def get_themes_inference(self, scripts):
        # Now lets break down to sentence
        script_sentences = sent_tokenize(scripts)

        # Batch Sentence 

        # lets say batch size is 20 
        sentence_batch_size = 20
        scripts_batches = []
        # Running a loop form 1 st sentence to last sentence and making a batch of 20 i.e sentence_batch_size
        for index in range(0, len(script_sentences), sentence_batch_size):
            # Now joining all the sentence from 1st to 20th in 1st go and so on and so forth increment of 20 everytime
            sent = " ".join(script_sentences[index:sentence_batch_size+index])
            scripts_batches.append(sent)

        # Run the Model 

        # Lets now try to classify it based on the theme_list where we run on the theme_classifier for one sentence 
        # theme_classifier is library form hugging face 
        theme_output = self.theme_classifier(
            scripts_batches[:2],
            self.theme_list, 
            multi_label = True
        )

        # Wrangle the output 

        # Now lets convert the output in table format so that we can use it any way we want 
        # Example for {'dialogue': [0.9800739288330078, 0.9370127320289612],
        # 'betrayal': [0.9396896362304688, 0.6457238793373108]}

        themes = {}
        for output in theme_output:
            for label, score in zip(output['labels'], output['scores']):
                # print(label, score)
                if label not in themes:
                    themes[label] = []
                themes[label].append(score)

        # Lets have the mean of the value 
        themes = {key : np.mean(value) for key, value in themes.items()}

        return themes
    
    # Next task is to take the whole dataset and convert to Pandas DataFrame 
    def get_themes(self, dataset_path, save_path=None):
        # After processing i will save the processing in save_path kind of checkpoint so i dont need to ru the whole model again
        # so that i dont need to run everytime to see the output 

        # Load the Dataset 
        # Now we want to use the load_subtitles_dataset function what is in utils 
        df = load_subtitles_dataset(dataset_path)

        # Run the inference 
        # Now next task is to get each sentence and then apply the fucntion by using which we can classiify and get score for each sentence 
        output_themes = df['script'].apply(self.get_themes_inference)

  
        # Convert to Dataframe 
        theme_df = pd.DataFrame(output_themes.tolist())

        # Now lets combine both of them 
        # The below line of code means we are adding all the column in df for all theme_df
        df[theme_df.columns] =  theme_df

        # Save output 
        if save_path is not None:
            df.to_csv(save_path, index=False)
