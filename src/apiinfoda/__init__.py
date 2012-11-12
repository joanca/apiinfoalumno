from flask import Flask
import settings

app = Flask('apiinfoda')
app.config.from_object('apiinfoda.settings')

import urls