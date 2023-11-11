#=============================================================================
# Bibliotecas
#=============================================================================
import pandas as pd
import numpy as np
import plotly.express as px
import streamlit as st
from PIL import Image
import folium
from streamlit_folium import folium_static
#from folium.plugins import MarkerCluster
#import plotly.graph_objects as go

#=============================================================================
# FUNÇÕES
#=============================================================================

def convert_df(df):
    return df.to_csv().encode('utf-8')

#-----------------------------

def clean_data(df):
    df = df.drop_duplicates(subset = "Restaurant ID", keep = "first")
    df = df.reset_index(drop = True)
    df = df.loc[df["Average Cost for two"] != 0, :]
    df["Cuisines_Separadas"] = df["Cuisines"].str.split(", ")
    return df

#====#====#====#====#====#====#====#====#====#====#====#====#====#====#====#====#====#====#====#====#====#====#
# CÓDIGO
#====#====#====#====#====#====#====#====#====#====#====#====#====#====#====#====#====#====#====#====#====#====#

# Importando dataset
df = pd.read_csv("dataset/zomato.csv")                
df_copy = df.copy()

# Limpeza de dados
df1 = clean_data(df)
df1_copy = df1.copy()

# Converção moedas para Dollar 

Average_Cost2_Dollar = []

for index, i in df1.iterrows():
    
    if i["Currency"] == "Botswana Pula(P)":
        cost2_dollar = i["Average Cost for two"] * 0.0726143
        
    elif i["Currency"] == "Brazilian Real(R$)":
        cost2_dollar = i["Average Cost for two"] * 0.202218
        
    elif i["Currency"] == "Indian Rupees(Rs.)":
        cost2_dollar = i["Average Cost for two"] * 0.0120385
    
    else:
        cost2_dollar = i["Average Cost for two"]
        
    Average_Cost2_Dollar.append(cost2_dollar)
    
df1["Average Cost for two in Dollar"] = Average_Cost2_Dollar
df1["Average Cost for two in Dollar"] = np.round(df1["Average Cost for two in Dollar"], 0)
        
# Adicionando informações ao dataframe

COUNTRIES = {
1: "India",
14: "Australia",
30: "Brazil",
37: "Canada",
94: "Indonesia",
148: "New Zeland",
162: "Philippines",
166: "Qatar",
184: "Singapure",
189: "South Africa",
191: "Sri Lanka",
208: "Turkey",
214: "United Arab Emirates",
215: "England",
216: "USA",
}

df1["Country Name"] = df1["Country Code"].map(COUNTRIES)

#----------------------
COLORS = {
"3F7E00": "darkgreen",
"5BA829": "green",
"9ACD32": "lightgreen",
"CDD614": "orange",
}

#====#====#====#====#====#====#====#====#====#====#====#====#====#====#====#====#====#====#====#====#====#====#
# CÓDIGO STREAMLIT
#====#====#====#====#====#====#====#====#====#====#====#====#====#====#====#====#====#====#====#====#====#====#

st.set_page_config(page_title = "MyFood - Home", page_icon =  "🍽️", layout = "centered", initial_sidebar_state = "expanded")

# Sidebar
imagem = Image.open("logo.png")
st.sidebar.image(imagem, width=152)
st.sidebar.markdown("# MyFood 🍽️")
st.sidebar.markdown("### The Best Food in Town")
st.sidebar.markdown("""---""")

country_options = st.sidebar.multiselect("Filtrar por Países:", ["India", "Australia", "Brazil", "Canada", "Indonesia", "New Zeland", "Philippines", "Qatar", "Singapure", "South Africa", "Sri Lanka", "Turkey", "United Arab Emirates", "England", "USA"], default = ["India", "Australia", "Brazil", "Canada", "Indonesia", "New Zeland", "Philippines", "Qatar", "Singapure", "South Africa", "Sri Lanka", "Turkey", "United Arab Emirates", "England", "USA"])

linhas_selecionadas = df1["Country Name"].isin(country_options)
df1 = df1.loc[linhas_selecionadas, :]
st.sidebar.markdown("""---""")
st.sidebar.write("Baixar dados:")
csv = convert_df(df1)
st.sidebar.download_button("Download data as CSV", data = csv, file_name = 'dataframe_pedrogarcia.csv', mime='text/csv')


# Sidebar (with CSS)
st.sidebar.markdown("""
<style>
    .sidebar-text {
        text-align: center;
        font-size: 10px;
    }
</style>
""", unsafe_allow_html=True)

st.sidebar.markdown('<p class="sidebar-text">Powered by Pedro Garcia.</p>', unsafe_allow_html=True)



# Página

st.markdown("# MyFood 🍽️")
st.markdown("## O melhor lugar para encontrar seu mais novo restaurante favorito!")
st.markdown("#### Atingimos as seguintes marcas em nossa plataforma:")



with st.container():
        
    col1, col2, col3, col4, col5 = st.columns(5)
        
    with col1:
        qnt_restaurantes_unicos = len(df1.loc[:,"Restaurant ID"].unique())
        qnt_restaurantes_unicos_formatada = f"{qnt_restaurantes_unicos / 1000:.1f} Mil"
        st.metric("Restaurantes", qnt_restaurantes_unicos_formatada)
        
    with col2:
        qnt_paises_unicos = len(df1.loc[:,"Country Code"].unique())
        st.metric("Países", qnt_paises_unicos)
            
    with col3:
        qnt_cidades_unicas = len(df1.loc[:, "City"].unique())
        st.metric("Cidades", qnt_cidades_unicas)
            
    with col4:
        qnt_avaliacoes = df1.loc[:, "Votes"].sum()
        qnt_avaliacoes_formatada = f"{qnt_avaliacoes / 1000000:.1f} M"
        st.metric("Avaliações", qnt_avaliacoes_formatada)
            
    with col5:
        df_aux = df1.explode("Cuisines_Separadas")
        qnt_culinarias = len(df_aux.loc[:, "Cuisines_Separadas"].unique())
        st.metric("Tipos de Culinária", qnt_culinarias)

        
with st.container():    
    st.markdown("""---""")
    df1_aux_mapa = df1.loc[:, ["Restaurant ID", "Restaurant Name", "Longitude", "Latitude"]].reset_index(drop = True)
    mapa = folium.Map()
    marker_cluster = MarkerCluster().add_to(mapa)
        
    for index, i in df1_aux_mapa.iterrows():
        folium.Marker([i["Latitude"], i["Longitude"]]).add_to(marker_cluster)
        
    folium_static(mapa, width = 700, height = 450)

