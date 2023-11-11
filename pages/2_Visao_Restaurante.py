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
from streamlit_folium import folium_static
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

st.set_page_config(page_title = "MyFood - Análise Restaurantes", page_icon =  "🍽️", layout = "centered")

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

st.markdown("# Visão Culinárias 🍽️")
st.markdown("""---""")

with st.container():
    st.markdown("### Top 10 Melhores tipos de Culinária")
    
    df1_aux = df1.explode("Cuisines_Separadas")
    df1_votes_cuisines = df1_aux.loc[:, ["Cuisines_Separadas", "Restaurant Name", "Aggregate rating"]].groupby("Cuisines_Separadas").mean("Aggregate rating")
    df1_votes_cuisines = df1_votes_cuisines.sort_values("Aggregate rating", ascending = False).reset_index()
    df1_votes_cuisines = df1_votes_cuisines.loc[1:10, :]
    fig = px.bar(df1_votes_cuisines, x = "Cuisines_Separadas", y = "Aggregate rating")
    fig.update_layout(legend_title_text="", showlegend=False, xaxis_title = "", yaxis_title = "")
    fig.update_traces(texttemplate='%{y}', textposition='outside')
    fig.update_yaxes(range=[0, 5.5, ], tickformat=".2f")
    st.plotly_chart(fig, use_container_width = True)


with st.container():
    st.markdown("""---""")
    
col1, col2 = st.columns(2)

with col1:

    with st.container():
        df1_aux = df1.explode("Cuisines_Separadas")
        linhas_selecionadas = df1_aux["Cuisines_Separadas"] == "Healthy Food"
        df1_rest_hel = df1_aux.loc[linhas_selecionadas, ["Cuisines_Separadas", "Restaurant Name", "Aggregate rating", "Country Name"]].sort_values("Aggregate rating", ascending = False).reset_index(drop=True)
        df1_rest_hel = df1_rest_hel.loc[0:4, :]
        fig = px.bar(df1_rest_hel, x = "Restaurant Name", y = "Aggregate rating", color = "Country Name")
        fig.update_layout(title = "Top 5 Restaurantes Suadáveis", title_x = 0.1, xaxis_title = "", yaxis_title = "", legend_title_text= "Países")
        fig.update_traces(texttemplate='%{y}', textposition='outside')
        fig.update_yaxes(range=[0, 5.8, ], tickformat=".2f")
        st.plotly_chart(fig, use_container_width = True)

with col2:
    
    with st.container():
        df1_aux = df1.explode("Cuisines_Separadas")
        linhas_selecionadas = df1_aux["Cuisines_Separadas"] == "Japanese"
        df1_rest_bra = df1_aux.loc[linhas_selecionadas, ["Cuisines_Separadas", "Restaurant Name", "Aggregate rating", "Country Name"]].sort_values("Aggregate rating", ascending = False).reset_index(drop=True)
        df1_rest_bra = df1_rest_bra.loc[0:4, :]
        fig = px.bar(df1_rest_bra, x = "Restaurant Name", y = "Aggregate rating", color = "Country Name")
        fig.update_layout(title = "Top 5 Restaurantes Japoneses", title_x = 0.1, xaxis_title = "", yaxis_title = "", legend_title_text= "Países")
        fig.update_traces(texttemplate='%{y}', textposition='outside')
        fig.update_yaxes(range=[0, 5.8, ], tickformat=".2f")
        st.plotly_chart(fig, use_container_width = True)


with st.container():
    st.markdown("""---""")
        
col1, col2 = st.columns(2)

