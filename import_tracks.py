#!/usr/bin/python

import gpxpy
import gpxpy.gpx
import subprocess
from os import path

def import_from_device(device_name, output_path, gpsbabel_path='gpsbabel'):
    retcode = subprocess.call([
        gpsbabel_path,
        '-t',
        '-i', 'garmin',
        '-f', device_name,
        '-o', 'gpx',
        '-F', output_path])
    return retcode == 0

def process_tracks(gpx_path, output_dir, overwrite=False):
    f = open(gpx_path, 'r')
    gpx = gpxpy.parse(f)

    for t in gpx.tracks:
        print "Processing track %s" % t.name
        if len(t.segments) > 0 and len(t.segments[0].points) > 0:
            p = t.segments[0].points[0]
            filename = '%s-%s.gpx' % (p.time.strftime('%Y-%m-%d'), t.name)
            track_path = path.join(output_dir, filename)
            if overwrite or not path.exists(track_path):
                with open(track_path, 'w') as track_file:
                    track_file.write(gpxpy.gpx.GPX(tracks=[t]).to_xml())
                    print "Wrote file %s" % filename
        else:
            print "(no segments and/or points found)"

if __name__ == '__main__':
    import argparse
    import tempfile
    import sys

    parser = argparse.ArgumentParser()
    parser.add_argument('--from-device', default='usb:')
    parser.add_argument('--overwrite', action='store_true', default=False)
    parser.add_argument('file', nargs='*')

    args = parser.parse_args(sys.argv[1:len(sys.argv)])

    if args.from_device and len(args.file) == 0:
        f, gpx_path = tempfile.mkstemp()
        if not import_from_device(args.from_device, gpx_path):
            print "Import from device failed"
            sys.exit(1)
    else:
        gpx_path = args.file[0]

    process_tracks(gpx_path, path.expanduser('~/.gps-log/tracks'), args.overwrite)
