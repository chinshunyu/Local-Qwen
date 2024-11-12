from flask import Flask, request, jsonify, make_response
from chatbot import ChatBot, SyntacticBot
from flask_cors import CORS
import uuid
from gevent.pywsgi import WSGIServer
from gevent import monkey
from model import qw_model


chatbot = ChatBot(qw_model=qw_model)
syntatic_chatbot = SyntacticBot(qw_model=qw_model)
