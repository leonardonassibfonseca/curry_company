#==========================================================
#Bibliotécas
#==========================================================
from haversine import haversine
import re
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime
import streamlit as st
from PIL import Image
from streamlit_folium import folium_static
import folium
import numpy as np

st.set_page_config(page_title = 'Visao Entregadores', layout = 'wide')#Deixa o objeto ocupar toda a extensão da tela

#==========================================================
#Funções
#==========================================================
def velocidade_entregador(df, ascend):
    '''Esta função tem a responsabilidade retornar uma tabela
        Input: dataframe
        Output: tabela
    ''' 
    df_aux = (df.loc[:, ['Time_taken(min)', 'Delivery_person_ID', 'City']]
                .groupby(['Delivery_person_ID', 'City'])
                .mean()
                .reset_index()
                .sort_values(['Time_taken(min)','City'], ascending = ascend))    
    df_aux1 = df_aux.loc[df_aux['City'] == 'Metropolitian', :].head(10)
    df_aux2 = df_aux.loc[df_aux['City'] == 'Urban', :].head(10)
    df_aux3 = df_aux.loc[df_aux['City'] == 'Semi-Urban', :].head(10)
    df_aux4 = pd.concat([df_aux1, df_aux2, df_aux3]).reset_index(drop=True)                    
    return df_aux4
def limpar_codigo(df):
    '''Esta função tem a responsábilidade de limpar e formatar o dataframe

        Tipos de limpeza e formatação:
        1. Remoção dos dados NaN
        2. Mudança do tipo da coluna de dados
        3. Remoção dos espaços das variáveis de texto
        4. Formatação da coluna de data
        5. Separação do texto da variável numérica

        Input: dataframe
        Output: dataframe    
    '''    
    #Removendo espaços vazios dentro de texto/string/object
    df['ID'] = df['ID'].str.strip()
    df['Delivery_person_Age'] = df['Delivery_person_Age'].str.strip()
    df['Delivery_person_ID'] = df['Delivery_person_ID'].str.strip()
    df['Road_traffic_density'] = df['Road_traffic_density'].str.strip()
    df['Type_of_order'] = df['Type_of_order'].str.strip()
    df['Type_of_vehicle'] = df['Type_of_vehicle'].str.strip()
    df['Festival'] = df['Festival'].str.strip()
    df['City'] = df['City'].str.strip()
    
    #Excluindo as linhas vazias (diferentes de 'NaN' na coluna 'Delivery_person_Age') com condicional
    linhas_selecionadas = df['Delivery_person_Age'] != 'NaN'# != É o sinal de diferente de
    df = df.loc[linhas_selecionadas, :]
    
    #Excluindo as linhas vazias (diferentes de 'NaN' na coluna 'Road_traffic_density') com condicional
    linhas_selecionadas = df['Road_traffic_density'] != 'NaN'# != É o sinal de diferente de
    df = df.loc[linhas_selecionadas, :]
    
    #Excluindo as linhas vazias (diferentes de 'NaN' na coluna 'City') com condicional
    linhas_selecionadas = df['City'] != 'NaN'# != É o sinal de diferente de
    df = df.loc[linhas_selecionadas, :]
    
    #Excluindo as linhas vazias (diferentes de 'NaN' na coluna 'Festival') com condicional
    linhas_selecionadas = df['Festival'] != 'NaN'# != É o sinal de diferente de
    df = df.loc[linhas_selecionadas, :]
    
    #Convertendo de texto/string/object para número
    df['Delivery_person_Age'] = df['Delivery_person_Age'].astype(int)
    
    #Convertendo de texto/string/object para número decimal
    df['Delivery_person_Ratings'] = df['Delivery_person_Ratings'].astype(float)
    
    #Convertendo de texto/string/object para data
    df['Order_Date']=pd.to_datetime(df['Order_Date'], format = '%d-%m-%Y')
    
    #Removendo as linhas da coluna multiple_deliveries que tenham o
    #o conteúdo igual a 'NaN'
    linhas_selecionadas = df['multiple_deliveries'] != 'NaN '# != É o sinal de diferente de
    df= df.loc[linhas_selecionadas, :]
    df['multiple_deliveries']=df['multiple_deliveries'].astype(int)
    
    #Removendo texto de número
    df['Time_taken(min)'] = df['Time_taken(min)'].apply(lambda x: x.split('(min) ')[1])
    df['Time_taken(min)'] = df['Time_taken(min)'].astype(int)
    return df

#----------------------------------Inicio da estrutura lógica do código-----------------------------------
#Importando o dataset
df1 = pd.read_csv('dataset/train.csv')

#Fazendo uma cópia do arquivo original
df = df1.copy()

#Limpando os dados
df = limpar_codigo(df)

