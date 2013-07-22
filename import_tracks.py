#!/usr/bin/python

import gpxpy
import gpxpy.gpx
import subprocess
from os import path
import json
import datetime
import time

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
    n_processed = 0
    n_written = 0

    for t in gpx.tracks:
        if len(t.segments) > 0 and len(t.segments[0].points) > 0:
            p = t.segments[0].points[0]
            name = '%s-%s' % (p.time.strftime('%Y-%m-%d'), t.name)
            gpx_filename = '%s.gpx' % name
            track_path = path.join(output_dir, gpx_filename)
            if overwrite or not path.exists(track_path):
                with open(track_path, 'w') as track_file:
                    track_file.write(gpxpy.gpx.GPX(tracks=[t]).to_xml())
                with open(path.join(output_dir, '%s.json' % name), 'w') as meta_file:
                    meta_file.write(json.dumps({
                            'name': t.name,
                            'time': t.get_time_bounds(),
                            'duration': t.get_duration(),
                            'distance': t.length_2d(),
                        }, cls=DateTimeJSONEncoder, indent=True))

                    n_written = n_written + 1

        n_processed = n_processed + 1

    return (n_processed, n_written)

class DateTimeJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return time.mktime(obj.timetuple())
        else:
            return super(DateTimeJSONEncoder, self).default(obj)

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
