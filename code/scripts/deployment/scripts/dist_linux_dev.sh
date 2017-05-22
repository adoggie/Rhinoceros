#!/bin/bash

pwd=$(cd `dirname $0`;pwd)
alias cp='cp -f'
#alias cp='rsync'
#alias rsync='rsync -r'

#SERVICE_DIR=$(echo $1)/services
RELEASE_DIR=$pwd/release

if [ $# == 0 ]; then
  echo 'Warning: params is 0, default: [release]'
else
  RELEASE_DIR=$(echo $1)
fi
LEMON_DIR=$(echo $RELEASE_DIR)/lemon
echo $RELEASE_DIR






mkdir -p $RELEASE_DIR/nginx/log
mkdir -p $LEMON_DIR/
mkdir -p $LEMON_DIR/src/
mkdir -p $LEMON_DIR/test/
mkdir -p $LEMON_DIR/bin

mkdir -p $RELEASE_DIR/file
mkdir -p $RELEASE_DIR/package

SRC_HOME=$pwd/..
echo $SRC_HOME


rsync -rvt $SRC_HOME/3rd/Django-1.6.5.tar.gz $RELEASE_DIR/package
rsync -rvt $SRC_HOME/3rd/poster-0.8.1.tar.gz $RELEASE_DIR/package


#cp -r $pwd/../client $LEMON_DIR
rsync -rvt $pwd/../client $LEMON_DIR

rsync -rvt $pwd/../etc $LEMON_DIR

rsync -rvt $pwd/../lemon $LEMON_DIR
rsync -rvt $pwd/../libs $LEMON_DIR
rsync -rvt $pwd/../model $LEMON_DIR
rsync -rvt $pwd/../service $LEMON_DIR


rsync -rvt $pwd/../src/web $LEMON_DIR/src
rsync -rvt $pwd/../init_script.py $LEMON_DIR



rsync -rvt $pwd/../test/init_org_tree.py $LEMON_DIR/test
rsync -rvt $pwd/../test/init_org_user.py $LEMON_DIR/test


rsync clean.sh docker_start.sh service_start.sh init_pgsql.sh service_stop.sh $RELEASE_DIR
rsync -rvt $pwd/../etc/nginx  $RELEASE_DIR/
rsync -rvt $pwd/scripts $RELEASE_DIR/

#rsync -rvt /opt/kingsoft $RELEASE_DIR/
rsync -rvt $SRC_HOME/src/pdf_converter/pdf_convert $LEMON_DIR/bin
rsync -rvt $SRC_HOME/service/file_convert $RELEASE_DIR

#echo  ROOT_DIR=\'/opt/lemon\'  >> $LEMON_DIR/model/django/lemon/settings.py
cat $pwd/settings_patch.txt >> $LEMON_DIR/model/django/lemon/settings.py

#echo -e '\n\nimport settings_patch' >> $LEMON_DIR/init_script.py
#echo -e 'settings_patch.patch(settings)' >> $LEMON_DIR/init_script.py
#rsync -vt $pwd/settings_patch.py $LEMON_DIR

#rsync -rvt /home/openoffice4 $RELEASE_DIR

sed -e 's/server1/localhost/' -e 's/192.168.10.99/localhost/' $pwd/../etc/settings.yaml > $LEMON_DIR/etc/settings.yaml
sed -e 's/server1/localhost/' -e 's/server2/localhost/' $pwd/../etc/services.xml > $LEMON_DIR/etc/services.xml

