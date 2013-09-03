from cuisine import *
from fabric.api import *

# Cuisine environment
env.use_ssh_config = False

# Your host(s)
env.hosts = ['vps31544.ovh.net']

# Deploying to Amazon EC2 instance?
# If True, user creation, ssh setup and firewall configuration will be skipped
ec2 = False

# ssh key. Not for EC2
ssh_key = '/Users/me/.ssh/id_rsa.pub'

# Root password. Not for EC2
root_pwd = 'root_password'

# Database
DB_SCHEMA = 'db_name'
DB_USER_NAME = DB_SCHEMA                                            # let's keep it simple
DB_ROOT_PASSWORD = 'db_root_password'
DB_USER_PASSWORD = 'db_user_password'

# Tomcat
TOMCAT_DRIVER_PATH = '/path/to/driver/mysql-connector-java-5.1.22.jar'
TOMCAT_APP = 'myapp'

# nginx
NGINX_APP = TOMCAT_APP


def use_ssh_ubuntu_passwordless():
    """Switch to ubuntu user, passwordless."""
    env.user = 'ubuntu'
    env.password = None


def use_ssh_root_password():
    """Switch to root user, with password. For early setup stages."""
    env.user = 'root'
    env.password = root_pwd


def main():
    # By default, we connect with ubuntu user, passwordless.
    use_ssh_ubuntu_passwordless()


main()


def setup():
    """Setup our server.
    Ubuntu box, ssh, mysql, nginx, tomcat, ... the whole nine yard."""

    if not ec2:
        create_ubuntu_user()
        setup_ssh()
        use_ssh_ubuntu_passwordless()                       # switch to ubuntu user, passwordless
        ufw()

    fix_locales()
    automatic_updates()
    scramble_password()
    mysql()
    tomcat()
    nginx()
    scripts()


def version():
    """Print the OS version. For testing purpose."""

    # switch to plain password ssh auth for root
    use_ssh_root_password()

    version = run('cat /proc/version')
    print version


def create_ubuntu_user():
    """Create the ubuntu user. Add them to sudoer."""

    # switch to root plain password ssh
    use_ssh_root_password()

    # ubuntu user
    user_ensure(name='ubuntu', home='/home/ubuntu', shell='/bin/bash')

    # sudoer
    file_update(
        '/etc/sudoers',
        lambda _: text_ensure_line(
            _,
            "%ubuntu ALL=(ALL) NOPASSWD:ALL")
    )


def setup_ssh():
    """Setup SSH for ubuntu user."""

    # switch to plain password ssh auth for root
    use_ssh_root_password()

    # add your public key to ubuntu authorized keys
    ssh_authorize('ubuntu', file_local_read(ssh_key))

    # TODO make sure ubuntu user exists and prevent root ssh http://feross.org/how-to-setup-your-linode/


def ufw():
    """Configure and enable ufw (uncomplicated firewall)"""
    package_ensure('ufw')

    status = sudo('ufw status | head -1')

    if 'inactive' in status:
        with mode_sudo():
            file_update(
                '/etc/default/ufw',
                lambda _: 'IPV6=no' if _ == 'IPV6=yes' else _
            )
        sudo('ufw allow ssh')
        sudo('ufw allow http')
        sudo('ufw allow https')
        sudo('ufw --force enable')


def iptables():
    """Configure iptables. Depending on your tastes, you may prefer using ufw/"""
    # https://help.ubuntu.com/community/IptablesHowTo
    # https://www.digitalocean.com/community/articles/how-to-set-up-a-firewall-using-ip-tables-on-ubuntu-12-04
    status = sudo('iptables -L | grep ssh')
    if 'ssh' not in status:
        sudo('iptables -A INPUT -p tcp --dport ssh -j ACCEPT')
        sudo('iptables -A INPUT -p tcp --dport 80 -j ACCEPT')
        sudo('iptables -A INPUT -p tcp --dport 443 -j ACCEPT')
        sudo('iptables -A INPUT -j DROP')
        sudo('iptables -I INPUT 1 -i lo -j ACCEPT')
        sudo('iptables-save > /etc/iptables.rules')

        iptablesload = '/etc/network/if-pre-up.d/iptablesload'
        file_upload(iptablesload, './files/iptables/iptablesload.txt')
        file_ensure(iptablesload, owner='root', group='root', mode=755)

        iptablessave = '/etc/network/if-post-down.d/iptablessave'
        file_upload(iptablessave, './files/iptalbes/iptablessave.txt')
        file_ensure(iptablessave, owner='root', group='root', mode=755)


def scramble_password():
    # TODO
    return


def fix_locales():
    """Fix locales to avoid nasty warning messages on upgrades/install."""
    # for ubuntu user
    locale_ensure('en_US.UTF-8')

    # do it again for root :/
    with mode_sudo():
        locale_ensure('en_US.UTF-8')

    return

    # above is ok but errors may still be emitted - you can do it the hard way (not tested):
    path = '/etc/default/locale'
    if not text_get_line(path, 'LC_ALL=en_US.UTF-8'):
        # Add lines
        file_update(
            path,
            lambda _:text_ensure_line(_,
            'LC_ALL="en_US.UTF-8"',
            'LANG="en_US.UTF-8"',
            'LANGUAGE="en_US.UTF-8"')
        )

        # Configure
        sudo('dpkg-reconfigure locales')
        sudo('locale-gen en_US.UTF-8')


