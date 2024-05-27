import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import zscore
from sklearn import datasets
from sklearn.model_selection import train_test_split
from sklearn.model_selection import GridSearchCV
from xgboost import XGBRegressor



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

x_train, x_test, y_train, y_test = train_test_split(df_model[data["feature_names"]],
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

print(f"Coeficiente de determinación: {model.score(x_test, y_test)}")

# ---------------------------------------------------------------------------------------------------------------------------------------

# realizadno boostrapping

# tomando muestra principal con reemplazo del 3% de la población de datos

main_sample = df["MedHouseVal"].sample(frac=3/100)

samples = np.array([])

# tomando 1000 muestras con reemplazo del 3%

for m in range(0,1000):
    sample = df["MedHouseVal"].sample(frac=3/100,replace=True)
    samples = np.append(samples,sample.values)
    
samples = samples.reshape((-1,sample.shape[0]))

# calculando la media de la muestra principal

main_sample_mean = main_sample.mean()

# calculando la media de las demás muestras

samples_mean = samples.mean(axis=1)

# calculando la media de la población

population_mean = df["MedHouseVal"].mean()

# calculando los límites del intervalo de confianza del 95%

confidence_interval = np.quantile(samples_mean,[0.025,0.975])

x = np.linspace(confidence_interval[0],confidence_interval[1], 100)
y = [25] * x.size

plt.title("Distribución muestral de la media")

plt.hist(samples_mean,alpha=0.5)

plt.axvline(main_sample_mean,linestyle="--",color="red",label="Media de la muestra principal")

plt.axvline(confidence_interval[0],color="black",label="Límite inferior")
plt.axvline(confidence_interval[1],color="black",label="Límite superior")

# grafincando el rango del intervalo de confiaza

plt.scatter(x, y, color="black",s=10,alpha=0.5)

plt.axvline(population_mean,linestyle="--",color="blue",label="Media poblacional")

plt.xlabel("Valores de casas")
plt.ylabel("conteo")
plt.legend(bbox_to_anchor=(1,0.5))
plt.subplots_adjust(left=0.05,right=0.8)
plt.show()