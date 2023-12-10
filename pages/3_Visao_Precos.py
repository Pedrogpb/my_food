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
from folium.plugins import MarkerCluster
from folium.plugins import HeatMap
import plotly.graph_objects as go
import scipy.stats as stats
import statsmodels.api as sm

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
cor = "#5353ec"

#====#====#====#====#====#====#====#====#====#====#====#====#====#====#====#====#====#====#====#====#====#====#
# SIDEBAR STREAMLIT
#====#====#====#====#====#====#====#====#====#====#====#====#====#====#====#====#====#====#====#====#====#====#

st.set_page_config(page_title = "MyFood - Análise de Preços", page_icon =  "🍽️", layout = "centered")

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

st.markdown("# Visão por Preços 💷")
st.markdown("""---""")



with st.container():
    st.markdown("### Valor Médio de Prato para Dois por País (USD $)")

    col1, col2, col3, col4, col5, col6 = st.columns(6)

    with col1:
        df1_cost2 = df1.loc[:, ["Country Name", "Average Cost for two in Dollar"]].groupby("Country Name").mean("Average Cost for two in Dollar")
        df1_cost2 = df1_cost2.sort_values("Average Cost for two in Dollar", ascending = False).reset_index()
        filipinas = np.round(df1_cost2.loc[0, "Average Cost for two in Dollar"], 2)
        st.metric("Philippines", filipinas)

    with col2:
        nova_zelandia = np.round(df1_cost2.loc[1, "Average Cost for two in Dollar"], 2)
        st.metric("New Zeland", nova_zelandia)

    with col3:
        usa = np.round(df1_cost2.loc[2, "Average Cost for two in Dollar"], 2)
        st.metric("USA", usa)

    with col4:
        canada = np.round(df1_cost2.loc[3, "Average Cost for two in Dollar"], 2)
        st.metric("Canada", canada)

    with col5:
        brazil = np.round(df1_cost2.loc[4, "Average Cost for two in Dollar"], 2)
        st.metric("Brazil", brazil)

    with col6:
        india = np.round(df1_cost2.loc[5, "Average Cost for two in Dollar"], 2)
        st.metric("India", india)

with st.container():
    st.markdown("""---""")
    st.markdown("### Restaurante mais Caros do Mundo (USD $)")
    
    df1_cost2_city = df1.loc[:, ["Country Name", "Restaurant Name", "Average Cost for two in Dollar"]].groupby(["Country Name", "Restaurant Name"]).mean()
    df1_cost2_city = df1_cost2_city.sort_values("Average Cost for two in Dollar", ascending = False).reset_index()
    df1_cost2_city = df1_cost2_city.loc[0:9, :]
    fig = px.bar(df1_cost2_city, x = "Restaurant Name", y = "Average Cost for two in Dollar", color = "Country Name")
    fig.update_layout(legend_title = "Países", xaxis_title = "", yaxis_title = "")
    fig.update_traces(texttemplate='%{y}', textposition='outside')
    fig.update_yaxes(range=[0, 700])
    st.plotly_chart(fig, use_container_width = True)
    
    st.markdown("""---""")
        
        
with st.container():
    
    col1, col2 = st.columns(2)
    
    with col1:
        
                
        df1_aux = df1.explode("Cuisines_Separadas")
        df1_cost2 = df1_aux.loc[:, ["Cuisines_Separadas", "Average Cost for two in Dollar"]].groupby("Cuisines_Separadas").mean("Average Cost for two in Dollar")
        df1_cost2 = df1_cost2.sort_values("Average Cost for two in Dollar", ascending = False).reset_index()
        df1_cost2 = df1_cost2.loc[0:9,:]
        fig = px.bar(df1_cost2, x = "Cuisines_Separadas", y = "Average Cost for two in Dollar")
        fig.update_layout(title = "Top 10 Culinárias mais Caras", title_x = 0.26, xaxis_title = "", yaxis_title = "")
        fig.update_traces(texttemplate='%{y}', textposition='outside')
        fig.update_yaxes(range=[0, 200], tickformat=".1f")
        st.plotly_chart(fig, use_container_width = True)
        
    with col2:
        
        df1_aux = df1.explode("Cuisines_Separadas")
        df1_cost2 = df1_aux.loc[:, ["Cuisines_Separadas", "Average Cost for two in Dollar"]].groupby("Cuisines_Separadas").mean("Average Cost for two in Dollar")
        df1_cost2 = df1_cost2.sort_values("Average Cost for two in Dollar", ascending = True).reset_index()
        df1_cost2 = df1_cost2.loc[0:9,:]
        fig = px.bar(df1_cost2, x = "Cuisines_Separadas", y = "Average Cost for two in Dollar")
        fig.update_layout(title = "Top 10 Culinárias mais Baratas", title_x = 0.26, xaxis_title = "", yaxis_title = "")
        fig.update_traces(texttemplate='%{y}', textposition='outside')
        fig.update_yaxes(range=[0, 7], tickformat=".1f")
        st.plotly_chart(fig, use_container_width = True)
        
    
