import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import zscore
from sklearn import datasets
from sklearn.model_selection import train_test_split
from sklearn.model_selection import GridSearchCV
from xgboost import XGBRegressor
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score



data = datasets.fetch_california_housing()

df = pd.DataFrame(data["data"],columns=data["feature_names"])
df["MedHouseVal"] = data["target"]

df_model = df.copy()

# removiendo los valores atípicos para la optimización del modelo

def remove_outliers(df,columns):
    for c in columns:
        df[c] = df[c].mask(zscore(df[c]).abs() > 3, np.nan)
    
    return df

df_model = remove_outliers(df_model,df.columns)

df_model.dropna(inplace=True)

x_train, x_test, y_train, y_test = train_test_split(df_model[df_model.column[:-1]],
                                                    df_model["MedHouseVal"],
                                                    test_size=0.25)

# ajuste de hiperparámetros utilizando Grid Search 

xgbr_test = XGBRegressor()           

turned_parameters = {
    "n_estimators":[100,200,300],
    "max_depth":[3,4,5],
    "learning_rate":[0.3,0.4,0.5],
    "min_child_weight":[1,2,3]
}

grid_search = GridSearchCV(xgbr_test,param_grid=turned_parameters,cv=5)
grid_search.fit(x_train,y_train)

xgbr = XGBRegressor(n_estimators = grid_search.best_params_["n_estimators"],
                    max_depth = grid_search.best_params_["max_depth"],
                    learning_rate = grid_search.best_params_["learning_rate"],
                    min_child_weight = grid_search.best_params_["min_child_weight"])    


model = xgbr.fit(x_train,y_train)

# validando la eficiencia del modelo con los datos de prueba

print(f"Coeficiente de determinación: {model.score(x_test, y_test)} \n")

# generando clusters según los valores de las viviendas

# clusters = []
# inertias = []

# for c in range(3,12):
#     kmeans = KMeans(n_clusters=c).fit(df["MedHouseVal"].values.reshape((-1,1)))
#     clusters.append(c)
#     inertias.append(kmeans.inertia_)
    
# plt.plot(clusters,inertias,marker="o")
# plt.grid("on")
# plt.show()
#                   Método del codo
#                          |
kmeans = KMeans(n_clusters=5).fit(df["MedHouseVal"].values.reshape((-1,1)))
clusters = kmeans.labels_.astype(str)
df["clusters"] = clusters

silhouette_km = silhouette_score(df["MedHouseVal"].values.reshape((-1,1)),kmeans.labels_)
print(f"Coeficiente de silueta: {silhouette_km}")

df["index"] = df.index

fig = px.scatter(df, x="index", y="MedHouseVal", color="clusters")
fig.update_layout(xaxis_title="Houses", yaxis_title="Values", title="Houses'values clustered")
fig.show()
