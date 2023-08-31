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

st.set_page_config(page_title = 'Visao Empresa', layout = 'wide')#Deixa o objeto ocupar toda a extensão da tela

#==========================================================
#Funções
#==========================================================
def mapa_paises(df):     
    '''Esta função tem a responsabilidade retornar um mapa
        Input: dataframe
        Output: mapa    
    '''   
    df_aux = (df.loc[:, ['City', 'Road_traffic_density', 'Delivery_location_latitude', 'Delivery_location_longitude']]
                .groupby(['City', 'Road_traffic_density'])
                .median()
                .reset_index())
    df_aux = df_aux.loc[df_aux['City']!='NaN', :]
    df_aux = df_aux.loc[df_aux['Road_traffic_density']!='NaN', :]
    map = folium.Map(zoom_start=11)
    for index, location_info in df_aux.iterrows():
      folium.Marker([location_info['Delivery_location_latitude'],
                     location_info['Delivery_location_longitude']],
               popup=location_info[['City', 'Road_traffic_density']]).add_to(map)
    folium_static(map, width=924, height=600)
    return None
def pedidos_distribuidos_semana(df):
    '''Esta função tem a responsabilidade retornar um gráfico de linha
        Input: dataframe
        Output: gráfico de linha   
    ''' 
    df['Week'] = df['Order_Date'].dt.strftime('%U')
    df_aux1 = (df.loc[:, ['ID', 'Week']]
                .groupby(['Week'])
                .count()
                .reset_index())
    df_aux2 = (df.loc[:, ['Delivery_person_ID', 'Week']]
                .groupby(['Week'])
                .nunique()
                .reset_index())
    df_aux = pd.merge(df_aux1, df_aux2, how ='inner')
    df_aux['Order_by_delivery'] = df_aux['ID'] / df_aux['Delivery_person_ID']
    figura = px.line( df_aux, x='Week', y='Order_by_delivery' )
    return figura
def pedidos_por_semana(df):  
    '''Esta função tem a responsabilidade retornar um gráfico de linha
        Input: dataframe
        Output: gráfico de linha   
    ''' 
    df['Week'] = df['Order_Date'].dt.strftime('%U')
    df_aux = (df.loc[:,['ID', 'Week']]
                .groupby(['Week'])
                .count()
                .reset_index())
    figura = px.line(df_aux, x='Week', y='ID')
    return figura
def pedidos_transito_e_cidade(df):
    '''Esta função tem a responsabilidade retornar um gráfico de bolha
        Input: dataframe
        Output: gráfico de bolha  
    '''
    df_aux = (df.loc[:, ['ID', 'City', 'Road_traffic_density']]
                .groupby(['City', 'Road_traffic_density'])
                .count()
                .reset_index())
    df_aux = df_aux.loc[df_aux['City']!='NaN', :]
    df_aux = df_aux.loc[df_aux['Road_traffic_density']!='NaN', :]
    figura = px.scatter(df_aux, x='City', y='Road_traffic_density', size='ID', color = 'City')
    return figura
def pedidos_e_transito(df):
    '''Esta função tem a responsabilidade retornar um gráfico de pizza
        Input: dataframe
        Output: gráfico de pizza  
    '''
    df_aux = (df.loc[df['Road_traffic_density']!='NaN', ['ID', 'Road_traffic_density']]
                .groupby(['Road_traffic_density'])
                .count()
                .reset_index())
    df_aux['Percent'] = 100 * df_aux['ID'] / df_aux['ID'].sum()
    figura = px.pie(df_aux, values= 'Percent', names='Road_traffic_density')
    return figura
def metricas_pedido(df):
    '''Esta função tem a responsabilidade retornar um gráfico de barra
        Input: dataframe
        Output: gráfico de barra  
    '''
    df_aux = (df.loc[:, ['ID', 'Order_Date']]
                .groupby(['Order_Date'])
                .count()
                .reset_index())#.reset_index é por causa do gráfico    
    figura = px.bar(df_aux, x='Order_Date', y='ID')    
    return figura
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
df1 = pd.read_csv('../dataset/train.csv')

#Fazendo uma cópia do arquivo original
df = df1.copy()

#Limpando os dados
df = limpar_codigo(df)

#VISÃO: EMPRESA

#==========================================================
#Barra laterial
#==========================================================
st.header('Marketplace - Visão Cliente')

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
tab1, tab2, tab3 = st.tabs(['Visão Gerencial', 'Visão Tática', 'Visão Geográfica'])

with tab1:
    with st.container():
        figura = metricas_pedido(df)
        st.markdown('#### Pedidos por dia')
        st.plotly_chart(figura, use_container_width=True)  
        
    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            figura = pedidos_e_transito(df)
            st.markdown('#### Tipos de trânsito')
            st.plotly_chart(figura, use_container_width=True)           
                
        with col2:
            figura = pedidos_transito_e_cidade(df)
            st.markdown('#### Pedidos por trânsito e cidade')
            st.plotly_chart(figura, use_container_width=True)

with tab2:
    with st.container():
        figura = pedidos_por_semana(df)
        st.markdown('#### Pedidos por semana')
        st.plotly_chart(figura, use_container_width=True)        
    
    with st.container():
        figura = pedidos_distribuidos_semana(df)
        st.markdown('#### Entrega de pedidos por semana')
        st.plotly_chart(figura, use_container_width=True)        

with tab3:
    st.markdown('#### Mapa de países')
    mapa_paises(df)
