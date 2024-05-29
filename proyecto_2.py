import mysql.connector
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots


# realizando una conexión con el gestor de bases de datos MySQL

conexion = mysql.connector.connect(host="localhost",                                             
                                   user="root",
                                   password="123456789",
                                   port="3306",
                                   database="northwind",
                                   auth_plugin="mysql_native_password")                                     

cursor_1 = conexion.cursor()

# realizando consultas que relacionan tablas y generan columnas nuevas

cursor_1.execute('''create view order_details_cash as
                    select OrderID, od.ProductID, Price * Quantity as product_cash from OrderDetails od
                    join Products p on od.ProductID = p.ProductID;''')

cursor_1.execute('''select ProductName, sum(product_cash) as product_revenue from order_details_cash odc
                    join Products p on p.ProductID = odc.ProductID
                    group by p.ProductID
                    order by product_revenue desc
                    limit 20''')

# creando un Data frame que esté constituido por los datos provenientes de las consultas realizadas en la base de datos

data_1 = {
    "products":[],
    "products_revenue":[]
}

for p in cursor_1:
    data_1["products"].append(p[0])
    data_1["products_revenue"].append(p[1])

df_1 = pd.DataFrame(data_1)

# ------------------------------------------------------------------------------------------------------------------

cursor_2 = conexion.cursor()

cursor_2.execute('''create view orders_revenue as
                    select o.OrderID, sum(product_cash) as order_revenue, EmployeeID from order_details_cash odc
                    join Orders o on o.OrderID = odc.OrderID
                    group by o.OrderID
                    order by order_revenue desc;''')

cursor_2.execute('select * from orders_revenue limit 20')

data_2 = {
    "orders_id":[],
    "orders_revenue":[]
}

for o in cursor_2:
    data_2["orders_id"].append(o[0])
    data_2["orders_revenue"].append(o[1])

df_2 = pd.DataFrame(data_2)
df_2["orders_id"] = df_2["orders_id"].astype("string")

# --------------------------------------------------------------------------------------------------------

cursor_3 = conexion.cursor()

cursor_3.execute('''select concat (FirstName," ",LastName) as name, sum(order_revenue) as employee_revenue from Employees e
                join orders_revenue o on o.EmployeeID = e.EmployeeID 
                group by e.EmployeeID
                order by employee_revenue''')
data_3 = {
    "names":[],
    "employees_revenue":[]
}

for e in cursor_3:
    data_3["names"].append(e[0])
    data_3["employees_revenue"].append(e[1])
    
df_3 = pd.DataFrame(data_3)

# delete_views = conexion.cursor()
# delete_views.execute('drop view order_details_cash; drop view orders_revenue')

# generando una figura que muestre las mayores ganancias de empleados, productos y órdenes

fig = make_subplots(rows=1, cols=3)

fig.add_trace(go.Bar(x=df_1["products"],y=df_1["products_revenue"],name="20 productos con más ingresos"),row=1,col=1)

fig.add_trace(go.Bar(x=df_3["names"],y=df_3["employees_revenue"],name="Ingresos de empleados"),row=1,col=2)

fig.add_trace(go.Bar(x=df_2["orders_id"],y=df_2["orders_revenue"],name="20 órdenes con más ingresos"),row=1,col=3)

fig.update_layout(height=660, width=1340, title_text="Rentabilidad")
fig.show()
