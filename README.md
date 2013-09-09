GPS Track Import
================

Very basic script to import tracks from a GPS unit using [GPSBabel](http://www.gpsbabel.org/) and store them locally in an easily manageable format: one GPX file per tracks, plus metadata in JSON format.

Requirements
------------

* Python 2.7
* [gpxpy](https://github.com/tkrajina/gpxpy)

Usage
-----

```
import_tracks.py [-h] [--from-device FROM_DEVICE] [--overwrite]
                        [files [files ...]]
```

This assumes you have GPSBabel installed and on your path.

Unless ```--from-device``` is used, tracks will be imported from ```usb:```. 

Optionally, one or more GPX files can be supplied, from which tracks will be imported instead; ```--from-device``` will be ignored in this case.

Unless ```--overwrite``` is specified, the script will not overwrite any data that already exists (to avoid overwriting any manual changes done after an import).

Storage format
--------------

The script stores the imported tracks in your home directory under a directory called ```.gps-log/tracks```.

Two files are stored per track: a GPX file with the track's positions, and a JSON file containing metadata/summary information about the track.

A file called ```index.json``` is also produced, containing a summary of all tracks currently stored in the directory.
