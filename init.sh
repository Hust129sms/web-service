#!/bin/zsh
rm -rf data-dev.sqlite migrations
./fiiyu.py db init
./fiiyu.py db migrate
./fiiyu.py db upgrade
