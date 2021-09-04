'''
In this annotation tool, the annotator is given the image wihout any celebrity information (name, graph_knowledge)
'''


import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import numpy as np
import json
import cv2
import PIL as pil
import io
import os
import random
import sqlite3
import emoji
import xlsxwriter
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import seaborn as sns
import socket
import ssl
import requests
import ast
import base64
import datetime
from datetime import date, time , datetime
from datetime import timedelta


def get_graph_knowledge(person):
    
    with open('../scripts/celeb_graph_knowledge.json', 'r') as fp:
        data = json.load(fp)
    return data[person]


def get_name(img_id):

    with open('../scripts/celeb_boxes_10k.json', 'r') as fp:
        data = json.load(fp)

    celeb_names = []
    for i in data[img_id]['names']:
        celeb_names.append(i)#data[img_id]['names'][0]

    return celeb_names


def download_link(object_to_download, download_filename, download_link_text):

    """
    Generates a link to download the given object_to_download.

    object_to_download (str, pd.DataFrame):  The object to be downloaded.
    download_filename (str): filename and extension of file. e.g. mydata.csv, some_txt_output.txt
    download_link_text (str): Text to display for download link.

    Examples:
    download_link(YOUR_DF, 'YOUR_DF.csv', 'Click here to download data!')
    download_link(YOUR_STRING, 'YOUR_STRING.txt', 'Click here to download your text!')

    """
    if isinstance(object_to_download,pd.DataFrame):
        object_to_download = object_to_download.to_csv(index=False)

    # some strings <-> bytes conversions necessary here
    b64 = base64.b64encode(object_to_download.encode()).decode()

    return f'<a href="data:file/txt;base64,{b64}" download="{download_filename}">{download_link_text}</a>'

session = st.session_state
session2 = st.session_state
annotations = pd.DataFrame(columns = ['ID', 'Notes', 'Hate_level_case_1_1', 'Hate_level_case_1_2', 'Hate_level_case_2_1', 'Hate_level_case_2_2'])



sns.set_style('darkgrid')

option1 = ' '
option2 = 'Annotation'
selected_option = st.sidebar.selectbox(
    'Choose a view',
    (option1, option2)
)

img_path = './img/'

