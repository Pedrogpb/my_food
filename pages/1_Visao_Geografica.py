#=============================================================================
# Bibliotecas
#=============================================================================
import pandas as pd
from haversine import haversine
import numpy as np
import plotly.express as px
import streamlit as st
from PIL import Image
import folium
#from streamlit_folium import folium_static
#from folium.plugins import MarkerCluster
#from folium.plugins import HeatMap
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


#====#====#====#====#====#====#====#====#====#====#====#====#====#====#====#====#====#====#====#====#====#====#
# SIDEBAR STREAMLIT
#====#====#====#====#====#====#====#====#====#====#====#====#====#====#====#====#====#====#====#====#====#====#

st.set_page_config(page_title = "MyFood - Análise Geográfica", page_icon =  "🍽️", layout = "centered")

# Sidebar
imagem = Image.open("logo.png")
st.sidebar.image(imagem, width=130)
st.sidebar.markdown("# MyFood 🍽️")
st.sidebar.markdown("### The Best Food in Town")
st.sidebar.markdown("""---""")

country_options = st.sidebar.multiselect("Filtrar por Países:", ["India", "Australia", "Brazil", "Canada", "Indonesia", "New Zeland", "Philippines", "Qatar", "Singapure", "South Africa", "Sri Lanka", "Turkey", "United Arab Emirates", "England", "USA"], default = ["India", "Brazil", "Philippines", "USA", "Canada", "New Zeland"])

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



#====#====#====#====#====#====#====#====#====#====#====#====#====#====#====#====#====#====#====#====#====#====#
# PÁGINA STREAMLIT
#====#====#====#====#====#====#====#====#====#====#====#====#====#====#====#====#====#====#====#====#====#====#



st.markdown("# Visão Geográfica🌎")
st.markdown("#####")

tab1, tab2 = st.tabs(["Análise por País", "Análise por Cidade"])

with tab1:
                     
    with st.container():
        st.markdown("")
        st.markdown("### Quantidade de Restaurantes Registrados por País")
        
        df1_rest_max = df1.loc[:, ["Country Name", "Restaurant ID"]].groupby("Country Name").count()
        df1_rest_max = df1_rest_max.sort_values("Restaurant ID", ascending = False).reset_index()
        df1_rest_max.columns = (["Paises", "Restaurantes Cadastrados"])
        fig = px.bar(df1_rest_max, x = "Paises", y = "Restaurantes Cadastrados")
        fig.update_layout(legend_title_text="", showlegend=False, xaxis_title = "", yaxis_title = "")
        fig.update_traces(texttemplate='%{y}', textposition='outside')
        st.plotly_chart(fig, use_container_width = True)

    with st.container():
        st.markdown("""---""")
        st.markdown("#### Quantidade de Cidades Registradas por País")
        
        df1_city_max = df1.loc[:, ["Country Name", "City"]].groupby("Country Name").nunique().reset_index()
        df1_city_max = df1_city_max.sort_values("City", ascending = False)
        df1_city_max.columns = (["Paises", "Cidades Cadastradas"])
        fig = px.bar(df1_city_max, x = "Paises", y = "Cidades Cadastradas")
        fig.update_layout(legend_title_text="", showlegend=False, xaxis_title = "", yaxis_title = "")
        fig.update_traces(texttemplate='%{y}', textposition='outside')
        st.plotly_chart(fig, use_container_width = True)


    with st.container():
        col1, col2 = st.columns(2)

        with col1:
            df1_rank_mean = df1.loc[:, ["Restaurant ID", "Country Name", "Aggregate rating"]].groupby("Country Name").mean("Aggregate rating")
            df1_rank_mean = df1_rank_mean.sort_values("Aggregate rating", ascending = False).reset_index()
            fig = px.bar(df1_rank_mean, x = "Country Name", y = "Aggregate rating")
            fig.update_layout(title = "Média de Avaliação de Restaurantes por País", title_x = 0.08, showlegend=False, xaxis_title = "", yaxis_title = "")
            fig.update_traces(texttemplate='%{y}', textposition='outside')
            fig.update_yaxes(range=[0, 5.5, ], tickformat=".1f")
            st.plotly_chart(fig, use_container_width = True)
            
        with col2:
            df1_aux = df1.explode("Cuisines_Separadas")
            df1_cozinhas = df1_aux.loc[:, ["Country Name", "Cuisines_Separadas"]].groupby("Country Name").nunique()
            df1_cozinhas = df1_cozinhas.sort_values("Cuisines_Separadas", ascending = False).reset_index()
            fig = px.bar(df1_cozinhas, x = "Country Name", y = "Cuisines_Separadas")
            fig.update_layout(title = "Quantidade de Culinárias por País", title_x = 0.19, showlegend=False, xaxis_title = "", yaxis_title = "")
            fig.update_traces(texttemplate='%{y}', textposition='outside')
            st.plotly_chart(fig, use_container_width = True)


