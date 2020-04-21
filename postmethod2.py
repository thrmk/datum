import os
import pathlib
import requests
import flask
import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html

from flask import Flask, request,render_template
from flask_restful import Api
from flask_restful import Resource, reqparse
from flask_sqlalchemy import SQLAlchemy
from dash.dependencies import Input, Output, State
import dash_table
import plotly.graph_objs as go
import dash_daq as daq

import paho.mqtt.client as mqtt
import time
from datetime import datetime
from flask import Flask, render_template, request, jsonify, Response
from sqlalchemy import create_engine
from datetime import datetime
import pandas as pd

FA ="https://use.fontawesome.com/releases/v5.8.1/css/all.css"
LOGO ="https://www.tirumala.org/NewImages/TTD-Logo.png"
LOGO1="https://www.tirumala.org/NewImages/HD-TXT.png"

server = flask.Flask(__name__)

server.config['DEBUG'] = True

server.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///data.db')
server.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

server.secret_key = 'smarttrak'

db_URI = os.environ.get('DATABASE_URL', 'sqlite:///data.db')
engine = create_engine(db_URI)

api = Api(server)
db = SQLAlchemy()

db.init_app(server)

def stamp1():
    x= str(datetime.now())
    print("stamp=",x)
    return x


@server.before_first_request
def create_tables():
    print("create table")
    db.create_all()

class DeviceModel(db.Model):
    __tablename__ = 'devices'

    print("Dev modelinit")
    stamp = db.Column(db.String(25),primary_key=True)
    devId = db.Column(db.String(15),primary_key=True)
    sun = db.Column(db.String(15))
    ta= db.Column(db.String(15))

    #motor = db.Column(db.String(20))
        
    def __init__(self,stamp,devId,sun,ta):      #,motor):
        print("init")
        stamp=stamp1()
        self.stamp = stamp
        self.devId = devId
        self.sun = sun

        self.ta = ta

        #self.motor = motor
            
    def json(self):
        print("json")
        return {'stamp':self.stamp,'devId':self.devId,'sun':self.sun,'ta':self.ta}#,'motor': self.motor}


    @classmethod
    def find_by_name(cls, stamp):
        print("find by name")
        return cls.query.filter_by(stamp=stamp).first()

    def save_to_db(self):
        print("save to db")
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()

class Device(Resource):
    parser = reqparse.RequestParser()
    print("parser=",parser) 
    parser.add_argument('stamp',type=str)
    parser.add_argument('devId',type=str)
   
    parser.add_argument('sun',type=str)

    parser.add_argument('ta',type=str)
    print("add parser=",parser)
    #parser.add_argument('mode',type=str)
    #parser.add_argument('motor',type=str)
  
    def get(self):
        stamp=stamp1()
        device = DeviceModel.find_by_name(stamp)
        if device:
            return device.json()
        return {'message': 'Device not found'}, 404

    def post(self, stamp):# message):

        stamp=str(stamp1())
        
        data = Device.parser.parse_args()
        print("data=")
        print(data)
               
        device = DeviceModel.find_by_name(stamp)
        print("device=",device)
 
        print("after devicemodel")
              
        if device is None:
            print("if block beforedb")
 
            print("in between ")
            print("afterdb")

            device = DeviceModel(stamp,data['devId'],data['sun'],data['ta'])#,data['motor'])#,data['bphvol'])
          #  print("device=",device)
    
        elif device is None and devId!=stamp:
            print("else if beforedb")
            #k=DeviceModel("567","345","98","35")
            print("in between")
#            k=DeviceModel(stamp,x[1],x[4],x[7]) 
            device = DeviceModel(stamp,data['devId'],data['sun'],data['ta'])#,data['motor'])#,data['bphvol'])
            #k.save_to_db()
            print("after db")

        else:

            print("else")

            device.devId= data['devId']
            device.stamp = data['stamp']
            device.sun = data['sun']
            device.ta = data['ta']
            #device.bphvol = data['bphvol']
                       
        try:

            device.save_to_db()
        
        except:
            return {"message": "An error occurred inserting the device data."}, 500

        return device.json(), 201


class DeviceList(Resource):
    def get(self):
        x= {'devices': [x.json() for x in DeviceModel.query.all()]}
        return x


api.add_resource(Device, '/device/<string:stamp>')
api.add_resource(DeviceList, '/devices')

CONTENT_STYLE = {
    "margin-left": "18rem",
    "margin-right": "15rem",
    "padding": "2rem 2rem",
    "fontSize":"30rem"
}