with st.container():
    
    
    st.markdown("""---""")

    
    st.markdown("### Valor Média de um Prato para Dois x Nota do Restaurante")
    
    df1_scatter = df1.sort_values("Average Cost for two in Dollar", ascending=False)
    X = df1_scatter["Aggregate rating"]
    Y = df1_scatter["Average Cost for two in Dollar"]
    X = sm.add_constant(X)  # Adiciona uma constante (intercepto) à regressão
    model = sm.OLS(Y, X).fit()

    # Crie um array com valores para traçar a linha de tendência
    X_pred = np.linspace(X["Aggregate rating"].min(), X["Aggregate rating"].max(), 100)
    X_pred = sm.add_constant(X_pred)
    Y_pred = model.predict(X_pred)

    # Crie o gráfico de dispersão com a linha de tendência
    fig = px.scatter(df1_scatter, y="Average Cost for two in Dollar", x="Aggregate rating")
    fig.add_traces(px.line(x=X_pred[:, 1], y=Y_pred).data[0])
    fig.update_traces(name='Linha de Tendência', line=dict(color='red'))
    fig.update_yaxes(range=[0, 700])
    st.plotly_chart(fig, use_container_width=True)
    
    
with st.container():
    st.markdown("##### Existe uma fraca Correlação Positiva entre o Valor do Prato para Dois e a Nota do Restaurante.")

                
    var_preco = stats.shapiro(df1["Average Cost for two in Dollar"])       # Teste de Normalidade
    var_notas = stats.shapiro(df1["Aggregate rating"])                     # Teste de Normalidade

    _, p_var_preco = stats.shapiro(df1["Average Cost for two in Dollar"])         # O prefixo "_," signfica que estamos ignorando o primeiro valor gerado na variavel var_preco 
    _, p_var_notas = stats.shapiro(df1["Aggregate rating"])                       # O prefixo "_," signfica que estamos ignorando o primeiro valor gerado na variavel var_notas 

    alpha = 0.05  # Nível de significância

    if p_var_preco > alpha and p_var_notas > alpha:
        # Ambas as variáveis são aproximadamente normais, use a correlação de Pearson
        correlacao, _ = stats.pearsonr(df1["Average Cost for two in Dollar"], df1["Aggregate rating"])
        tipo_correlacao = "Pearson"
    else:
        # Pelo menos uma das variáveis não é normal, use a correlação de Spearman
        correlacao, _ = stats.spearmanr(df1["Average Cost for two in Dollar"], df1["Aggregate rating"])
        tipo_correlacao = "Spearman"
    
    correlacao = np.round(correlacao, 3)

    st.markdown(f"###### Correlação de {tipo_correlacao}: {correlacao}")
    
    
#with st.container():
#   st.markdown("### Prato para Dois mais Caros por Tipo de Culinária (USD $)")
#
#    col1, col2, col3, col4, col5, col6 = st.columns(6)
#
#    with col1:
#        df1_aux = df1.explode("Cuisines_Separadas")
#        df1_cost2 = df1_aux.loc[:, ["Cuisines_Separadas", "Average Cost for two in Dollar"]].groupby("Cuisines_Separadas").mean("Average Cost for two in Dollar")
#        df1_cost2 = df1_cost2.sort_values("Average Cost for two in Dollar", ascending = False).reset_index()
#        
#        new_mexican = np.round(df1_cost2.loc[0, "Average Cost for two in Dollar"], 1)
#        st.metric("New Mexican", new_mexican)
#
#    with col2:
#        jamaican = np.round(df1_cost2.loc[1, "Average Cost for two in Dollar"], 1)
#        st.metric("Jamaican", jamaican)
#        
#    with col3:
#        floribean = np.round(df1_cost2.loc[2, "Average Cost for two in Dollar"], 1)
#        st.metric("Floribbean", floribean)
#
#    with col4:
#        teppanyaki = np.round(df1_cost2.loc[3, "Average Cost for two in Dollar"], 1)
#        st.metric("Teppanyaki", teppanyaki)
#
#    with col5:
#        pacific = np.round(df1_cost2.loc[4, "Average Cost for two in Dollar"], 1)
#        st.metric("Pacific", pacific)
#
#    with col6:
#        new_american = np.round(df1_cost2.loc[5, "Average Cost for two in Dollar"], 1)
#        st.metric("New American", new_american)