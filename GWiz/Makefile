#
# Make release
#
# Make clean
#

SCRIPTS = \
	makegwiz \
	makewiz  \

all: clean release postclean setowner

clean:
	rm -rf *.deb
	rm -f *~
	rm -f $(SCRIPTS)

postclean:
	sudo rm -rf GWIZ.deb WIZARDS.deb

scripts:
	make $(SCRIPTS)

release:
	make scripts
	sudo ./makegwiz
	sudo ./makewiz

setowner:
	sudo chown $(USER).$(USER) *.deb
