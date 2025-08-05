import pandas as pd
import copy
import openpyxl  # для сохранения эксель файлов
import os
import shutil
import copy
import logging
import pythoncom
from datetime import date
pythoncom.CoInitializeEx(0)
import win32com.client
import time
# блок импорта отправки почты
import smtplib, ssl
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.utils import formatdate
from email import encoders

from functools import wraps
import time

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import calendar