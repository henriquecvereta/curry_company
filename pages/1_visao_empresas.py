# -------------------------------
# Libraries
# -------------------------------
from haversine import haversine
import plotly.express as px
import plotly.graph_objects as go
import re
import streamlit as st
from PIL import Image
import folium
from streamlit_folium import folium_static
import pandas as pd

# -------------------------------
# Funções
# -------------------------------
def country_maps(df1):
    df_map = df1.head(100).copy()
    map = folium.Map()
    for index, location_info in df_map.iterrows():
        folium.Marker(
            [location_info['Delivery_location_latitude'], 
            location_info['Delivery_location_longitude']], 
            popup=location_info[['City', 'Road_traffic_density']]
        ).add_to(map)
    folium_static(map, width = 1200)
    return None


def order_share_by_week(df1):
    df_aux01 = df1.loc[:, ['ID', 'week_of_year']].groupby('week_of_year').count().reset_index()
    df_aux02 = df1.loc[:, ['Delivery_person_ID', 'week_of_year']].groupby('week_of_year').nunique().reset_index()

    df_aux = pd.merge(df_aux01, df_aux02, how ='inner', on = 'week_of_year')
    fig = df_aux['order_by_delivery'] = df_aux['ID'] / df_aux['Delivery_person_ID']

    fig = px.line(df_aux, x = 'week_of_year', y = 'order_by_delivery')
    return fig


def order_by_week(df1):
    df1['week_of_year'] = df1['Order_Date'].dt.strftime('%U')
    df_aux = df1.loc[:, ['ID', 'week_of_year']].groupby('week_of_year').count().reset_index()
    fig = px.line(df_aux, x = 'week_of_year', y = 'ID')
    return fig


def traffic_order_city(df1):
    df_aux = df1.loc[:, ['ID', 'City', 'Road_traffic_density']].groupby(['City', 'Road_traffic_density']).count().reset_index()
    df_aux = df_aux.loc[(df_aux['City'] != 'NaN') & (df_aux['Road_traffic_density'] != 'NaN'), :]
    fig = px.scatter(df_aux, x = 'City', y = 'Road_traffic_density', size = 'ID', color = 'City')
    return fig


def traffic_order_share(df1):
    df_aux = df1.loc[:, ['ID', 'Road_traffic_density']].groupby('Road_traffic_density').count().reset_index()
    df_aux['entregas_perc'] = df_aux['ID'] / df_aux['ID'].sum()
    fig = px.pie(df_aux, names = 'Road_traffic_density', values = 'entregas_perc')
    return fig


def orders_by_day(df1):
            cols = ['ID', 'Order_Date']
            # selecao de linhas
            df_aux = df1.loc[:, cols].groupby('Order_Date').count().reset_index()
            # desenhar grafico de linhas
            fig = px.bar(df_aux, x = 'Order_Date', y = 'ID')
            return fig


