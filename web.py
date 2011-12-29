import os
import readit

if __name__ == '__main__':
    config = readit.get_defaults()
    port = os.environ.get('PORT')
    if port:
        config['port'] = int(port)
    readit.run(config)