collapse = html.Div(
    [
        dbc.Button("Menu",id="collapse-button",className="mb-4",color="primary"),
        dbc.Container(dbc.Collapse(
            children=[dbc.DropdownMenu(nav=True,in_navbar=True,label="Substations",
            children=[
                dbc.DropdownMenu(nav=True,in_navbar=True,label="SUB 1",
                    children=[
                        dbc.DropdownMenuItem(dbc.NavLink("Dev 1",href="/Dev-1",id="dev-1")),dbc.DropdownMenuItem(divider=True),dbc.DropdownMenuItem(dbc.NavLink("Dev 2",href="/Dev-2",id="dev-2")),dbc.DropdownMenuItem(divider=True),
                            dbc.DropdownMenuItem(dbc.NavLink("Dev 3",href="/Dev-3",id="dev-3"))]),
                           dbc.DropdownMenu(nav=True,in_navbar=True,label="SUB 2",
                               children=[
                                   dbc.DropdownMenuItem(dbc.NavLink("SVM 1",href="/SVM-1",id="svm-1")),dbc.DropdownMenuItem(divider=True),dbc.DropdownMenuItem(dbc.NavLink("SVM 2",href="/SVM 2",id="svm-2")),dbc.DropdownMenuItem(divider=True),
                            dbc.DropdownMenuItem(dbc.NavLink("SVM 3",href="/SVM-3",id="svm-3"))])]),
                    dbc.DropdownMenu(nav=True,in_navbar=True,label="Streetlights",
                        children=[
                dbc.DropdownMenu(nav=True,in_navbar=True,label="SL 1",
                    children=[
                        dbc.DropdownMenuItem(dbc.NavLink("JEO 1",href="/jeo-1")),dbc.DropdownMenuItem(divider=True),dbc.DropdownMenuItem(dbc.NavLink("JEO 2",href="/jeo 2")),dbc.DropdownMenuItem(divider=True),
                            dbc.DropdownMenuItem(dbc.NavLink("JEO 3",href="/jeo 3"))]),
                           dbc.DropdownMenu(nav=True,in_navbar=True,label="SL 2",
                               children=[
                                   dbc.DropdownMenuItem(dbc.NavLink("SVSD 1",href="/SVSD-1")),dbc.DropdownMenuItem(divider=True),dbc.DropdownMenuItem(dbc.NavLink("SVSD 2",href="/SVSD 2")),dbc.DropdownMenuItem(divider=True)])])],                                                                  
                                
    id="collapse"),style={"backgroundColor":"grey","width":"auto"})])     

sidebar = html.Div(
        [
       dbc.Row(
            html.Img(src=LOGO,height="100px",width="auto"),style={"padding-left":0}),
                
            dbc.Nav(collapse, vertical=True)
  ] ,

style={
    "position": "absolute",
    "top": 0,
    "left":"2rem",
    "bottom": 0,
    "width": "12rem",
    "padding": "1rem 0rem",
    "backgroundColor":"light"},
     id="sidebar",
)

button =html.Div(
           dbc.Row(
              [
                  dbc.Col(dbc.Button("Login",color="primary",className="mb-3",href="#"),style={"padding-left":"20rem","width":"15rem"})]))
navbar = dbc.Navbar(
           html.Div(
                # Use row and col to control vertical alignment of logo / brand
                dbc.Row(
                    [
                        dbc.Col(
                            dbc.NavbarBrand(
                                html.H2((html.Img(src=LOGO1,height="60px",width="auto"))),style={"fontSize":"50px","padding-left":"10rem"})),
                        dbc.NavbarToggler(id="navbar-toggler"),
                         dbc.Collapse(sidebar,id="sidebar-collapse",navbar=True),
                         dbc.Collapse(button,id="button-collapse",navbar=True)
                        ],
                    align="center",
                    no_gutters=True,
                ),
             ),
          )

content = html.Div(id="page-content", style=CONTENT_STYLE)

data1= html.Div([
        html.H4('Substation Data Live Feed'),
        html.Table(id="live-update-text"),],style={"overflowX":"scroll"}) 

app = dash.Dash(__name__,server=server,external_stylesheets=[dbc.themes.BOOTSTRAP, FA])

app.config['suppress_callback_exceptions']=True

def table(devices):
    
    table_header=[
        html.Thead(html.Tr([html.Th('time'),html.Th('devId'),html.Th('sun angle') ,html.Th('tracker angle')#, html.Th('motor status') ,
         ]))]
    table_body=[
        html.Tbody(html.Tr([html.Td(dev.stamp),html.Td(dev.devId),html.Td(dev.sun),html.Td(dev.ta)]))for dev in devices]
    table=dbc.Table(table_header+table_body,bordered=True,striped=True,hover=True,style={"backgroundColor":"white"})
    return table
