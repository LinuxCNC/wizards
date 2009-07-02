#! /bin/bash

# Create a wizard debian release in the current directory

VERSION=0.1.2
RELEASE=WIZARDS.deb

rm -rf ${RELEASE}


# directory for the debian control stuff
mkdir -p ${RELEASE}/DEBIAN
mkdir -p ${RELEASE}/usr/share/gwiz

# the control stuff
echo "2.0" > ${RELEASE}/DEBIAN/debian-binary
cp control.wiz ${RELEASE}/DEBIAN/control

cp -R WIZARDS ${RELEASE}/usr/share/gwiz/
mv ${RELEASE}/usr/share/gwiz/WIZARDS ${RELEASE}/usr/share/gwiz/wizards


# build the file

dpkg-deb -b ${RELEASE} demowiz_${VERSION}_i386.deb
