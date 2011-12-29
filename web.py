import os
import readit

if __name__ == '__main__':
    port = os.environ.get('PORT')
    if port:
        readit.application.PORT = int(port)
    readit.application.run()

