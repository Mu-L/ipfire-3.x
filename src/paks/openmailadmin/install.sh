#!/bin/bash
. /opt/pakfire/lib/functions.sh

extract_files

mysql -u root < /srv/web/openmailadmin/mail.dump