#VISÃO: ENTREGADORES

#==========================================================
#Barra laterial
#==========================================================
st.header('Marketplace - Visão Entregadores')

#image_path = 'C:/Users/Leonardo/curso_cientista_de_dados/Repos/Python_zero_ao_ds/arquivos_python/'
image = Image.open('logo.png')#Imagem precisa estar na mesma pasta do arquivo .PY
st.sidebar.image(image, width = 120)

st.sidebar.markdown('## Cury Company')
st.sidebar.markdown('## A mais rápida entrega da cidade!')
st.sidebar.markdown('''---''')

st.sidebar.markdown('## Selecione uma data limite')

date_slider = st.sidebar.slider(
    'Até qual valor?',
    value = datetime(2022, 4, 13),
    min_value = datetime(2022, 2, 11),
    max_value = datetime(2022, 4, 6),
    format = 'DD-MM-YYYY')

st.sidebar.markdown('''---''')

traffic_options = st.sidebar.multiselect('Quais as condições de trânsito?',
                        ['Low', 'Medium', 'High', 'Jam'],
                        default = ['Low', 'Medium', 'High', 'Jam'])

st.sidebar.markdown('''---''')
st.sidebar.markdown('### Powered by Comunidade DS')

#Filtro de data
linhas_selecionadas = df['Order_Date'] < date_slider
df = df.loc[linhas_selecionadas, :]

#Filtro de trânsito
linhas_selecionadas = df['Road_traffic_density'].isin(traffic_options)#isin está em
df = df.loc[linhas_selecionadas, :]

st.dataframe(df)
#==========================================================
#Layout no Streamlit
#==========================================================
tab1, tab2, tab3 = st.tabs(['Visão Gerencial', '_', '_'])

with tab1:
    with st.container():#Criando 1º container grande
        st.markdown('#### Métricas Gerais')
        
        col1, col2, col3, col4 = st.columns(4, gap = 'large')#Dividindo o container grande em 4 partes 
        with col1:            
            maior_idade = df['Delivery_person_Age'].max()#A maior idade
            col1.metric('Maior idade', maior_idade)
        with col2:
            menor_idade = df['Delivery_person_Age'].min()#A menor idade
            col2.metric('Menor idade', menor_idade)
        with col3:
            melhor_condição_veículo = df['Vehicle_condition'].max()#Melhor condição de veículo
            col3.metric('Melhor cond. veículo', melhor_condição_veículo)
        with col4:            
            pior_condição_veículo = df['Vehicle_condition'].min()#Pior condição de veículo
            col4.metric('Pior cond. veículo', pior_condição_veículo)
        
        with st.container():#Criando 2º container grande
            st.markdown('''---''')
            st.markdown('#### Avaliações')
            
            col1, col2 = st.columns(2, gap = 'small')#Dividindo o container grande em 2 partes 
            with col1:
                st.markdown('##### Avaliação média por Entregador')
                df_aux_entregador = (df.loc[:, ['Delivery_person_Ratings', 'Delivery_person_ID']]
                                       .groupby(['Delivery_person_ID'])
                                       .mean()
                                       .reset_index())
                st.dataframe(df_aux_entregador)
            with col2:
                st.markdown('##### Avaliação média por Trânsito')
                df_aux_transito = (df.loc[:, ['Delivery_person_Ratings', 'Road_traffic_density']]
                                     .groupby(['Road_traffic_density'])
                                     .agg({'Delivery_person_Ratings':['mean', 'std']}))
                df_aux_transito.columns = ['Delivery_mean', 'Delivery_std']
                df_aux_transito = df_aux_transito.reset_index()
                st.dataframe(df_aux_transito)
                
                st.markdown('##### Avaliação média por Clima')
                df_aux_clima = (df.loc[:, ['Delivery_person_Ratings', 'Weatherconditions']]
                                  .groupby(['Weatherconditions'])
                                  .agg({'Delivery_person_Ratings':['mean', 'std']}))
                df_aux_clima.columns = ['Delivery_mean', 'Delivery_std']
                df_aux_clima = df_aux_clima.reset_index()
                st.dataframe(df_aux_clima)
            
        with st.container():#Criando 3º container grande
            st.markdown('''---''')
            st.markdown('#### Velocidade de Entrega')
            
            col1, col2 = st.columns(2, gap = 'small')#Dividindo o container grande em 2 partes 
            with col1:
                df_aux4 = velocidade_entregador(df, ascend = True)
                st.markdown('##### Top Entregadores mais rápido') 
                st.dataframe(df_aux4)
            with col2:
                df_aux4 = velocidade_entregador(df, ascend = False)
                st.markdown('##### Top Entregadores mais lento')
                st.dataframe(df_aux4)
