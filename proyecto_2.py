import mysql.connector
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import dash
import dash_core_components as dcc
import dash_html_components as html

# realizando una conexión con el gestor de bases de datos MySQL

connect = mysql.connector.connect(host="localhost",                                             
                                   user="root",
                                   password="123456789",
                                   port="3306",
                                   database="northwind",
                                   auth_plugin="mysql_native_password")                                     

cursor_1 = connect.cursor()

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

cursor_2 = connect.cursor()

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

cursor_3 = connect.cursor()

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

# generando una dashboard orientado a estrategias empresariales que muestre la rentabilidad de empleados, productos y órdenes

fig = make_subplots(rows=1, cols=3)

fig.add_trace(go.Bar(x=df_1["products"],y=df_1["products_revenue"],name="20/77 productos con más ingresos"),row=1,col=1)

fig.add_trace(go.Bar(x=df_3["names"],y=df_3["employees_revenue"],name="Ingresos de empleados"),row=1,col=2)

fig.add_trace(go.Bar(x=df_2["orders_id"],y=df_2["orders_revenue"],name="20/196 órdenes con más ingresos"),row=1,col=3)

fig.update_layout(height=660, width=1340, title_text="Rentabilidad")

# ----------------------------------------------------------------------------------------------------------------------------------------

select_product = connect.cursor()

select_product.execute('''select ProductName, sum(Quantity), sum(product_cash) as product_revenue from order_details_cash odc
                        join Products p on odc.ProductID = p.ProductID
                        group by p.ProductID
                        order by product_revenue desc
                        limit 1;''')


for bp in select_product:
    product = bp[0]
    total_quantity_1 = str(bp[1])
    total_incomes_1 = bp[2]

# ----------------------------------------------------------------------------------------------------------------------------------------

select_employee = connect.cursor()

select_employee.execute('''select concat (FirstName," ",LastName) as name, sum(total_quantity) as total_quantity, sum(order_revenue) as employee_revenue  from Employees e
                    join orders_revenue o on o.EmployeeID = e.EmployeeID 
                    group by e.EmployeeID
                    order by employee_revenue desc
                    limit 1''')

for be in select_employee:
    name = be[0]
    total_quantity_2 = be[1]
    total_incomes_2 = be[2]

# ----------------------------------------------------------------------------------------------------------------------------------------

select_order = connect.cursor()

select_order.execute('''select OrderID, total_quantity, order_revenue from orders_revenue  
                    order by order_revenue desc
                    limit 1''')

for bo in select_order:
    order_id = bo[0]
    total_quantity_3 = bo[1]
    total_incomes_3 = bo[2]


app = dash.Dash(__name__)

app.layout = html.Div(id="body",children=[
    dcc.Graph(id="multi-figure",figure=fig),
    html.H1("Mayores ingresos",className="e2_titulo"),
    html.Div(className="e2_container",children=[
        html.Div(id="data_1",className="e2_children",style={"color":"blue"},children=[   
            html.H2("Productos",style={"color":"blue","font-family":"sans-serif"}),         
            html.Ul(className="e2_ul",children=[
                html.Li(f"Producto: {product}",style={"color":"blue","font-family":"sans-serif","margin":"2.5px 0"}),
                html.Li(f"Cantidad total vendida: {total_quantity_1}",style={"color":"blue","font-family":"sans-serif","margin":"2.5px 0"}),
                html.Li(f"Ingresos totales: {total_incomes_1}$",style={"color":"blue","font-family":"sans-serif","margin":"2.5px 0"})
            ])
        ]),
        html.Div(id="data_2",className="e2_children",children=[
            html.H2("Empleados",style={"color":"red","font-family":"sans-serif"}),
            html.Ul(className="e2_ul",children=[
                html.Li(f"Nombre: {name}",style={"color":"red","font-family":"sans-serif","margin":"2.5px 0"}),
                html.Li(f"Cantidad total de productos: {total_quantity_2}",style={"color":"red","font-family":"sans-serif","margin":"2.5px 0"}),
                html.Li(f"Ingresos totales: {total_incomes_2}$",style={"color":"red","font-family":"sans-serif","margin":"2.5px 0"})
            ])
        ]),
        html.Div(id="data_3",className="e2_children",children=[
            html.H2("Órdenes",style={"color":"green","font-family":"sans-serif"}),
            html.Ul(className="e2_ul",style={"color":"green"},children=[
                html.Li(f"Órden: {order_id}",style={"color":"green","font-family":"sans-serif","margin":"2.5px 0"}),
                html.Li(f"Cantidad total de productos: {total_quantity_3}",style={"color":"green","font-family":"sans-serif","margin":"2.5px 0"}),
                html.Li(f"Ingresos totales: {total_incomes_3}$",style={"color":"green","font-family":"sans-serif","margin":"2.5px 0"})
            ])
        ]) 
    ])
])

if __name__ == "__main__":
    app.run_server(debug=False)

# delete_views = conexion.cursor()
# delete_views.execute('drop view product_higher_income; drop view order_details_cash; drop view orders_revenue')
