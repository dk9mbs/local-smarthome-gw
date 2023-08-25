import logging

def create_logger(name):
    #logging.basicConfig(level=logging.WARNING, format='%(asctime)s %(name)s %(levelname)s:%(module)s - %(message)s')
    logging.basicConfig(level=logging.INFO , format='%(asctime)s %(name)s %(levelname)s:%(module)s - %(message)s')
    handler = logging.StreamHandler()
    logger = logging.getLogger(name)
    #logger.setLevel(logging.ERROR)
    #logger.addHandler(handler)
    return logger
