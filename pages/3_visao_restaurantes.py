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

st.set_page_config(page_title = 'Visao Restaurantes', layout = 'wide')#Deixa o objeto ocupar toda a extensão da tela

#==========================================================
#Funções
#==========================================================
def grafico_sol_queimado(df):
    '''Esta função tem a responsabilidade retornar um gráfico de pizza
        Input: dataframe
        Output: gráfico de pizza    
    ''' 
    df_aux = (df.loc[:, ['Time_taken(min)','City', 'Road_traffic_density']]
                .groupby(['City', 'Road_traffic_density'])
                .agg({'Time_taken(min)': ['mean', 'std']}))
    df_aux.columns = ['Avg_time', 'Std_time']
    df_aux = df_aux.reset_index()
    figura = px.sunburst(df_aux, path = ['City', 'Road_traffic_density'], values = 'Avg_time', color = 'Std_time', color_continuous_scale = 'RdBu', color_continuous_midpoint=np.average(df_aux['Std_time']))
    return figura
def grafico_distribuicao_tempo(df):
    '''Esta função tem a responsabilidade retornar um gráfico de pizza
        Input: dataframe
        Output: gráfico de pizza   
    ''' 
    df['Distance'] = (df.loc[:, ['Restaurant_latitude','Restaurant_longitude',
                                'Delivery_location_latitude','Delivery_location_longitude']]
                        .apply(lambda x: haversine(
                                (x['Restaurant_latitude'], x['Restaurant_longitude']),
                                (x['Delivery_location_latitude'], x['Delivery_location_longitude'])), axis = 1))
    df_aux_cidade = (df.loc[:, ['Distance', 'City']]
                        .groupby(['City'])
                        .mean()
                        .reset_index())
    figura = go.Figure(data = [go.Pie(labels=df_aux_cidade['City'], values = df_aux_cidade['Distance'], pull=[0,0.1,0])])
    return figura
def grafico_media_desvio_padrao_distancia(df):
    '''Esta função tem a responsabilidade retornar uma tabela
        Input: dataframe
        Output: tabela   
    ''' 
    df_aux = (df.loc[:, ['Time_taken(min)','City', 'Type_of_order']]
                .groupby(['City', 'Type_of_order'])
                .agg({'Time_taken(min)': ['mean', 'std']}))
    df_aux.columns = ['Avg_time', 'Std_time']        
    df_aux_distancia = df_aux.reset_index()
    return df_aux_distancia
def grafico_media_desvio_padrao(df_aux):
    '''Esta função tem a responsabilidade retornar um gráfico de barra
        Input: dataframe
        Output: gráfico de barra 
    ''' 
    df_aux = (df.loc[:, ['Time_taken(min)','City']]
                .groupby(['City'])
                .agg({'Time_taken(min)': ['mean', 'std']}))        
    df_aux.columns = ['Avg_time', 'Std_time']            
    df_aux = df_aux.reset_index()
    figura = go.Figure()
    figura.add_trace(go.Bar(name='Control', x=df_aux['City'], y=df_aux['Avg_time'], error_y=dict(type='data', array=df_aux['Std_time'])))
    figura.update_layout(barmode='group')
    return figura
def tempo_sem_festival(df, oper):
    '''Esta função tem a responsabilidade retornar uma tabela
        Input: dataframe
        Output: tabela
    ''' 
    df_aux = (df.loc[:, ['Time_taken(min)', 'Festival']]
                .groupby(['Festival'])
                .agg({'Time_taken(min)': ['mean', 'std']}))
    df_aux.columns = ['Avg_time', 'Std_time']
    df_aux = df_aux.reset_index()
    df_aux_sem_festival = (np.round(df_aux
                             .loc[df_aux['Festival']=='No', oper],2))
    return df_aux_sem_festival
def tempo_com_festival(df, oper):
    '''Esta função tem a responsabilidade retornar uma tabela
        Input: dataframe
        Output: tabela
    ''' 
    df_aux = (df.loc[:, ['Time_taken(min)', 'Festival']]
                .groupby(['Festival'])
                .agg({'Time_taken(min)': ['mean', 'std']}))
    df_aux.columns = ['Avg_time', 'Std_time']
    df_aux = df_aux.reset_index()
    df_aux_com_festival = (np.round(df_aux
                             .loc[df_aux['Festival']=='Yes', oper],2))
    return df_aux_com_festival
def distancia(df):
    '''Esta função tem a responsabilidade retornar uma tabela
        Input: dataframe
        Output: tabela
    ''' 
    cols = ['Restaurant_latitude', 'Restaurant_longitude',
            'Delivery_location_latitude', 'Delivery_location_longitude']
    df['Distance'] = (df.loc[:, cols]
                        .apply(lambda x: haversine(
                        (x['Restaurant_latitude'], x['Restaurant_longitude']),
                        (x['Delivery_location_latitude'], x['Delivery_location_longitude'])), axis = 1))
    df_aux_distancia = (np.round(df['Distance']
                          .mean(),2))
    return df_aux_distancia
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

#VISÃO: RESTAURANTES

#==========================================================
#Barra laterial
#==========================================================
st.header('Marketplace - Visão Restaurantes')

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
    with st.container():#Criando 1º container grande==============================================================
        st.markdown('#### Visão Geral')
        
        col1, col2, col3, col4, col5, col6= st.columns(6)#Dividindo o container grande em 6 partes 

        with col1:
            df_aux_unicos = df['Delivery_person_ID'].nunique()
            col1.metric('Entr. únicos', df_aux_unicos)
        with col2:
            df_aux_distancia = distancia(df)
            col2.metric('Dist. méd. entregas', df_aux_distancia)
        with col3:
            df_aux_com_festival = tempo_com_festival(df, 'Avg_time')
            col3.metric('T. méd. entr. c/ fest.', df_aux_com_festival)
        with col4:
            df_aux_sem_festival = tempo_sem_festival(df, 'Avg_time')
            col4.metric('T. méd. entr. s/ fest.', df_aux_sem_festival)
        with col5:
            df_aux_com_festival = tempo_com_festival(df, 'Std_time')
            col5.metric('DesvPad entr. c/ fest.', df_aux_com_festival)  
        with col6:
            df_aux_sem_festival = tempo_sem_festival(df, 'Std_time')
            col6.metric('DesvPad entr. s/ fest.', df_aux_sem_festival)
        
    st.markdown('''---''')
    with st.container():#Criando 2º container grande==============================================================
        col1, col2 = st.columns(2) 

        with col1:
            figura = grafico_media_desvio_padrao (df) 
            st.markdown('##### Tempo médio de entrega por cidade')
            st.plotly_chart(figura, use_container_width=True)                    
        with col2:
            df_aux_distancia = grafico_media_desvio_padrao_distancia (df) 
            st.markdown('##### Distribuição da distância')
            st.dataframe(df_aux_distancia) 
            
    st.markdown('''---''')
    with st.container():#Criando 3º container grande==============================================================
               
        col1, col2 = st.columns(2)#Dividindo o container grande em 2 partes

        with col1:
            figura = grafico_distribuicao_tempo (df)
            st.markdown('##### Distribuição do tempo')
            st.plotly_chart(figura, use_container_width=True)        
        with col2:
            figura = grafico_sol_queimado (df)
            st.plotly_chart(figura, use_container_width=True)
    
    st.markdown('''---''')

    
