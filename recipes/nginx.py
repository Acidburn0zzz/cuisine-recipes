from cuisine import *

import config

def setup():
    """Setup nginx."""
    package_ensure('nginx-light')
    with mode_sudo():
        # remove default configuration
        sudo('rm -f /etc/nginx/sites-enabled/default', warn_only=True)
        sudo('rm -f /etc/nginx/sites-available/default', warn_only=True)

        # push our configuration
        available = '/etc/nginx/sites-available/%s' % config.NGINX_APP
        file_upload(available, './files/nginx/nginx.conf')
        file_ensure(available, owner='root', group='root', mode=644)
        file_link(available, '/etc/nginx/sites-enabled/%s' % config.NGINX_APP)

        upstart_ensure('nginx')
