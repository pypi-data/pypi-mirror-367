import logging

from ingress.config import MyLogger


def test():
    logger = MyLogger(logging.getLogger('test'))
    logger.info(msg='lala', foo='bar')
    logger.info(kwargs_only='yeah')
    logger.info('plain old message')
    logger.info('message', with_kwarg='jo')
    logger.info(name='gets converted to name_')
