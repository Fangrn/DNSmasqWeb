#!/usr/bin/python
#-*- coding:utf8 -*-
# Desgin By Xiaok
from xk_application.xk_main import *

class HelpHandler(BaseHandler):
    def get(self):
        self.render2("xk_help.html")

    
