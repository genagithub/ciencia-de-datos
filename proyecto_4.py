import numpy as np
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Output, Input
from sklearn.preprocessing import LabelEncoder
from sklearn.decomposition import PCA
from sklearn.naive_bayes import GaussianNB



df = sns.load_dataset("iris")

# codificando las variables de etiqueta para el algoritmo

df["species_encoded"] = LabelEncoder().fit_transform(df["species"])

pca_model = PCA(n_components=2) 

# utilizando la técnica de PCA para reducir la dimensionalidad de las variables independenties

pca = pca_model.fit_transform(df.iloc[:,:-2])

df["PCA_1"] = pca[:,0]
df["PCA_2"] = pca[:,1]

naive_bayes = GaussianNB()

# instanciando el modelo de clasificación 

model = naive_bayes.fit(pca,df["species_encoded"])

object = [[df["sepal_length"].mean(),df["sepal_width"].mean(),df["petal_length"].mean(),df["petal_width"].mean()]]

pca_object = pca_model.transform(object)

# prediciendo la clase(especie) del nuevo objeto

predict_encoded = model.predict(pca_object)

# asociando las categorías codificadas con sus versiones originales

classes = list(zip(df["species"].unique(),df["species_encoded"].unique()))

# asociando la predicción a su clase

predict = classes[predict_encoded[0]][0]

# obteniendo la probabilidad ,es decir, la seguridad del modelo de su predicción

probability = model.predict_proba(pca_object)

probability = probability[0,predict_encoded]*100

probability = str(probability[0])

# generando un dashboard

app = dash.Dash(__name__)

map_spceies = {
    "setosa":"blue",
    "virginica":"green",
    "versicolor":"red"
}
df["species_colors"] = df["species"].apply(lambda x : map_spceies.get(x))

species_colors = list(zip(df["species_encoded"].unique(),df["species_colors"].unique()))

graph_pca = go.Figure()
graph_pca.add_trace(go.Scatter(x=df["PCA_1"],y=df["PCA_2"],mode="markers",marker_color="blue",name="especies"))
graph_pca.add_trace(go.Scatter(x=[pca_object[0,0]],y=[pca_object[0,1]],mode="markers",marker_color="red",name=f"nueva especie"))
graph_pca.update_layout(title="Figura PCA(principal components anlasysis)")

df_esp = sns.load_dataset("iris")
df_esp.columns = ["longitud_sépalo","ancho_sépalo","longitud_pétalo","ancho_pétalo","especies"]

app.layout =  html.Div(id="body",className="e4_body",children=[
    html.H1("dashboard",id="title",className="e4_title"),
    html.Div(id="dashboard",className="e4_dashboard",children=[
        html.Div(className="e4_graph_div",children=[
            dcc.Dropdown(id="dropdown",style={"width":"150px","height":"25px","margin":"3px 0 0 0"},
                        options=[
                            {"label":"Longitud pétalo","value":"longitud_pétalo"},
                            {"label":"Ancho pétalo","value":"ancho_pétalo"}
                        ],
                        value="longitud_pétalo",
                        multi=False,
                        clearable=False),
            dcc.Graph(id="graph-1",className="e4_graph",figure={})
        ]),
        html.Div(className="e4_graph_div",children=[
            dcc.Graph(id="graph-2",className="e4_graph",figure=graph_pca),
            html.P(["predicción: ",html.B(predict,style={"color":species_colors[predict_encoded[0]][1]}),f" | probabildad: {probability[:4]}%"],style={"font-size":"1em","font-weigth":"bold","font-family":"sans-serif","text-align":"center"})
        ])
    ])
])
    
@app.callback(
    Output(component_id="graph-1",component_property="figure"),
    [Input(component_id="dropdown",component_property="value")]
)

def update_graph(slct_var):
    
    graph_multi = px.scatter_3d(df_esp,x='longitud_sépalo',y='ancho_sépalo',z=slct_var,color='especies')
    graph_multi.update_layout(title="Figura multidimensional")
    
    return graph_multi
    
if __name__ == "__main__":
    app.run_server(debug=False)

# el dashboard generado no es una representación para ideas de negocio, sino una muestra gráfica de los procesos para la creación del modelo y su rendimiento