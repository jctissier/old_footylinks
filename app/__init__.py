from flask import Flask, render_template
from app.util import gzipped


# Define the WSGI application object
app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 2628000       # This caches all static files (1 month)


# Import a module / component using its blueprint handler variable (labels) -> Import all the controllers
from app.highlights.controllers import highlight as highlight_route
from app.livestreams.controllers import livestream as livestream_route
from app.stats.controllers import stat as stats_route
from app.config import config as config_route


# Register blueprint(s)
app.register_blueprint(highlight_route)                         # Highlights
app.register_blueprint(livestream_route)                        # Live Streams
app.register_blueprint(stats_route)                             # Fixtures & League Stats
app.register_blueprint(config_route)                            # Config functions for response compression


# 404 - wrong URL Error Handling
@app.errorhandler(404)
def not_found():
    return render_template('404.html'), 404
