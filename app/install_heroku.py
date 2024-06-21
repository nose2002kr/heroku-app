import os
from loguru import logger

logger.debug('heroku cli install start')
os.system('curl https://cli-assets.heroku.com/install.sh | sh')
logger.debug('heroku cli installed')