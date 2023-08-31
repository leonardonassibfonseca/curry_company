#==========================================================
#Bibliotécas
#==========================================================
import streamlit as st
from PIL import Image

st.set_page_config(page_title = 'Home')

#image_path = 'C:/Users/Leonardo/curso_cientista_de_dados/Repos/Python_zero_ao_ds/arquivos_python/'
image = Image.open('logo.png')#Imagem precisa estar na mesma pasta do arquivo .PY
st.sidebar.image(image, width = 120)

st.sidebar.markdown('## Cury Company')
st.sidebar.markdown('## A mais rápida entrega da cidade!')
st.sidebar.markdown('''---''')

st.write('# Curry Company Growth Dashboard')

st.markdown(
    '''
    Growth Dashboard foi construído para acompanhar as métricas de crescimento dos Entregadores e Restaurantes.
    ### Como utilizar este Growth Dashboard?
    - Visão Empresa:
        - Visão Gerencial: Métricas gerais de comportamento;
        - Visão Tática: Indicadores semanais de crescimento;
        - Visão Geográfica: Insights de geolocalização.
    - Visão Entregador:
        - Acompanhamento dos indicadores semanais de crescimento.
    - Visão Restaurante:
        - Indicadores semanais de crescimento dos restaurantes.
    Ask for help
    - Time de Data Science do Discord.
    ''')