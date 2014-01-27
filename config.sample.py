from fabric.api import env

# If set to true, it will try to copy a rice-config.xml in the current
# directory to set the kuali rice configuration parameters
env.use_local_rice_config = True

# db username & password of RICE mysql username
env.mysql_rice_username='username'
env.mysql_rice_password='password'

# username && password for host. The defaults below are for vagrant boxes
env.user = 'username'
env.password = 'password'

# host ip address or domain
env.hosts = '192.168.1.1'

