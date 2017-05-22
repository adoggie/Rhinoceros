#!/bin/bash

pwd=$(cd `dirname $0`;pwd)


pkill python
pgrep uwsgi | xargs kill -9

