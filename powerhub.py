#!/usr/bin/env python3
from powerhub.args import args
import powerhub.reverseproxy
try:
    from powerhub.webdav import run_webdav
except ImportError as e:
    print(str(e))
    print("You have unmet dependencies. WebDAV won't be available. "
          "Consult the README.")
import threading
import sys
import signal
import logging


FORMAT = '%(asctime)-15s %(message)s'

logging.basicConfig(
    stream=sys.stdout,
    level=logging.DEBUG if args.DEBUG else logging.INFO,
    format=FORMAT,
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger(__name__)

import powerhub.flask  # noqa, comes after logging has been set up


def signal_handler(sig, frame):
    log.info("CTRL-C caught, exiting...")
    powerhub.reverseproxy.reactor.stop()


def start_thread(f, *args):
    threading.Thread(
        target=f,
        args=(*args,),
        daemon=True,
    ).start()


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    try:
        start_thread(run_webdav)
    except NameError:
        pass
    start_thread(powerhub.flask.shell_receiver.run_receiver,
                 args.REC_HOST, args.REC_PORT)
    start_thread(powerhub.flask.shell_receiver.run_provider)
    start_thread(powerhub.flask.run_flask_app)
    powerhub.reverseproxy.run_proxy()