with col1:
    
    with st.container():
        df1_aux = df1.explode("Cuisines_Separadas")
        linhas_selecionadas = df1_aux["Cuisines_Separadas"] == "French"
        df1_rest_bra = df1_aux.loc[linhas_selecionadas, ["Cuisines_Separadas", "Restaurant Name", "Aggregate rating", "Country Name"]].sort_values("Aggregate rating", ascending = False).reset_index(drop=True)
        df1_rest_bra = df1_rest_bra.loc[0:4, :]
        fig = px.bar(df1_rest_bra, x = "Restaurant Name", y = "Aggregate rating", color = "Country Name")
        fig.update_layout(title = "Top 5 Restaurantes Franceses", title_x = 0.1, xaxis_title = "", yaxis_title = "", legend_title_text= "Países")
        fig.update_traces(texttemplate='%{y}', textposition='outside')
        fig.update_yaxes(range=[0, 5.8, ], tickformat=".2f")
        st.plotly_chart(fig, use_container_width = True)
        
        
with col2:
    
    with st.container():
        df1_aux = df1.explode("Cuisines_Separadas")
        linhas_selecionadas = df1_aux["Cuisines_Separadas"] == "Mexican"
        df1_rest_bra = df1_aux.loc[linhas_selecionadas, ["Cuisines_Separadas", "Restaurant Name", "Aggregate rating", "Country Name"]].sort_values("Aggregate rating", ascending = False).reset_index(drop=True)
        df1_rest_bra = df1_rest_bra.loc[0:4, :]
        fig = px.bar(df1_rest_bra, x = "Restaurant Name", y = "Aggregate rating", color = "Country Name")
        fig.update_layout(title = "Top 5 Restaurantes Mexicanos", title_x = 0.1, xaxis_title = "", yaxis_title = "", legend_title_text= "Países")
        fig.update_traces(texttemplate='%{y}', textposition='outside')
        fig.update_yaxes(range=[0, 5.8, ], tickformat=".2f")
        st.plotly_chart(fig, use_container_width = True)
        
### FAZER GRAFICO DE BARRAS
        
        
        
    
#   with st.container():
#       df1_pedidos_rating = df1.loc[:, ["Aggregate rating", "Has Online delivery"]].groupby("Has Online delivery").agg(["mean", "std","count"])
#       df1_pedidos_rating = df1_pedidos_rating.reset_index(drop = True)
#       df1_pedidos_rating


#   with st.container():
#       df1_reserva_cost2 = df1.loc[:, ["Aggregate rating", "Has Table booking"]].groupby("Has Table booking").agg(["mean", "std","count"])
#       df1_reserva_cost2 = df1_reserva_cost2.reset_index(drop = True)
#       df1_reserva_cost2


#   with st.container():
#       df1_aux = df1.explode("Cuisines_Separadas")
#       linhas_selecionadas = ((df1_aux["Cuisines_Separadas"] == "Japanese") | (df1_aux["Cuisines_Separadas"] == "BBQ")) & (df1_aux["Country Name"] == "USA")
#       df1_jap_bbq_usa = df1_aux.loc[linhas_selecionadas, ["Cuisines_Separadas", "Country Name", "Average Cost for two"]].groupby("Cuisines_Separadas").agg(["mean", "std","count"])
#       df1_jap_bbq_usa

######## 
# USAR NA ABA AVERAGE COST
#####

#  with st.container():
#       df1_aux = df1.explode("Cuisines_Separadas")
#       df1_cost2_cuisines = df1_aux.loc[:, ["Cuisines_Separadas", "Restaurant Name", "Average Cost for two"]].groupby("Cuisines_Separadas").mean("Average Cost for two")
#       df1_cost2_cuisines = df1_cost2_cuisines.sort_values("Average Cost for two", ascending = False).reset_index()
#       df1_cost2_cuisines


#   with st.container():
#       df1_aux = df1.explode("Cuisines_Separadas")
#       df1_cuisines_barata = df1_aux.loc[:, ["Cuisines_Separadas", "Average Cost for two in Dollar", "Country Name"]].groupby("Cuisines_Separadas").agg(["mean", "std","count"])
#       df1_cuisines_barata   

#   with st.container():
#       df1_rest_cost2 = df1.loc[:,["Restaurant Name", "Average Cost for two"]].sort_values("Average Cost for two", ascending = False).reset_index(drop=True)
#       df1_rest_cost2 = df1_rest_cost2.loc[0:4, :]
#       df1_rest_cost2