graph=html.Div([
    dcc.Dropdown(
        id='devices',
        options=[
            {'label': 'R1', 'value': 'R1 '},
            {'label': 'G2', 'value': 'G2 '},
            {'label': 'R2', 'value': 'R2 '}
        ],
        value='R1 ', style={"width":"auto"}),
html.Div(id='dd-output-container')
    ,


 #style={"backgroundColor":"grey","width":"auto"},
    dcc.Graph(id='graph-with-slider'),
    dcc.Interval(
            id='interval-component',
            interval=1*1000, # in milliseconds
            n_intervals=0
        )
        ])


"""def graph():
 #if df["devname"]=="dev_30":
  return dbc.Container([
                        html.H2("Graph"),
                        dcc.Graph(
       #  figure = go.Figure(go.Scatter(x = df['dateandtime'], y = df['rphvol'],)),
       #figure={"data": {"x":df["dateandtime"], "y": df["rphvol"]}}
                             figure={
                                'data': [
                                    {'x': df.tStamp, 'y':df.rphvol.where(df.devname=='dev_01'), 'name': 'rphvol'},
                                  #  {'x': df['tStamp'], 'y': df['yphvol'], 'z':df['devname'],  'name': 'yphvol'},
                                #    {'x': df['tStamp'], 'y': df['bphvol'], 'z':df['devname'],  'name': 'bphvol'},
                                   # {'x': df['tStamp'], 'y': df['avgvol'], 'type': 'bar', 'name': 'avgvol'}#if df['devId']  =="1",
                                   ],
            'layout': {
                'title': 'Voltage Visualization'
                }}
                        )])"""


x=app.layout = html.Div([navbar,content,data1,graph,dcc.Location(id="url",refresh=True)])
   
@app.callback(
    Output('graph-with-slider', 'figure'),
    [Input('devices', 'value')])#,Input('interval-component', 'n_intervals')])
def update_figure(selected_device):
#    connection = sqlite3.connect('data.db')#,check_same_thread=False)
    df=pd.read_sql("select * from devices",engine)

    filtered_df = df[df.devId == selected_device]
    print("filtered df=",filtered_df)

    return {
                                'data': [
                                    {'x': filtered_df.stamp, 'y':filtered_df.sun
                                    #.where(df.devname=='dev_01')
                                    , 'name': 'SPA'},
                                    {'x': filtered_df.stamp, 'y':filtered_df.ta
                                                                  , 'name': 'TA'},

                                  #  {'x': df['tStamp'], 'y': df['yphvol'], 'z':df['devname'],  'name': 'yphvol'},
                                #    {'x': df['tStamp'], 'y': df['bphvol'], 'z':df['devname'],  'name': 'bphvol'},
                                   # {'x': df['tStamp'], 'y': df['avgvol'], 'type': 'bar', 'name': 'avgvol'}#if df['devId']  =="1",
                                   ],
            'layout': {
                'title': 'SPA and TA'
                }}

@app.callback(Output("live-update-text", "children"),
              [Input("live-update-text", "className")])

def update_output_div(input_value):
    devices = DeviceModel.query.all()
    print("table device=",devices)
    return [html.Table(table(devices)
        )]
                      
@app.callback(
    Output("collapse", "is_open"),
    [Input("collapse-button", "n_clicks")],
    [State("collapse", "is_open")],)

def toggle_collapse(n, is_open):
    if n:
        return not is_open
    return is_open

for i in range(1,4):
    @app.callback(
         Output("dev-{%d}"%i, "active"),
         [Input("url", "pathname")],
         )
    def toggle_active_links(pathname):
        if pathname == "/":
        # Treat page 1 as the homepage / index
            return True, False, False
        return [pathname == "/Dev-{%d}"%i]

@app.callback([Output("page-content", "children")],
        [Input("url", "pathname")])

def render_page_content(pathname):
    if pathname in ["/", "/Dev-1"]:
        return [
                html.H4("Displays Device 1 Graph")]

    elif pathname in ["/", "/Dev-2"]:
        return [
                html.H4("Displays Device 2 Graph")]

    elif pathname in ["/", "/Dev-3"]:
        return [
                html.H4("Displays Device 3 Graph")]
    
   # If the user tries to reach a different page, return a 404 message
    return [404]


if __name__=="__main__":
    app.run_server(debug=True,port=8883)

