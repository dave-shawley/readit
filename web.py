import os
import readit

if __name__ == '__main__':
    config = readit.Configuration()
    port = os.environ.get('PORT')
    if port:
        config.port = int(port)
    readit.run(config)