######################################3


# with st.container():
   # df1_aux = df1.explode("Cuisines_Separadas")
    #linhas_selecionadas = (df1_aux["Cuisines_Separadas"] == "Brazilian") & (df1_aux["Country Name"] == "Brazil")
    #df1_rest_bral_2 = df1_aux.loc[linhas_selecionadas, ["Restaurant Name", "Aggregate rating"]]
    #df1_rest_bral_2
    
    
 #  with st.container():
  #     df1_rest_votes = df1.loc[:, ["Country Name", "Restaurant Name", "Votes"]].sort_values("Votes", ascending = False).reset_index(drop=True)
   #    df1_rest_votes = df1_rest_votes.loc[0:50, :]
    #   df1_rest_votes
    
    


#   with st.container():
    
    #ol1, col2 = st.columns(2)

    #ith col1:

       #with st.container():
        #   df1_aux = df1.explode("Cuisines_Separadas")
         #  linhas_selecionadas = (df1_aux["Cuisines_Separadas"] == "Italian")
          # df1_italian_votes = df1_aux.loc[linhas_selecionadas, ["Aggregate rating", "Restaurant Name"]].sort_values("Aggregate rating", ascending = False)
          # df1_italian_votes = df1_italian_votes.reset_index(drop = True)
          # a = df1_italian_votes["Restaurant Name"][df1_italian_votes["Aggregate rating"].idxmax()]
          # df1_italian_votes
        #   a
   #with col2:
   #    a

#   with st.container():
 #      df1_aux = df1.explode("Cuisines_Separadas")
  #     linhas_selecionadas = (df1_aux["Cuisines_Separadas"] == "Italian")
   #    df1_italian_votes_menor = df1_aux.loc[linhas_selecionadas, ["Aggregate rating", "Restaurant Name"]].sort_values("Aggregate rating", ascending = True)
    #   df1_italian_votes_menor = df1_italian_votes_menor.reset_index(drop = True)
     #  a = df1_italian_votes_menor["Restaurant Name"][df1_italian_votes_menor["Aggregate rating"].idxmin()]
      # df1_italian_votes_menor
       #a

#   with st.container():
 #      df1_aux = df1.explode("Cuisines_Separadas")
  #     linhas_selecionadas = (df1_aux["Cuisines_Separadas"] == "American")
   #    df1_american_votes = df1_aux.loc[linhas_selecionadas, ["Aggregate rating", "Restaurant Name"]].sort_values("Aggregate rating", ascending = False)
    #   df1_american_votes = df1_american_votes.reset_index(drop = True)
     #  a = df1_american_votes["Restaurant Name"][df1_american_votes["Aggregate rating"].idxmax()]
      # df1_american_votes
       #a

#   with st.container():
 #      df1_aux = df1.explode("Cuisines_Separadas")
  #     linhas_selecionadas = (df1_aux["Cuisines_Separadas"] == "American")
   #    df1_american_votes_menor = df1_aux.loc[linhas_selecionadas, ["Cuisines_Separadas", "Aggregate rating", "Restaurant Name"]].sort_values("Aggregate rating", ascending = True)
    #   df1_american_votes_menor = df1_american_votes_menor.reset_index(drop = True)
     #  a = df1_american_votes_menor["Restaurant Name"][df1_american_votes_menor["Aggregate rating"].idxmin()]
      # df1_american_votes_menor
       #a

#   with st.container():
 #      df1_aux = df1.explode("Cuisines_Separadas")
  #     linhas_selecionadas = (df1_aux["Cuisines_Separadas"] == "Arabian")
   #    df1_arabian_votes = df1_aux.loc[linhas_selecionadas, ["Restaurant ID", "Aggregate rating", "Restaurant Name"]].sort_values("Aggregate rating", ascending = False)
    #   df1_arabian_votes = df1_arabian_votes.reset_index(drop = True)
     #  a = df1_arabian_votes["Restaurant Name"][df1_arabian_votes["Aggregate rating"].idxmax()]
      # df1_arabian_votes
       #a

