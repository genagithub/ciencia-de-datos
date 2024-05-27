import pandas as pd
import plotly.express as px
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import confusion_matrix,accuracy_score,recall_score,precision_score,f1_score
from sklearn import tree




df  = pd.read_csv("titanic.csv")


df.fillna({"Age": df["Age"].mean()},inplace=True)


df["Sex_encoded"] = LabelEncoder().fit_transform(df["Sex"])
df["Embarked_encoded"] = LabelEncoder().fit_transform(df["Embarked"])


map_survived = {
    0:"no",
    1:"yes"
}
df["Survived_no_encoded"] = df["Survived"].apply(lambda x : map_survived.get(x))



data_train, data_test, class_train, class_test = train_test_split(
                                                   df[["Sex_encoded","Pclass","Fare","Parch","SibSp"]],
                                                   df["Survived"],
                                                   test_size=0.15)


tree_decision = tree.DecisionTreeClassifier(criterion="entropy",max_depth=5)

model = tree_decision.fit(data_train,class_train)


class_predicts = tree_decision.predict(data_test)

class_real = class_test.values


matrix_confusion = confusion_matrix(class_real,class_predicts)
TP = matrix_confusion[0,0]
FP = matrix_confusion[0,1]
FN = matrix_confusion[1,0]
TN = matrix_confusion[1,1]

accuracy = accuracy_score(class_real,class_predicts)
accuracy = str(accuracy)
recall = recall_score(class_real,class_predicts)
recall = str(recall)
precision = precision_score(class_real,class_predicts)
precision = str(precision)
F1_score = f1_score(class_real,class_predicts)
F1_score = str(F1_score)


app = dash.Dash(__name__)

app.layout = html.Div(id="body",className="e1_body",children=[
html.H1("dashboard",id="title",className="e1_title"),
html.Div(className="e1_dashboards",children=[
    html.Div(id="graph_div_1",className="e1_graph_div",children=[
        html.Div(id="dropdown_div_1",className="e1_dropdown_div",children=[
            dcc.Dropdown(id="dropdown_1",className="e1_dropdown",
                        options = [
                            {"label":"Sexo","value":"Sex"},
                            {"label":"Clase social","value":"Pclass"},
                            {"label":"Embarcadero","value":"Embarked"},
                            {"label":"Padres e hijos/as","value":"Parch"},
                            {"label":"Hermanas/os y esposas/os","value":"SibSp"},
                        ],
                        value="Sex",
                        multi=False,
                        clearable=False)
        ]),
        dcc.Graph(id="piechart",className="e1_graph",figure={})
    ]),
    html.Div(id="graph_div_2",className="e1_graph_div",children=[
        html.Div(id="dropdown_div_2",className="e1_dropdown_div",children=[
            dcc.Dropdown(id="dropdown_2",className="e1_dropdown",
                        options = [
                            {"label":"Edad","value":"Age"},
                            {"label":"Boleto","value":"Fare"},
                        ],
                        value="Age",
                        multi=False,
                        clearable=False)
        ]),
        dcc.Graph(id="bar",className="e1_graph",figure={})
    ]),
]),
    
    html.Div(className="e1_div",children=[
        html.Div(id="algoritmo",className="e1_algoritmo",children=[
        html.H2("Árbol de decisión",className="e1_title_arbol"),
        html.Div(className="e1_arbol",children=[
        html.P("|--- Sex <= 0.50"),
        html.P("|   |--- Pclass <= 2.50"),
        html.P("|   |   |--- class: 1"),
        html.P("|   |--- Pclass >  2.50"),
        html.P("|   |   |--- class: 1"),
        html.P("|--- Sex >  0.50"),
        html.P("|   |--- Fare <= 15.17"),
        html.P("|   |   |--- class: 0"),
        html.P("|   |--- Fare >  15.17"),
        html.P("|   |   |--- class: 0")  
        ])
        ]),
        html.Div(id="modelos_metricas",className="e1_modelos_metricas",children=[
            html.Div(id="modelos",className="e1_modelos",children=[
                html.P(f"Clases reales: \n {class_real}",style={"text-align":"center","font-family":"sans-serif"}),
                html.P(f"Predicciones: \n {class_predicts}",style={"text-align":"center","font-family":"sans-serif"}),
                html.P("--------------------------------------------------------------------------------",className={"text-align":"center","font-family":"sans-serif"})
            ]),
            html.Div(className="e1_metricas",id="metricas",children=[
                html.Div(children=[
                    html.P("Matriz de confusión",style={"font-size":"0.9em","text-align":"center","font-family":"sans-serif","font-weigth":"bold"}),
                    html.Div(className="e1_matriz",id="matriz_confusion",children=[
                        html.Div(f"{TP}",id="TP",className="e1_aciertos"), 
                        html.Div(f"{FP}",id="FP",className="e1_aciertos"),
                        html.Div(f"{FN}",id="FN",className="e1_aciertos"),
                        html.Div(f"{TN}",id="TN",className="e1_aciertos")
                    ])
                ]),
                html.Div(className="e1_puntuaciones",children=[
                    html.Ul(id="lista",children=[
                        html.Li(f"Accuracy: {accuracy[:4]}",id="accuracy",style={"font-family":"sans-serif"}),
                        html.Li(f"Recall: {recall[:4]}",id="recall",style={"font-family":"sans-serif"}),
                        html.Li(f"Precision: {precision[:4]}",id="precision",style={"font-family":"sans-serif"}),
                        html.Li(f"F1 Score: {F1_score[:4]}",id="f1_score",style={"font-family":"sans-serif"})
                    ],className={"padding-top":"45px"})
                ])
            ])
        ])
    ])
])

@app.callback(
    [Output(component_id="piechart",component_property="figure"),
    Output(component_id="bar",component_property="figure")],
    [Input(component_id="dropdown_1",component_property="value"),
    Input(component_id="dropdown_2",component_property="value")]
)

def update_graph(slct_var_cat,slct_var_num):
    
    df_percentage = df.groupby(slct_var_cat)["Survived"].mean()
    df_percentage = df_percentage.reset_index()
    df_percentage["Survived"] = df_percentage["Survived"] * 100
    
    piechart = px.pie(df_percentage,values='Survived',names=slct_var_cat,title='Porcentage de sobrevivir')
    
    
    df_mean = df.groupby("Survived_no_encoded")[slct_var_num].mean()
    df_mean = df_mean.reset_index()
    
    barplot = px.bar(df_mean,x="Survived_no_encoded",y=slct_var_num,title='Medias de Edad y Boleto',labels={"x":"sobrevivientes","y":slct_var_num})
    barplot.update_layout(xaxis_title="Sobrevivientes")
    
    return piechart,barplot

if __name__ == "__main__":
    app.run_server(debug=False)
    
# el dashboard generado no es una representación para ideas de negocio, sino una muestra gráfica de los procesos para la creación del modelo y su rendimiento