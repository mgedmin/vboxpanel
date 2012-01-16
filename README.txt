VirtualBox Panel
================

This is a small web app that lets me control a few VirtualBox virtual machines
on our BuildBot server.

.. figure:: http://i.imgur.com/uxIPp.png
   :alt: screenshot
   :width: 640
   :height: 388


Running a development version
-----------------------------

After cloning this repository do ::

    make run

Make should take care of everything.  You need make (obviously),
python, virtualenv, VirtualBox (I used virtualbox-ose from Ubuntu universe),
and an Internet connection (to download Pyramid etc. from PyPI).


Getting screenshots via VNC
---------------------------

Install `vncsnapshot`_ on the host.  Install a VNC server on the guest
(`TightVNC`_ works fine for Windows guests).

.. _vncsnapshot: http://packages.ubuntu.com/search?keywords=vncsnapshot
.. _TightVNC: http://www.tightvnc.com/download.php

Set up guest port mapping for each guest machine like this (using different
values in the 590x range for HostPort)::

    VBoxManage setextradata VMNAME "VBoxInternal/Devices/pcnet/0/LUN#0/Config/vnc/HostPort" 5901
    VBoxManage setextradata VMNAME "VBoxInternal/Devices/pcnet/0/LUN#0/Config/vnc/GuestPort" 5900
    VBoxManage setextradata VMNAME "VBoxInternal/Devices/pcnet/0/LUN#0/Config/vnc/Protocol" TCP


Security
--------

There is none.  Use a front-end server like Apache with mod_wsgi to prevent
unauthorized access.  Do not use ``make run`` or ``bin/pserve development.ini``
on a multi-user machine.


Deployment
----------

Here's a sample Apache config::

  WSGIScriptAlias /vboxpanel "/opt/vboxpanel/pyramid.wsgi"
  WSGIDaemonProcess vboxpanel user=buildbot group=buildbot processes=2 threads=5 \
    maximum-requests=1000 umask=0007 display-name=wsgi-vboxpanel \
    python-path=/opt/vboxpanel/lib/python2.6/site-packages
  WSGIProcessGroup vboxpanel
  WSGIPassAuthorization on

  <Location /vboxpanel>
    AuthType Basic
    AuthName "example.com"
    AuthUserFile /etc/apache2/vboxpanel.passwd
    Require valid-user
  </Location>

Be sure to use HTTPS.
