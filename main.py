from os import getenv

from WebApp import WebApp

"""
This is the main file of the Web application. It's starting here.
"""

app = WebApp(__name__)

if __name__ == '__main__':
    app.run(port=getenv('port'), host=getenv('server'))
    # TODO: adding a new stuff by admin
    # TODO: managing orders by stuff
    # TODO: hosting
    # FIXME: view.
