import logging

logger = logging.getLogger(__name__)

class Config2(object):

    PROGRESS = """
Percentage : {0}%
Done: {1}
Total: {2}
Speed: {3}/s
ETA: {4}
    """