with tab2:
    
    with st.container():

            st.markdown("### Top 10 Cidades com Tipos de Culinária Distinstas")
            
            df1_aux = df1.explode("Cuisines_Separadas")
            df1_cozinhas_unicas = df1_aux.loc[:, ["Country Name", "Cuisines_Separadas", "City"]].groupby(["Country Name", "City"]).nunique()
            df1_cozinhas_unicas = df1_cozinhas_unicas.sort_values("Cuisines_Separadas", ascending = False).reset_index()
            df1_cozinhas_unicas_top7 = df1_cozinhas_unicas.loc[0:10, :]
            fig = px.bar(df1_cozinhas_unicas_top7, x = "City", y = "Cuisines_Separadas", color = "Country Name")
            fig.update_layout(showlegend=True, legend_title = "Países", xaxis_title = "Cidades", yaxis_title = "")
            fig.update_traces(texttemplate='%{y}', textposition='outside')
            st.plotly_chart(fig, use_container_width = True)  
    
    
    with st.container():
        
        st.markdown("""---""")
        
        col1, col2 = st.columns(2)
        
        with col1:
            
            linhas_selecionadas = df1["Aggregate rating"] >= 4.5
            df1_rest_4 = df1.loc[linhas_selecionadas, ["Country Name", "City", "Aggregate rating"]].groupby(["Country Name", "City"]).count()
            df1_rest_4 = df1_rest_4.sort_values("Aggregate rating", ascending = False).reset_index()
            df1_rest_4_top5 = df1_rest_4.iloc[0:5, :]
            fig = px.bar(df1_rest_4_top5, x = "City", y = "Aggregate rating", color = "Country Name")
            fig.update_layout(title = "Top 5 Cidades com Melhores Restaurantes", title_x = 0.08, showlegend=True,legend_title = "Países", xaxis_title = "Cidades", yaxis_title = "")
            fig.update_traces(texttemplate='%{y}', textposition='outside')
            st.plotly_chart(fig, use_container_width = True)

        with col2:
            
            linhas_selecionadas = df1["Aggregate rating"] <= 2.5
            df1_rest_4 = df1.loc[linhas_selecionadas, ["Country Name", "City", "Aggregate rating"]].groupby(["Country Name", "City"]).count()
            df1_rest_4 = df1_rest_4.sort_values("Aggregate rating", ascending = False).reset_index()
            df1_rest_4_top5 = df1_rest_4.iloc[0:5, :]
            fig = px.bar(df1_rest_4_top5, x = "City", y = "Aggregate rating", color = "Country Name")
            fig.update_layout(title = "Top 5 Cidades com Piores Restaurantes", title_x = 0.08, showlegend=True,legend_title = "Países", xaxis_title = "Cidades", yaxis_title = "")
            fig.update_traces(texttemplate='%{y}', textposition='outside')
            st.plotly_chart(fig, use_container_width = True)
                      
            
            
    #with st.container():
        
        #linhas_selecionadas = df1["Has Table booking"] == 1
        #df1_rest_reserva = df1.loc[linhas_selecionadas, ["Has Table booking", "City"]].groupby("City").count()
        #df1_rest_reserva = df1_rest_reserva.sort_values("Has Table booking", ascending = False).reset_index()         
        #df1_rest_reserva = df1_rest_reserva.loc[0:4, :]
        #fig = px.bar(df1_rest_reserva, x = "City", y = "Has Table booking")
        #st.plotly_chart(fig, use_container_widht = True)
            
            
    #with st.container():
        #linhas_selecionadas = df1["Is delivering now"] == 1
        #df1_rest_entrega = df1.loc[linhas_selecionadas, ["Is delivering now", "City"]].groupby("City").count()
        #df1_rest_entrega = df1_rest_entrega.sort_values("Is delivering now", ascending = False).reset_index()
        #df1_rest_entrega = df1_rest_entrega.loc[0:4, :]
        #fig = px.bar(df1_rest_entrega, x = "City", y = "Is delivering now")
        #st.plotly_chart(fig, use_container_widht = True)
            
    #with st.container():
        #linhas_selecionadas = df1["Has Online delivery"] == 1
        #df1_rest_online = df1.loc[linhas_selecionadas, ["Has Online delivery", "City"]].groupby("City").count()
        #df1_rest_online = df1_rest_online.sort_values("Has Online delivery", ascending = False).reset_index()
        #df1_rest_online = df1_rest_online.loc[0:4, :]
        #fig = px.bar(df1_rest_online, x = "City", y = "Has Online delivery")
        #st.plotly_chart(fig, use_container_widht = True)
        
       #with st.container():
        
        #col1, col2= st.columns(2)
        
        
        #with col1:
                                           
            
            #df1_registro_rest = df1.loc[:, ["Restaurant ID", "City", "Country Name"]].groupby(["Country Name", "City"]).count()
            
            #df1_registro_rest = df1_registro_rest.sort_values("City", ascending = True).reset_index()            
            
            #linhas_selecionadas = df1_registro_rest["Country Name"] == "India"
            
            #df1_registro_rest_ind = df1_registro_rest.loc[linhas_selecionadas, ["Restaurant ID", "City"]].groupby("City").sum()
            #df1_registro_rest_ind = df1_registro_rest_ind.sort_values("Restaurant ID", ascending = False).reset_index()
            #df1_registro_rest_ind
            
            
            #linhas_selecionadas = df1_registro_rest["Country Name"] == "USA"
            #df1_registro_rest_usa = df1_registro_rest.loc[linhas_selecionadas, ["Restaurant ID", "City"]].groupby("City").sum()
            
            #df1_registro_rest_usa = df1_registro_rest_usa.sort_values("Restaurant ID", ascending = False).reset_index() 
            #df1_registro_rest_usa
            
            
            #linhas_selecionadas = df1_registro_rest["Country Name"] == "Brazil"
            #df1_registro_rest_bra = df1_registro_rest.loc[linhas_selecionadas, ["Restaurant ID", "City"]].groupby("City").sum()
            
            #df1_registro_rest_bra = df1_registro_rest_bra.sort_values("Restaurant ID", ascending = False).reset_index() 
            #df1_registro_rest_bra
            
            
            #linhas_selecionadas = df1_registro_rest["Country Name"] == "Philippines"
            #df1_registro_rest_phi = df1_registro_rest.loc[linhas_selecionadas, ["Restaurant ID", "City"]].groupby("City").sum()
            
            #df1_registro_rest_phi = df1_registro_rest_phi.sort_values("Restaurant ID", ascending = False).reset_index() 
            #df1_registro_rest_phi
            
            # Sera que dá pra fazer um FOR?

            
    #city_max = df1_city_max["Country Name"][df1_city_max["City"].idxmax()]

    # st.metric("Pais com mais cidades", city_max)

    #df1_rest_max = df1.loc[:, ["Country Name", "Restaurant Name"]].groupby("Country Name").count().sort_values("Country Name", ascending = False).reset_index()
    #rest_max = df1_rest_max["Country Name"][df1_rest_max["Restaurant Name"].idxmax()]

    #st.write(rest_max)
            


    #with st.container():    
        #st.markdown("""---""")
        #df1_aux_mapa = df1.loc[0:300, ["Restaurant Name", "Latitude", "Longitude", "Average Cost for two in Dollar"]].reset_index(drop=True)

        #mapa = folium.Map()
        #marker_cluster = MarkerCluster().add_to(mapa)

        #for index, row in df1_aux_mapa.iterrows():
            #popup_text = "{}<br>Preço por Prato: ${:.2f}".format(row['Restaurant Name'], row['Average Cost for two in Dollar'])
            #folium.CircleMarker(
                #location=[row["Latitude"], row["Longitude"]],
                #radius=5,  # Tamanho da bolha
                #popup=popup_text,
                #fill=True,
            #).add_to(marker_cluster)

        #folium_static(mapa, width=700, height=450)


    #with st.container():
        #df1_votes_mean = df1.loc[:, ["Restaurant ID", "Country Name", "Votes"]].groupby("Country Name").mean("Votes")
        #df1_votes_mean = df1_votes_mean.sort_values("Votes", ascending = False).reset_index()
        #fig = px.bar(df1_votes_mean, x = "Country Name", y = "Votes")
        #fig.update_layout(title = "Quantidade Média de Avaliações por País", title_x = 0.08, showlegend=False, xaxis_title = "", yaxis_title = "")
        #fig.update_traces(marker_color = cor, texttemplate='%{y}', textposition='outside')
        #fig.update_yaxes(tickformat=".0f")
        #st.plotly_chart(fig, use_container_width = True)


            #fig = px.bar(df1_cost2, x = "Country Name", y = "Average Cost for two in Dollar")
            #fig.update_layout(title = "Valor Médio de Prato para Dois por País", title_x = 0.15, showlegend=False, xaxis_title = "", yaxis_title = "Dollar ($)")
            #fig.update_traces(marker_color = cor, texttemplate='%{y}', textposition='outside')
            #fig.update_yaxes(tickformat=".0f")
            #st.plotly_chart(fig, use_container_width = True)


    #with st.container():
        #col1, col2 = st.columns(2)

        #with col1:
            #linhas_selecionadas = df1["Has Table booking"] == 1
            #df1_delivery = df1.loc[linhas_selecionadas, ["Restaurant ID", "Country Name", "Has Table booking"]].groupby("Country Name").count()
            #df1_delivery = df1_delivery.sort_values("Country Name", ascending = False).reset_index()
            #fig = px.bar(df1_delivery,  x = "Country Name", y = "Has Table booking")
            #fig.update_traces(marker_color = cor, texttemplate='%{y}', textposition='outside')
            #st.plotly_chart(fig, use_container_width = True)

        #with col2:
            #df1_votes = df1.loc[:, ["Restaurant ID", "Country Name", "Votes"]].groupby("Country Name").sum("Votes")
            #df1_votes = df1_votes.sort_values("Country Name", ascending = False).reset_index()
            #fig = px.bar(df1_votes, x = "Country Name", y = "Votes")
            #fig.update_traces(marker_color = cor, texttemplate='%{y}', textposition='outside')
            #st.plotly_chart(fig, use_container_width = True)

    #with st.container():
        #col1, col2 = st.columns(2)

        #with col1:       
            #df1_rest = df1.loc[:, ["Country Name", "Aggregate rating", "Restaurant ID"]]
            #df1_rest_4_star = df1_rest[df1_rest["Aggregate rating"] > 4]
            #df1_rest_4_star = df1_rest_4_star.groupby("Country Name").count()
            #df1_rest_4_star = df1_rest_4_star.sort_values("Restaurant ID", ascending = False).reset_index()
            #fig = px.bar(df1_rest_4_star, x = "Country Name", y = "Restaurant ID")
            #fig.update_layout(title = "Restaurantes Avaliados c", title_x = 0.2, showlegend=False, xaxis_title = "", yaxis_title = "")
            #fig.update_traces(marker_color = cor, texttemplate='%{y}', textposition='outside')
            #st.plotly_chart(fig, use_container_width = True)


        #with col2:
            #linhas_selecionadas = df1["Has Online delivery"] == 1
            #df1_delivery = df1.loc[linhas_selecionadas, ["Restaurant ID", "Country Name", "Has Online delivery"]].groupby("Country Name").count()
            #df1_delivery = df1_delivery.sort_values("Country Name", ascending = False).reset_index()
            #fig = px.bar(df1_delivery,  x = "Country Name", y = "Has Online delivery")
            #fig.update_traces(marker_color = cor, texttemplate='%{y}', textposition='outside')
            #st.plotly_chart(fig, use_container_width = True)