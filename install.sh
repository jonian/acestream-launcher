#! /bin/sh

mkdir -p "/opt/acestream-launcher"

cp -a "*" "/opt/acestream-launcher"

update-desktop-database "/opt/acestream-launcher"

ln -s "/opt/acestream-launcher/acestream_launcher.py" "/usr/bin/acestream-launcher"
mv "/opt/acestream-launcher/acestream-launcher.desktop" "/usr/share/applications/acestream-launcher.desktop"
