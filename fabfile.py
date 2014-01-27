import os, sys

from fabric.api import local, lcd, task, env
from fabric.colors import green
from fabric.operations import prompt, sudo, put, run
from fabric.context_managers import cd
from fabric.contrib.files import append, sed
import config

M2_HOME = '/usr/local/maven'
JAVA_HOME = '/usr/lib/jvm/java-1.7.0'
kuali_server_file = 'rice-dist-2.3.3-server.tar.bz2'
kuali_download_url = 'http://maven.kuali.org/release/org/kuali/rice/rice-dist/2.3.3/' + kuali_server_file
tomcat_home = '/usr/share/tomcat6'
mysql_connector_file = 'mysql-connector-java-5.1.26-bin.jar'

@task
def install():
    install_mysql()
    install_java()
    install_maven()
    install_tomcat()
    install_ricedb()
    configure_rice()
    disable_iptables()

# Disable iptables and make sure it doesn't start on boot
def disable_iptables():
    print(green('Disabling iptables'))
    sudo('service iptables stop')
    sudo('chkconfig iptables off')

# Install mysql and setup mysql for kuali rice
def install_mysql():
    print(green('Installing Mysql'))
    sudo('yum -y install mysql-server')
    sudo('mkdir -p /java/drivers')
    put(mysql_connector_file, '/java/drivers', True)
    sed('/etc/my.cnf', '\[mysqld\]', "[mysqld]\\nlower_case_table_names=1", '', True)
    sudo('service mysqld start')

    print(green('Create rice db user'))
    # @todo: mysql root password
    run("mysql -u root -e \"CREATE USER '%s'@'localhost' IDENTIFIED BY '%s'\"" % (env.mysql_rice_username , env.mysql_rice_password))
    run("mysql -u root -e \"CREATE USER '" + env.mysql_rice_username + "'@'%' IDENTIFIED BY '" + env.mysql_rice_password + "'\"")

    sudo('chkconfig --add mysqld')
    sudo('chkconfig --level 234 mysqld on')
    # @todo: set permissions

# Install java and set JAVA_HOME variable
def install_java():
    print(green('Installing Java'))
    sudo('yum -y install java-1.7.0-openjdk-devel')
    add_environment_var('JAVA_HOME', JAVA_HOME)

# Install maven and set maven variables
def install_maven():
    print(green('Installing Maven'))
    run('wget http://apache.osuosl.org/maven/maven-3/3.1.1/binaries/apache-maven-3.1.1-bin.tar.gz')
    sudo('tar xzf apache-maven-3.1.1-bin.tar.gz -C /usr/local')
    with(cd('/usr/local/')):
        sudo('ln -s apache-maven-3.1.1 maven')

    add_environment_var('M2_HOME', M2_HOME)
    add_environment_var('PATH', '${M2_HOME}/bin:${PATH}')
    add_environment_var('MAVEN_OPTS', '-Xmx1024m -XX:MaxPermSize=768m')

# Install tomcat6 and make sure it starts on boot
def install_tomcat():
    print(green('Installing Tomcat'))
    sudo('yum -y install tomcat6 tomcat6-admin-webapps tomcat6-docs-webapp tomcat6-webapps')
    sudo('chkconfig --add tomcat6')
    sudo('chkconfig --level 234 tomcat6 on')

# Install ricedb
def install_ricedb():
    print(green('Installing Rice DB'))
    sudo('chown -R %s /java' % env.user)
    run('mkdir -p /java/rice')
    with(cd('/java/rice')):
        run('wget %s' % kuali_download_url)
        run('tar -xjvf %s' % kuali_server_file)

    with(cd('/java/rice/db/demo')):
        # validate that maven can connect to mysql
        run('mvn validate -Pdb,mysql -Dimpex.database=rice -Dimpex.username=%s -Dimpex.password=%s' % (env.mysql_rice_username, env.mysql_rice_password)) #@todo: mysql root password
        run('mvn clean install -Pdb,mysql -Dimpex.database=rice -Dimpex.username=%s -Dimpex.password=%s' % (env.mysql_rice_username, env.mysql_rice_password))

# Configure kuali rice
def configure_rice():
    print(green('Configuring Rice'))
    sudo('cp /java/rice/kr-dev.war %s/webapps' % tomcat_home)
    sudo('cp /java/drivers/%s %s/lib' % (mysql_connector_file, tomcat_home))
    sudo('mkdir -p /usr/local/rice/plugins')
    sudo('mkdir -p /usr/local/rice/kew_attachments')
    sudo('mkdir -p /usr/local/rice/kew')

    with(cd('/usr/local/rice')):
        if env.use_local_rice_config:
            put('rice-config.xml', '.', True)
        else:
            sudo('cp /java/rice/config/rice-middleware/web/src/main/config/example-config/rice-config.xml .')

    sudo('service tomcat6 restart')
    
# Adds environment variable to .bashrc
def add_environment_var(variable, value):
    append('~/.bashrc', "\nexport %s=\"%s\"" % (variable, value) )
