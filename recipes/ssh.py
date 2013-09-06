from cuisine import *
from fabric.api import *

import config


def use_ubuntu_passwordless():
    """Switch to ubuntu user, passwordless."""
    env.user = 'ubuntu'
    env.password = None


def use_root_password():
    """Switch to root user, with password. For early setup stages."""
    env.user = 'root'
    env.password = config.root_pwd


def setup():
    """Setup SSH for ubuntu user."""

    # switch to plain password ssh auth for root
    use_root_password()

    # add your public key to ubuntu authorized keys
    ssh_authorize('ubuntu', file_local_read(config.ssh_key))

    # TODO make sure ubuntu user exists and prevent root ssh http://feross.org/how-to-setup-your-linode/
