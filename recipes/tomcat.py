from cuisine import *

import config


def setup():
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

        app_conf_folder = "/var/lib/tomcat7/conf/Catalina/%s/" % config.TOMCAT_APP
        app_conf_file = app_conf_folder + "/context.xml.default"    # root tomcat7 644
        dir_ensure(app_conf_folder, owner='root', group='tomcat7', mode=775)
        file_upload(app_conf_file, './files/tomcat/context.xml')
        file_ensure(app_conf_file, owner='root', group='tomcat7', mode=644)

        # database driver
        db_driver = '/usr/share/tomcat7/lib/' + os.path.basename(config.TOMCAT_DRIVER_PATH)
        already_installed = file_exists(db_driver)
        file_upload(db_driver, config.TOMCAT_DRIVER_PATH)
        file_ensure(db_driver, owner='tomcat7', group='tomcat7', mode=440)

        # create application directory
        # could use recursive=True but webapps would owned by root:root. Maybe a bug?
        dir_ensure('/home/ubuntu/webapps/', owner='tomcat7', group='tomcat7', mode=770)
        dir_ensure('/home/ubuntu/webapps/ROOT', owner='tomcat7', group='tomcat7', mode=770)

        # restart if fresh install
        if not already_installed:
            sudo('service tomcat7 restart')
