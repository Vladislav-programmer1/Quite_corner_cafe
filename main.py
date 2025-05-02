from os import getenv

from WebApp import WebApp

app = WebApp(__name__)

if __name__ == '__main__':
    app.run(port=getenv('port'), host=getenv('server'))
