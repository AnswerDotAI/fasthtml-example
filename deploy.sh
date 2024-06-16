#!/usr/bin/env bash
: "${1:?No arguments provided}"

railway init -n $1
railway up -c
railway domain
fh_railway_link
# railway volume add -m /app/data

