#!/bin/bash

pwd=$(cd `dirname $0`;pwd)

pgrep uwsgi | xargs kill -9