# ----- Annotation -----
if selected_option == option2: 
    st.markdown("<h1 style='text-align: center;'>Hello! Please label some of the memes below</h1>", unsafe_allow_html=True)

    results = []

    check = False
    for result in os.listdir(img_path):
        img_name = result
        results.append(os.path.join(img_path, img_name))
    
    if(len(results) == 0):
        st.markdown("<h3 style='text-align: center;'>Congratulations, you have nothing to label!​​​​​​​​​​​​​​​​​​​​​ &#x1F60a;</h3>", unsafe_allow_html=True)


    # def set_index(value):
    #     session['curr_index'] = value

    # if('curr_index' not in session):
    #     session['curr_index'] = 0

    # index_2 = session['curr_index']

    index = st.number_input(label = 'Index', value = 0 ,min_value = 0, max_value = 146, step = 1)
    plus_sign = '<p style="font-family:sans-serif; color: brown   ; font-size: 15px;"> ' + "+ : move to next meme" + '</p>'
    st.markdown(plus_sign, unsafe_allow_html=True)
    minus_sign = '<p style="font-family:sans-serif; color: brown   ; font-size: 15px;"> ' + "- : move to previous meme" + '</p>'
    st.markdown(minus_sign, unsafe_allow_html=True)

    
    results.sort()
    
    img_id = results[index]
    img_name = results[index]
    img_score = results[index]
    img = cv2.imread(img_name)
 
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    height, width, channels = img.shape
    
    col1, col3, col2 = st.beta_columns(3)
    
    with col1:
        st.image(img, width=int(width*0.5))
        # if(str(img_id) in session):
        #     celebs = get_name(img_id[6:])
        #     for i in celebs:
        #         st.text("Celebrity name : {}".format(i))#get_name(img_id[6:])
        #         info = get_graph_knowledge(i)#get_name(img_id[6:])
        #         new_title = '<p style="font-family:sans-serif; color: #2e4053   ; font-size: 15px;"> ' + info + '</p>'
        #         st.markdown(new_title, unsafe_allow_html=True)
            
        
    with col3:
        st.write('')

    with col2:
        st.markdown("<h2>What kind of hateful meme is this?</h2>", unsafe_allow_html=True)
        
        # to check wheather the annotator know the person in the image or not
        is_the_person_known = st.checkbox('Do you know the person(s) in this meme?', key = "{}.1".format(img_id))

        # first case, the annotator knows the person in the image
        if(is_the_person_known):
            st.write('Please write the name of the person(s) in the meme and some information about each:')
            notes = st.text_area('Notes', key="{}.6".format(img_id))
    
            hate_level_case_1_1 = st.radio('Hateful level',['1', '2', '3'], key = "{}.2".format(img_id))
            st.caption('1 : Not hateful')
            st.caption('2 : Hateful level is intermediate')
            st.caption('3 : Hateful level is very high')

            st.write('Suppose that you do not know the person(s) in this meme, what will be your hateful level rating?')
            hate_level_case_1_2 = st.radio('Hateful level',['1', '2', '3'], key = "{}.3".format(img_id))

        # second case, the annotatoe don't know the person in the image
        else:
            hate_level_case_2_1 = st.radio('Hateful level',['1', '2', '3'], key = "{}.4".format(img_id))
            st.caption('1 : Not hateful')
            st.caption('2 : Hateful level is intermediate')
            st.caption('3 : Hateful level is very high')

        # if(not is_the_person_known):
        #     if(str(img_id) in session):
        #         st.write('Now you some info about the person(s) in the meme, please re-choose the new hateful level and press the submit button again')
        if(st.button('Submit', key="{}.16".format(img_id))):

            if 'annotations' not in session:
                st.session_state.annotations =  annotations
                

            annotations = session.annotations
            if(img_id[6:] not in annotations['ID'].unique()):
                annotations.loc[len(annotations), 'ID'] = img_id[6:]


            hate_handler_case_1_1 = ''
            hate_handler_case_1_2 = ''
            hate_handler_case_2_1 = ''
            hate_handler_case_2_2 = ''

            notes_handler = ''
            if(is_the_person_known):
                hate_handler_case_1_1 = str(hate_level_case_1_1)
                hate_handler_case_1_2 = str(hate_level_case_1_2)
                notes_handler = notes
            else:
                if(str(img_id) not in  session):
                      
                    hate_handler_case_2_1 = str(hate_level_case_2_1)
                if(str(img_id) in session):
                    
                    hate_handler_case_2_2 = str(hate_level_case_2_1)
            
            if(not is_the_person_known):
                #st.markdown("<h1 style='padding:-50; color: red;'>Some title</h1>", unsafe_allow_html=True)
                if(str(img_id) not in session):
                    celebs = get_name(img_id[6:])
                    for i in celebs:
                        st.text("Celebrity name : {}".format(i))#get_name(img_id[6:])
                        info = get_graph_knowledge(i)#get_name(img_id[6:])
                        new_title = '<p style="font-family:sans-serif; color: #2e4053   ; font-size: 15px;"> ' + info + '</p>'
                        st.markdown(new_title, unsafe_allow_html=True)
                    new_info = '<p style="font-family:sans-serif; color: blue   ; font-size: 15px;"> ' + "Now you know some info about the person(s) in the meme, please re-choose the new hateful level and hit the submit button again" + '</p>'
                    st.markdown(new_info, unsafe_allow_html=True)
                session[str(img_id)] = 0


            #annotations.loc[annotations.ID == img_id[6:], "Image-text relation"] = image_text_relation_handler
            #annotations.loc[annotations.ID == img_id[6:], "Translation"] = translation_handler
            if(is_the_person_known):
                annotations.loc[annotations.ID == img_id[6:], "Hate_level_case_1_1"] = hate_handler_case_1_1
                annotations.loc[annotations.ID == img_id[6:], "Hate_level_case_1_2"] = hate_handler_case_1_2
            else:
                x = annotations.loc[annotations.ID == img_id[6:], "Hate_level_case_2_1"]
                if(x.isna().values.any()):
                    annotations.loc[annotations.ID == img_id[6:], "Hate_level_case_2_1"] = hate_handler_case_2_1
                annotations.loc[annotations.ID == img_id[6:], "Hate_level_case_2_2"] = hate_handler_case_2_2

            annotations.loc[annotations.ID == img_id[6:], "Notes"] = notes_handler
            session.annotations = annotations
       
        if st.button('Download your annotations as a CSV file'):
            st.markdown('<h5>Please send your annotations to this email address : abdelrahman.eldakrony@stud.uni-due.de</h5>', unsafe_allow_html=True)
            tmp_download_link = download_link(session.annotations, 'annotations_' + str(datetime.now()) + '.csv', 'Click here to download your data!')
            st.markdown(tmp_download_link, unsafe_allow_html=True)


        