def clean_code(df1):
    ''' Esta função tem a responsabilidade de limpar o dataframe
        Tipos de limpeza:
        1. Remoção dos dados NaN
        2. Mudança do tipo da coluna de dados
        3. Remoção dos espaços das variáveis de texto
        4. Formação da coluna de datas
        5. Limpeza da coluna de tempo (remoção do texto da variável numérica)

        Input: Dataframe
        Output: Dataframe
    '''
    # Remover spaco da string
    df1['ID'] = df1['ID'].str.strip()
    df1['Delivery_person_ID'] = df1['Delivery_person_ID'].str.strip()

    # Excluir as linhas com a idade dos entregadores vazia
    # ( Conceitos de seleção condicional )
    linhas_vazias = df1['Delivery_person_Age'] != 'NaN '
    df1 = df1.loc[linhas_vazias, :]

    # Conversao de texto/categoria/string para numeros inteiros
    df1['Delivery_person_Age'] = df1['Delivery_person_Age'].astype( int )

    # Conversao de texto/categoria/strings para numeros decimais
    df1['Delivery_person_Ratings'] = df1['Delivery_person_Ratings'].astype( float )

    # Conversao de texto para data
    df1['Order_Date'] = pd.to_datetime( df1['Order_Date'], format='%d-%m-%Y' )

    # Remove as linhas da culuna multiple_deliveries que tenham o 
    # conteudo igual a 'NaN '
    linhas_vazias = df1['multiple_deliveries'] != 'NaN '
    df1 = df1.loc[linhas_vazias, :]
    df1['multiple_deliveries'] = df1['multiple_deliveries'].astype( int )

    # Comando para remover o texto de números
    df1 = df1.reset_index( drop=True )

    # Retirando os numeros da coluna Time_taken(min)
    df1['Time_taken(min)'] = df1['Time_taken(min)'].apply(lambda x: re.findall( r'\d+', x))
    df1['Time_taken(min)'] = df1['Time_taken(min)'].apply(lambda x: x[0])

    # Retirando os espaços da coluna Festival
    df1['Festival'] = df1['Festival'].str.strip()

    df1['City'] = df1['City'].str.strip()

    df1['Road_traffic_density'] = df1['Road_traffic_density'].str.strip()

    # Remove os NAN da coluna City
    df1 = df1.loc[df1['City']!='NaN']

    df1 = df1.loc[df1['Weatherconditions'] != 'conditions NaN']

    # Remove os NA que forem np.na
    df1 = df1.dropna()

    return df1

# ------------ Inicio da Estrutura lógica do código -----------------

# ----------------------
# Exibição app
# ------------------------
st.set_page_config(layout="wide")

# ----------------------
# import dataset
# ----------------------
df = pd.read_csv('datasets/train.csv')

# ------------------------
# Limpando os dados
# ------------------------
df1 = clean_code(df)


# ==================
# Barra Lateral
# ===================

st.header('Marketplace - Visão Cliente')

image_path = 'logo.jpeg'
image = Image.open(image_path)
st.sidebar.image(image, width=120)

st.sidebar.markdown("# Cury Company")
st.sidebar.markdown("## Fastest Delivery in Town")
st.sidebar.markdown("""---""")

st.sidebar.markdown("## Selecione uma data limite")
date_slider = st.sidebar.slider(
                                "Até qual valor?",
                                value = pd.datetime(2022, 3, 25),
                                min_value = pd.datetime(2022, 3, 11),
                                max_value = pd.datetime(2022, 4, 6),
                                format = 'DD-MM-YYYY'
                            )




st.sidebar.markdown("""---""")
traffic_options =    st.sidebar.multiselect(
                    "Quais as condições do transito", 
                    ['Low', 'Medium', 'High', 'Jam'],
                    default = ['Low', 'Medium', 'High', 'Jam']
                )

st.sidebar.markdown("---")
st.sidebar.markdown("### Powered by Henrique Vereta")

# Filtro de Data
selecao = df1['Order_Date'] < date_slider
df1 = df1.loc[selecao, :]

# Filtro de Transito
selecao = df1['Road_traffic_density'].isin(traffic_options)
df1 = df1.loc[selecao,:]



# ===================
# Layout no Streamlit
# ===================
tab1, tab2, tab3 = st.tabs(
                            ['Visão Gerencial',
                            'Visão Tática',
                            'Visão Geográfica']
                            )

with tab1:
    with st.container():
        st.markdown('# Orders by Day')
        fig = orders_by_day(df1)
        st.plotly_chart(fig, use_container_width=True)
        
    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            st.header('Traffic Order Share')
            fig = traffic_order_share(df1)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.header('Traffic Order City')
            fig = traffic_order_city(df1)
            st.plotly_chart(fig)
              
with tab2:
    with st.container():
        # criar a coluna de semana
        st.markdown("# Order by week")
        fig = order_by_week(df1)
        st.plotly_chart(fig, use_container_width=True)

    with st.container():
        st.markdown('# Order Share by Week')
        fig = order_share_by_week(df1)
        st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.markdown("# Country Maps")
    country_maps(df1)



