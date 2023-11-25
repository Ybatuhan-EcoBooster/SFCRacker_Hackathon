import streamlit as st
import re
from pdfminer.high_level import extract_pages, extract_text
import numpy as np
import pandas as pd
import os

st.set_page_config(page_title='SF_Cracker Hackaton',
                   page_icon='📑',
                   layout='wide')

# Data verification
def verification(pdf,datasfrc,date,kodzak,LP):
    
    # Companies Name
    first_data = pd.read_excel('CompaniesName.xlsx') # Provided by hackaton
    first_data = first_data[['LP.','KOD ZAKŁADU','NAZWA ZAKŁADU']]
        
    # Keywords
    second_data = pd.read_excel('KeyWords.xlsx') # Provided by hackaton
    second_data = second_data[['Unnamed: 1','Unnamed: 2','Unnamed: 3']].iloc[1:]
    second_data = second_data.rename(columns=second_data.iloc[0])
    second_data.drop(index = second_data.index[0],axis=0,inplace=True)
    second_data = second_data.reset_index(drop=True)

    # PDF Reports
    text  = extract_text(pdf)


    keywords = second_data['NAZWA SEKCJI (WEDŁUG ROZPORZĄDZENIA)'].to_list()

    # Text Patter Symbols
    main_pattern = re.compile(r'[a-zA-Z]\.[0-9] .*')
    main_matches = main_pattern.findall(text)
    common_elements = [element for element in keywords if element not in main_matches]

    pattern = re.compile(r'[a-zA-Z].[a-zA-Z_0-9]\.\d .*')
    matches = pattern.findall(text)
    
    pattern_1 = re.compile(r'[a-zA-Z].[a-zA-Z_0-9].[a-zA-Z_0-9]\.\d .*')
    matches_1 = pattern_1.findall(text)

    pattern_2 = re.compile(r'[a-zA-Z].[a-zA-Z_0-9].[a-zA-Z_0-9].[a-zA-Z_0-9]\.\d .*')
    matches_2 = pattern_2.findall(text)

    new_list = common_elements + matches_2 + matches_1 + matches
    new_sort = sorted(new_list)
    multi = len(new_sort)

    new_second = second_data[['ID SEKCJI NADRZĘDNEJ (STAŁA)','NAZWA SEKCJI (WEDŁUG ROZPORZĄDZENIA)']]

    new_sort_df = pd.DataFrame(new_sort)
    new_sort_df.rename(columns={0:'NAZWA SEKCJI (WEDŁUG ROZPORZĄDZENIA)'}, inplace=True)
    merge = pd.merge(new_second,new_sort_df, on='NAZWA SEKCJI (WEDŁUG ROZPORZĄDZENIA)', how='outer')

    # Final CSV file creating
    final_df = pd.DataFrame()
    final_df['ID_TAB']= [1] * multi
    final_df['DATA SFCR'] = [datasfrc] * multi
    final_df['WERSJA SFCR'] = [date] * multi
    final_df['KOD ZAKLADU'] = [f'{kodzak}'] * multi
    final_df['LP.'] = [f'{LP}']*multi
    final_df['ID SEKCJI NADRZĘDNEJ (STAŁA)'] = merge['ID SEKCJI NADRZĘDNEJ (STAŁA)']
    final_df['NAZWA SEKCJI (WEDŁUG ROZPORZĄDZENIA)'] = merge['NAZWA SEKCJI (WEDŁUG ROZPORZĄDZENIA)']

    unmatched_data = [item for item in new_sort if item not in keywords]
    
    def extract_paragraph(titlex):
        
        # Use regex to find the title and its corresponding paragraph
        patternx = re.compile(fr'{titlex}\s*([\s\S]+?)(?=\n\n|$)')
        matchx = patternx.search(text)
        
        paragraph = matchx.group(1).strip()
        return paragraph

    text_list = []

    for titley in unmatched_data:
        result = extract_paragraph(titley)
        text_list.append(result)

    # Finding text paragraph
    text_list = pd.DataFrame(text_list)
    text_list['NAZWA SEKCJI (WEDŁUG ROZPORZĄDZENIA)'] = unmatched_data
    text_list.rename(columns={0:'Treść'},inplace=True)

    Merged_Data_2 = pd.merge(final_df,text_list, on='NAZWA SEKCJI (WEDŁUG ROZPORZĄDZENIA)', how='outer')
    Sorted_DF = Merged_Data_2.sort_values(by='NAZWA SEKCJI (WEDŁUG ROZPORZĄDZENIA)',ascending=True)

    
    return Sorted_DF

# Page Configure

with st.empty():

    with st.container():

        st.title('WELCOME TO VERIFICATION SYSTEM ⚙️')

        directory_path = 'D:\dosyalar\Github\SFCraker\SFCR' # Database file path

        folder_names = [folder for folder in os.listdir(directory_path) if os.path.isdir(os.path.join(directory_path, folder))]

        option = st.selectbox(
        
        'Choose The Company 🏢',
        (folder_names))

        st.info(f'You selected: {option}')

        directory_path_2 = f'D:\dosyalar\Github\SFCraker\SFCR\{option}'
        date_numbers = [os.path.basename(file) for file in os.listdir(directory_path_2) if os.path.isfile(os.path.join(directory_path_2, file))]

        date = st.selectbox('Please Choose Date 🗓:',(date_numbers))
        st.info(f"You selected: {date}")

        PDF = f'D:\dosyalar\Github\SFCraker\SFCR\{option}\{date}'

        def ConvertCSV(SaveDF):
            return SaveDF.to_csv()  # Saving File with CSV
        

        # Companies Name
        CompanyNameData = pd.read_excel('CompaniesName.xlsx')
        CompanyNameData = CompanyNameData[['LP.','KOD ZAKŁADU','NAZWA ZAKŁADU']]
        
        KodzakNo = CompanyNameData[CompanyNameData['NAZWA ZAKŁADU'] == option]['KOD ZAKŁADU']
            
        Lp = CompanyNameData[CompanyNameData['NAZWA ZAKŁADU'] == option]['LP.']
            
        Verificationmodel = verification(PDF,datasfrc=option,date=date,kodzak=KodzakNo,LP=Lp) #Function of verification

        st.dataframe(Verificationmodel, use_container_width=True)

        ModelCSV = ConvertCSV(Verificationmodel)
        st.download_button('Download the file ✅', ModelCSV, file_name=f'{date}SFCR{KodzakNo}_{option}.csv')
        
