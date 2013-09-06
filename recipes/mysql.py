from cuisine import *

import config

def setup():
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
        run("mysqladmin -u root password %s" % config.DB_ROOT_PASSWORD)

    # create application user if applicable
    db_user = run('mysql -u %s -e "SELECT 1"' % config.DB_USER_NAME, warn_only=True)
    if db_user.return_code == 0:
        # operation was allowed -> application user is not password-protected or does not exist -
        # assume application db user does not exit
        run('mysql -u root -p%s -e "CREATE USER \'%s\'@\'localhost\' IDENTIFIED BY \'%s\'"'
            % (config.DB_ROOT_PASSWORD, config.DB_USER_NAME, config.DB_USER_PASSWORD))

        # create schema
        run('mysql -u root -p%s -e "CREATE SCHEMA %s DEFAULT CHARACTER SET utf8;"'
            % (config.DB_ROOT_PASSWORD, config.DB_SCHEMA), warn_only=True)

        # create tables, boot data
        create_db_script = '/home/ubuntu/create_db.sql'
        file_upload(create_db_script, './files/mysql/create_db.sql')
        run('mysql %s -u root -p%s < %s' % (config.DB_SCHEMA, config.DB_ROOT_PASSWORD, create_db_script))

        # grant access to application db user
        run('mysql -u root -p%s -e "GRANT SELECT,INSERT,UPDATE,DELETE,CREATE ON %s.* TO \'%s\'@\'localhost\';"'
            % (config.DB_ROOT_PASSWORD, config.DB_USER_NAME, config.DB_SCHEMA))
