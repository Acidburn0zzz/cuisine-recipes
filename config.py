from cuisine import *
from fabric.api import *


# Cuisine environment
env.use_ssh_config = False

# Your host(s)
#env.hosts = ['myhost.com']

# Deploying to Amazon EC2 instance?
# If True, user creation, ssh setup and firewall configuration will be skipped
ec2 = False

# ssh key. Not for EC2
ssh_key = '/Users/me/.ssh/id_rsa.pub'

# Root password. Not for EC2
root_pwd = 'root_pwd'

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
