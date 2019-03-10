import sys

from web import app

from flask import Flask
from flask import render_template
from flask import jsonify

import setting

from web.controller.home import *
from web.controller.hold_stock import hold_stock_blueprint

app.register_blueprint(hold_stock_blueprint)