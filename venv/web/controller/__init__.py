import sys

from web import app

from flask import Flask
from flask import render_template
from flask import jsonify

import setting

from web.controller.home import *
from web.controller.hold_stock import hold_stock_blueprint
from web.controller.index_pe import index_pe_blueprint
from web.controller.index import index_blueprint
from web.controller.money_flow_north_south import money_flow_blueprint

app.register_blueprint(hold_stock_blueprint)
app.register_blueprint(index_pe_blueprint)
app.register_blueprint(index_blueprint)
app.register_blueprint(money_flow_blueprint)
