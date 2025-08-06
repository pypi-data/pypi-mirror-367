import logging

def get_logger(name: str = "nwm.explorer") -> logging.Logger:
    """
    Generate and a return a logger.

    Paramters
    ---------
    name: str, optional, default 'nwm.explorer'
        Name of the logger.
    
    Returns
    -------
    Logger
    """
    logger = logging.getLogger(name)
    if not logger.hasHandlers():
        logger.setLevel(logging.INFO)
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        logger.addHandler(ch)
    return logger
