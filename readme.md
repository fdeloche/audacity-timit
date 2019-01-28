Audacity script for TIMIT files
=================================

Description
-----------

This script opens a wave file from the TIMIT database in Audacity and adds the phonetic data in Label Tracks using the segmentation provided by TIMIT.


Scripting
----------

This is a [script for Audacity](https://manual.audacityteam.org/man/scripting.html) written in Python 2.7.

Audacity has to be installed from source and *mod-script-pipe* enabled. [Compilation info](https://github.com/audacity/audacity/blob/master/INSTALL).

Help
----

Type

    python audacity-timit.py --help
for help. File can be chosen by the user or at random in the database. Works only when the Audacity project is empty at first.


Screenshot
-----------

![Screenshot](./screenshots/screenshot01.png)