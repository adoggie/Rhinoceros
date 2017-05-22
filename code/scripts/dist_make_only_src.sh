#!/bin/bash

pwd=$(cd `dirname $0`;pwd)
alias cp='cp -f'

RELEASE_DIR=$pwd/release

if [ $# == 0 ]; then
  echo 'Warning: params is 0, default: [release]'
else
  RELEASE_DIR=$(echo $1)
fi
LEMON_DIR=$(echo $RELEASE_DIR)/rhino
echo $RELEASE_DIR

#mkdir -p $RELEASE_DIR/nginx/log
mkdir -p $LEMON_DIR/
mkdir -p $LEMON_DIR/libs

SRC_HOME=$pwd/..
echo $SRC_HOME

rsync -rvt $pwd/deployment/* $LEMON_DIR
rsync -rvt $pwd/../backends/Adapters/oryx $LEMON_DIR/services/ --exclude '.svn' --exclude '.idea' --exclude '*.pyc' --exclude 'etc' --exclude '*.log'
rsync -rvt $pwd/../backends/DataAggregator $LEMON_DIR/services/ --exclude '.svn' --exclude '.idea' --exclude '*.pyc' --exclude 'etc' --exclude '*.log'

rsync -rvt $pwd/../backends/DataShuffler $LEMON_DIR/services/ --exclude '.svn' --exclude '.idea' --exclude '*.pyc' --exclude 'etc' --exclude '*.log'

rsync -rvt $pwd/../backends/DataTracer $LEMON_DIR/services/ --exclude '.svn' --exclude '.idea' --exclude '*.pyc' --exclude 'etc' --exclude '*.log'

rsync -rvt $pwd/../backends/LocUserService $LEMON_DIR/services/ --exclude '.svn' --exclude '.idea' --exclude '*.pyc' --exclude 'etc' --exclude '*.log'

rsync -rvt $PYTHONPATH/* $LEMON_DIR/libs --exclude '.svn' --exclude '.idea' --exclude '*.pyc' --exclude '*.log'




