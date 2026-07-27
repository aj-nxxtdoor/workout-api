"""
Shared extension instances.

Keeping db and migrate here (instead of instantiating them directly in
app.py) avoids circular imports between app.py and models.py, since both
need access to `db`.
"""
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()