#   with st.container():
 #      df1_aux = df1.explode("Cuisines_Separadas")
  #     linhas_selecionadas = (df1_aux["Cuisines_Separadas"] == "Arabian")
   #    df1_arabian_votes_menor = df1_aux.loc[linhas_selecionadas, ["Restaurant ID", "Aggregate rating", "Restaurant Name"]].sort_values("Aggregate rating", ascending = True)
    #   df1_arabian_votes_menor = df1_arabian_votes_menor.reset_index(drop = True)
     #  a = df1_arabian_votes_menor["Restaurant Name"][df1_arabian_votes_menor["Aggregate rating"].idxmin()]
      # df1_arabian_votes_menor
       #a

#   with st.container():
 #      df1_aux = df1.explode("Cuisines_Separadas")
  #     linhas_selecionadas = (df1_aux["Cuisines_Separadas"] == "Japanese")
   #    df1_japonese_votes = df1_aux.loc[linhas_selecionadas, ["Restaurant ID", "Aggregate rating", "Restaurant Name"]].sort_values("Aggregate rating", ascending = False)
    #   df1_japonese_votes = df1_japonese_votes.reset_index(drop = True)
     #  a = df1_japonese_votes["Restaurant Name"][df1_japonese_votes["Aggregate rating"].idxmax()]
      # df1_japonese_votes
       #a

#   with st.container():
 #      df1_aux = df1.explode("Cuisines_Separadas")
  #     linhas_selecionadas = (df1_aux["Cuisines_Separadas"] == "Japanese")
   #    df1_japonese_votes_menor = df1_aux.loc[linhas_selecionadas, ["Restaurant ID", "Aggregate rating", "Restaurant Name"]].sort_values("Aggregate rating", ascending = True)
    #   df1_japonese_votes_menor = df1_japonese_votes_menor.reset_index(drop = True)
     #  a = df1_japonese_votes_menor["Restaurant Name"][df1_japonese_votes_menor["Aggregate rating"].idxmin()]
      # df1_japonese_votes_menor
       #a

#   with st.container():
 #      df1_aux = df1.explode("Cuisines_Separadas")
  #     linhas_selecionadas = (df1_aux["Cuisines_Separadas"] == "Healthy Food")
   #    df1_healthy_votes = df1_aux.loc[linhas_selecionadas, ["Restaurant ID", "Aggregate rating", "Restaurant Name"]].sort_values("Aggregate rating", ascending = False)
    #   df1_healthy_votes = df1_healthy_votes.reset_index(drop = True)
     #  a = df1_healthy_votes["Restaurant Name"][df1_healthy_votes["Aggregate rating"].idxmax()]
      # df1_healthy_votes
       #a

#   with st.container():
 #      df1_aux = df1.explode("Cuisines_Separadas")
  #     linhas_selecionadas = (df1_aux["Cuisines_Separadas"] == "Healthy Food")
   #    df1_healthy_votes_menor = df1_aux.loc[linhas_selecionadas, ["Restaurant ID", "Aggregate rating", "Restaurant Name"]].sort_values("Aggregate rating", ascending = True)
    #   df1_healthy_votes_menor = df1_healthy_votes_menor.reset_index(drop = True)
     #  a = df1_healthy_votes_menor["Restaurant Name"][df1_healthy_votes_menor["Aggregate rating"].idxmin()]
      # df1_healthy_votes_menor
       #a

  # with st.container():
   #    df1        
    
    

#   with st.container():
 #      df1_rest_rank = df1.loc[:, ["Restaurant Name", "Aggregate rating", "Country Name"]].sort_values("Aggregate rating", ascending = False).reset_index(drop=True)
  #     df1_rest_rank = df1_rest_rank.loc[0:30, :]
   #    df1_rest_rank

        