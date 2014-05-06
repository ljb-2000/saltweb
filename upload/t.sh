#!/bin/sh

chattr -i /etc/sudoers
sed -i 's/Defaults    requiretty/#Defaults    requiretty/' /etc/sudoers
chattr +i /etc/sudoers
