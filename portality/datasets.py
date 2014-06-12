import json
from portality.core import app
import os

with open(os.path.join(app.config['BASE_FILE_PATH'], 'resources', 'domain_uni_lookup.json'), 'rb') as f:
    domain_uni_lookup = json.loads(f.read())