def automatic_updates():
    # TODO automatic updates
    return


def mysql():
    """Setup MySQL.
    Includes creation of a dedicated user and schedma, limited privileges, enforcing root password
    and tables + data creation."""

    # mysql package
    package_ensure('mysql-server')

    # configuration file
    config_file = '/etc/mysql/my.cnf'
    file_upload(config_file, './files/mysql/my.cnf', sudo=True)
    # FIXME check owner + mode
    with mode_sudo():
        file_ensure(config_file, owner='root', group='root', mode=644)

    # create root user if applicable
    root_user = run('mysql -u root -e "SELECT 1"', warn_only=True)
    if root_user.return_code == 0:
        # operation was allowed -> root is not password-protected
        run("mysqladmin -u root password %s" % DB_ROOT_PASSWORD)

    # create application user if applicable
    db_user = run('mysql -u %s -e "SELECT 1"' % DB_USER_NAME, warn_only=True)
    if db_user.return_code == 0:
        # operation was allowed -> application user is not password-protected or does not exist -
        # assume application db user does not exit
        run('mysql -u root -p%s -e "CREATE USER \'%s\'@\'localhost\' IDENTIFIED BY \'%s\'"'
            % (DB_ROOT_PASSWORD, DB_USER_NAME, DB_USER_PASSWORD))

        # create schema
        run('mysql -u root -p%s -e "CREATE SCHEMA %s DEFAULT CHARACTER SET utf8;"'
            % (DB_ROOT_PASSWORD, DB_SCHEMA), warn_only=True)

        # create tables, boot data
        create_db_script = '/home/ubuntu/create_db.sql'
        file_upload(create_db_script, './files/mysql/create_db.sql')
        run('mysql %s -u root -p%s < %s' % (DB_SCHEMA, DB_ROOT_PASSWORD, create_db_script))

        # grant access to application db user
        run('mysql -u root -p%s -e "GRANT SELECT,INSERT,UPDATE,DELETE,CREATE ON %s.* TO \'%s\'@\'localhost\';"'
            % (DB_ROOT_PASSWORD, DB_USER_NAME, DB_SCHEMA))


def tomcat():
    """Setup Tomcat."""
    # first the jdk to avoid getting JRE6 i.o. 7
    package_ensure('openjdk-7-jre-headless')

    # then tomcat itself
    package_ensure('tomcat7')

    # tip: check permissions with: stat -c "%U %G %a %n" file_name

    with mode_sudo():
        cfg = '/etc/default/tomcat7'                                # root root 644
        file_upload(cfg, './files/tomcat/tomcat7')
        file_ensure(cfg, owner='root', group='root', mode=644)

        server_xml = '/var/lib/tomcat7/conf/server.xml'             # root tomcat7 644
        file_upload(server_xml, './files/tomcat/server.xml')
        file_ensure(server_xml, owner='root', group='tomcat7', mode=644)

        app_conf_folder = "/var/lib/tomcat7/conf/Catalina/%s/" % TOMCAT_APP
        app_conf_file = app_conf_folder + "/context.xml.default"    # root tomcat7 644
        dir_ensure(app_conf_folder, owner='root', group='tomcat7', mode=775)
        file_upload(app_conf_file, './files/tomcat/context.xml')
        file_ensure(app_conf_file, owner='root', group='tomcat7', mode=644)

        # database driver
        db_driver = '/usr/share/tomcat7/lib/' + os.path.basename(TOMCAT_DRIVER_PATH)
        already_installed = file_exists(db_driver)
        file_upload(db_driver, TOMCAT_DRIVER_PATH)
        file_ensure(db_driver, owner='tomcat7', group='tomcat7', mode=440)

        # create application directory
        # could use recursive=True but webapps would owned by root:root. Maybe a bug?
        dir_ensure('/home/ubuntu/webapps/', owner='tomcat7', group='tomcat7', mode=770)
        dir_ensure('/home/ubuntu/webapps/ROOT', owner='tomcat7', group='tomcat7', mode=770)

        # restart if fresh install
        if not already_installed:
            sudo('service tomcat7 restart')


def nginx():
    """Setup nginx."""
    package_ensure('nginx-light')
    with mode_sudo():
        # remove default configuration
        sudo('rm -f /etc/nginx/sites-enabled/default', warn_only=True)
        sudo('rm -f /etc/nginx/sites-available/default', warn_only=True)

        # push our configuration
        available = '/etc/nginx/sites-available/%s' % NGINX_APP
        file_upload(available, './files/nginx/nginx.conf')
        file_ensure(available, owner='root', group='root', mode=644)
        file_link(available, '/etc/nginx/sites-enabled/%s' % NGINX_APP)

        upstart_ensure('nginx')


def scripts():
    """Deploy user scripts."""
    package_ensure('unzip')

    deploy_script = '/home/ubuntu/deploy.sh'
    file_upload(deploy_script, './files/scripts/deploy.sh')
    file_ensure(location=deploy_script, mode=700)

    # Note: script should copy backup to remote host
    backup_script = '/home/ubuntu/backup.sh'
    file_upload(backup_script, './files/scripts/backup.sh')
    file_ensure(location=backup_script, mode=700)
    dir_ensure('/home/ubuntu/backups', mode=700)
