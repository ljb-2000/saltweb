
saltweb 运维管理平台
-
###部署环境说明

cents6.2<br>
django 1.6.2<br>
salt-master 2014.1.0-1<br>
Python 2.6.6<br>

###saltweb部署
wget --no-check-certificate https://pypi.python.org/packages/source/s/setuptools/setuptools-2.1.tar.gz<br>
tar zxf setuptools-2.1.tar.gz<br>
cd setuptools-2.1<br>
python setup.py install<br>
cd ..<br>
wget --no-check-certificate https://pypi.python.org/packages/source/p/pip/pip-1.5.tar.gz<br>
tar zxf pip-1.5.tar.gz<br>
cd pip-1.5<br>
python setup.py install<br>
cd ..<br>
yum -y install gcc gcc-c++ python-devel<br>
yum install php-devel mysql mysql-server mysql-devel nginx php-mysql php php-fpm MySQL-python<br>
yum install salt-master salt-minion salt<br>
yum install rrdtool-devel python-rrdtool<br>
pip install django<br>
pip install uwsgi<br>
pip install apscheduler paramiko<br>
sed -i 's/\(.*\)HAVE_DECL_MPZ_POWM_SEC/#\1HAVE_DECL_MPZ_POWM_SEC/' /usr/lib64/python2.6/site-packages/Crypto/Util/number.py<br>
sed -i 's/\(.*\)mpz_powm_sec/#\1mpz_powm_sec/' /usr/lib64/python2.6/site-packages/Crypto/Util/number.py<br>
mkdir /etc/salt/master.d<br>
cat << EOF > /etc/salt/master.d/group.conf<br>
nodegroups:<br>
    master: testgroups<br>
EOF<br>
echo "auto_accept: True" >>/etc/salt/master<br>
grep "^default_include: master.d/\*\.conf" /etc/salt/master >/dev/null 2>&1|| echo "default_include: master.d/*.conf" >> /etc/salt/master<br>


/etc/init.d/mysqld start<br>
chkconfig mysqld on<br>
mysqladmin -uroot password 123<br>
mysql -uroot -p123 -e "create database saltweb default charset utf8"<br>

./manage.py syncdb <br>
注：第一次执行syncdb会提示创建超级管理员，该账号为saltweb的登录账号及后台超级管理员<br>
./manage.py runserver 0.0.0.0:8001<br>

sed -i 's/^user.*/user   root;/' /etc/nginx/nginx.conf<br>
cat << EOF > /etc/nginx/conf.d/virtual.conf<br>
server {<br>
    listen          80;<br>
    server_name    www.hhr.com;<br>
    charset utf-8;<br>
    index index.html index.htm index.php;<br>
    access_log  /var/log/nginx/hhr.access.log;<br>
    error_log  /var/log/nginx/hhr.error.log;<br>
    location / {<br>
        uwsgi_pass     127.0.0.1:8008;<>br
        include        uwsgi_params;<br>
    }<br>
    location /static/ {<br>
        alias  /root/saltweb/saltweb/static/;<br>
        index  index.html index.htm;<br>
    }<br>
}<br>
EOF<br>

注意：如果saltweb在/root目录下，必须修改nginx的配置文件改成root用户，否则访问css报403错误<br>
python /root/saltweb/saltweb/init.py<br>
python /root/saltweb/saltweb/salt_service.py start<br>
python /root/saltweb/saltweb/salt_service.py status<br>

###测试
修改本机host，添加"172.16.1.237 www.hhr.com",访问http://www.hhr.com/salt
