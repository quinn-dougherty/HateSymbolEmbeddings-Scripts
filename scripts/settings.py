#!/usr/bin/env python
import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

BASILICA_KEY = os.getenv('BASILICA_KEY')
DIREC = os.getenv('DIREC')
FILES_DIR = os.getenv('FILES_DIR')
