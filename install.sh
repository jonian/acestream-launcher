#!/usr/bin/env bash

pkgname=acestream-launcher
pkgfile=acestream_launcher

install() {
  mkdir -p "/opt/$pkgname"

  cp "$pkgfile.py" "/opt/$pkgname/$pkgfile.py"
  cp "$pkgname.desktop" "/opt/$pkgname/$pkgname.desktop"

  update-desktop-database "/opt/$pkgname"

  ln -s "/opt/$pkgname/$pkgfile.py" "/usr/bin/$pkgname"
  mv "/opt/$pkgname/$pkgname.desktop" "/usr/share/applications/$pkgname.desktop"
}

if [ "$EUID" -ne 0 ]
  then echo "Please run as root"
  else install
fi
