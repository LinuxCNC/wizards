#! /bin/bash

# Create a gwiz debian release in the current directory

VERSION=0.1.3
RELEASE=GWIZ.deb

rm -rf ${RELEASE}

# directory for the debian control stuff
mkdir -p ${RELEASE}/DEBIAN

mkdir -p ${RELEASE}/usr/share/applications
mkdir -p ${RELEASE}/usr/share/pixmaps
mkdir -p ${RELEASE}/usr/share/applications
mkdir -p ${RELEASE}/usr/share/gwiz/images
mkdir -p ${RELEASE}/usr/share/gwiz/wizards
mkdir -p ${RELEASE}/usr/share/doc/gwiz
mkdir -p ${RELEASE}/usr/bin


# the control stuff
echo "2.0" > ${RELEASE}/DEBIAN/debian-binary
cp control.gwiz ${RELEASE}/DEBIAN/control

cp gwiz.desktop ${RELEASE}/usr/share/applications
#cp gwiz.py ${RELEASE}/usr/bin

# the icon to appear in the application menu
cp bitmaps/wizicon.png ${RELEASE}/usr/share/pixmaps/gwizicon.png

# the icon and the splash screen
cp bitmaps/wizicon.png ${RELEASE}/usr/share/gwiz/images
cp bitmaps/splash.png ${RELEASE}/usr/share/gwiz/images

# the buttons
cp buttons/*.png ${RELEASE}/usr/share/gwiz/images

# the executables
cp gwiz.py ${RELEASE}/usr/bin/gwiz
chmod 755  ${RELEASE}/usr/bin/gwiz
cp About.py ${RELEASE}/usr/bin/About.py
chmod 755  ${RELEASE}/usr/bin/About.py

cp wiz2gcode.py ${RELEASE}/usr/bin/wiz2gcode
chmod 755  ${RELEASE}/usr/bin/wiz2gcode

# the docs
cp doc/* ${RELEASE}/usr/share/doc/gwiz

# build the file
dpkg-deb -b ${RELEASE} gwiz_${VERSION}_i386.deb
