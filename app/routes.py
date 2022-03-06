# -*- coding: utf-8 -*-
from flask import render_template
from flask import send_from_directory
from flask import redirect
from app import app


#### Основные страницы ####
@app.route('/')
def index():
    return render_template('index.html', title='Samuro bot')

