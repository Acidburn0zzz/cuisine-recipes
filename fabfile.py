from cuisine import *
from fabric.api import *

import config
from recipes import ssh, ubuntu, firewall, mysql, tomcat, nginx


def main():
    # By default, we connect with ubuntu user, passwordless.
    ssh.use_ubuntu_passwordless()


main()


def setup():
    """Setup our server.
    Ubuntu box, ssh, mysql, nginx, tomcat, ... the whole nine yard."""

    if not config.ec2:
        ubuntu.create_user()
        ssh.setup()
        ssh.use_ubuntu_passwordless()
        firewall.ufw()

    ubuntu.fix_locales()
    ubuntu.automatic_updates()
    ubuntu.scramble_password()

    mysql.setup()
    tomcat.setup()
    nginx.setup()
    ubuntu.scripts()
