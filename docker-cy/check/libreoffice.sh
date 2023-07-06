#!/bin/sh
soffice --headless --convert-to png --outdir /check /check/libreoffice.sh
killall soffice;exit 0