import logging, os
import inspect

logging.basicConfig(filename='_%s.log' % os.path.basename(inspect.stack()[-1][1]).rstrip(".py"), level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
if "debug" in os.environ and os.environ["debug"] == "1":
    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)

    # set a format which is simpler for console use
    formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
    console.setFormatter(formatter)
    logging.getLogger().addHandler(console)
