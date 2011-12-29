import os
import readit

if __name__ == '__main__':
    config = readit.Configuration()
    value = os.environ.get('PORT')
    if value:
        config.port = int(value)
    value = os.environ.get('MONGOURL')
    if value:
        config.mongo_url = value
    value = os.environ.get('DEBUG')
    if value:
        config.debug = value.lower() == 'true' or str(value) == '1'
    readit.run(config)

