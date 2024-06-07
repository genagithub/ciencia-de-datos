import numpy as np
from scipy import zscore
import pandas as pd
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from scipy.stats import pearsonr, zscore
from sklearn.linear_model import LinearRegression





df = sns.load_dataset("tips")

# Análisis estadísticos en los datos para las supocisiones sobre la función objetivo

correlacion, _ = pearsonr(df["total_bill"],df["tip"])
correlacion = str(correlacion)

var_x = df["total_bill"].var()
var_x = str(var_x)

var_y = df["tip"].var()
var_y = str(var_y)

linear_regression = LinearRegression()
 
total_bill = df["total_bill"].values.reshape((-1,1))

# estableciendo el modelo de regresión

model = linear_regression.fit(total_bill,df["tip"])

# realizando la regresión de nuevos datos

objects = np.array([[28.15],[12.5],[3.8],[8.25],[19.5],[32.7],[40.9],[45]])

predicts = model.predict(objects)

# extrayendo valores atípicos

df_zscore = df[["total_bill","tip"]]

df_zscore["total_bill_zscore"] = zscore(df["total_bill"]).abs()
df_zscore["tip_zscore"] = zscore(df["tip"]).abs()

outliers = df_zcore.loc((df_zscore["total_bill_zscore"] > 3) | (df_zscore["tip_zscore"] > 3),["total_bill","tip"])

# generando un Dashboard

app = dash.Dash(__name__)

app.layout = html.Div(id="body",className="e2_body",children=[
    html.H1("dashboard",id="titulo",className="e2_title"),
    html.Div(id="dashboard",className="e2_dashboard",children=[
        html.Div(id="column-1",className="e2_column_1",children=[
            dcc.Dropdown(id="dropdown",className="e2_dropdown",
                        options=[
                            {"label":"Cuentas totales","value":"total_bill"},
                            {"label":"Propinas","value":"tip"}
                        ],
                        value="total_bill",
                        multi=False,
                        clearable=False),
            
            dcc.Graph(id="graph-1",className="e2_graphs",figure={}), 
            dcc.Graph(id="graph-2",className="e2_graphs",figure={})
        ]),
        html.Div(id="column-2",className="e2_column_2",children=[
            html.Div(id="medidas",className="e2_medidas",children=[
                html.Div(id="var_x",className="e2_medida",children=[html.P(f"Varianza X: {var_x[:4]}",style={"font-size":"0.99em"})]),
                html.Div(id="var_y",className="e2_medida",children=[html.P(f"Varianza Y: {var_y[:4]}",style={"font-size":"1em"})])
            ]),
            html.Div(f"Correlación: {correlacion[:4]}",className="e2_correlacion",id="correlacion"),
            dcc.Graph(id="graph-3",className="e2_graph_3",figure={})
        ])
    ])
])

@app.callback(
    [Output(component_id="graph-1",component_property="figure"),
    Output(component_id="graph-2",component_property="figure"),
    Output(component_id="graph-3",component_property="figure")],
    [Input(component_id="dropdown",component_property="value")]
)

def update_dash(slct_var):
    
    mean = df[slct_var].mean()
    median = df[slct_var].median()
    
    extr_list = [0]
    
    var_title = "Cuentas totales"
    
    if slct_var == "tip":
        extr_list.append(60)
        var_title = "Propinas"
    elif slct_var == "total_bill":
        extr_list.append(40)
        var_title = "Cuentas totales"
    
    histplot = go.Figure(go.Histogram(x=df[slct_var],name="Distribución"))
    histplot.add_trace(go.Scatter(x=[mean,mean],y=extr_list,mode="lines+markers",marker_color="red",name="Media"))
    histplot.add_trace(go.Scatter(x=[median,median],y=extr_list,mode="lines+markers",marker_color="green",name="Mediana"))
    histplot.update_layout(title="Histograma",xaxis_title=var_title)
        
    df["zscore"] = zscore(df[slct_var])
    shapiro_wilk = px.scatter(df,x="zscore",y=slct_var)
    shapiro_wilk.update_layout(title="Shapiro-wilk",xaxis_title="Valores Z",yaxis_title=var_title)
    
    scatter = go.Figure()
    scatter.add_trace(go.Scatter(x=df["total_bill"],y=df["tip"],mode="markers",marker_color="blue",name="Propinas reales"))
    scatter.add_trace(go.Scatter(x=objects.reshape(-1),y=predicts,mode="lines+markers",marker_color="red",name="Predicciones"))
    scatter.add_trace(go.Scatter(x=df_zscore["total_bill"],y=df_zscore["tip"],mode="markers",marker_color="green",name="Outliers"))
    scatter.update_layout(title="Algoritmo de Regresión Lineal",xaxis_title="Cuentas totales",yaxis_title="Propinas")

    return histplot,shapiro_wilk,scatter

if __name__ == "__main__":
    app.run_server(debug=False)

# el dashboard generado no es una representación para ideas de negocio, sino una muestra gráfica de los procesos para la creación del modelo y su rendimiento
