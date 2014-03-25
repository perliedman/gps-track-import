#!/usr/bin/python

import gpxpy
import gpxpy.gpx
import subprocess
from os import path
import json
import datetime
import time
from glob import glob
import re
from nominatim.reversegeocoder import ReverseGeocoder
import math

def import_from_device(device_name, output_path, gpsbabel_path='gpsbabel'):
    retcode = subprocess.call([
        gpsbabel_path,
        '-t',
        '-i', 'garmin',
        '-f', device_name,
        '-o', 'gpx',
        '-F', output_path])
    return retcode == 0

last_geocode = None

def project(ll):
    d = math.pi / 180
    mx = 1 - 1E-15
    sin = max(min(math.sin(ll[0] * d), mx), -mx);

    return (ll[1] * d,
            math.log((1 + sin) / (1 - sin)) / 2);

def get_osm_zoom_from_resolution(v):
    """Given a scale (pixels per pseudo-meters), calculate the
    highest zoom level with at least that resolution"""
    return int(math.log((v)) / math.log(2))

def get_osm_zoom_to_fit(ll_bounds, pixels):
    sw = project((ll_bounds.min_latitude, ll_bounds.min_longitude))
    ne = project((ll_bounds.max_latitude, ll_bounds.max_longitude))
    size = max(ne[0] - sw[0], ne[1] - sw[1])
    return get_osm_zoom_from_resolution(pixels / size)

def geocode(t):
    global last_geocode
    # Avoid breaking Nominatim's terms of service (max 1 req/s)
    now = time.time()
    if last_geocode:
        time.sleep(max(0, 1 - (now - last_geocode)))
    try:
        center = t.get_center()
        location = ReverseGeocoder().geocode(center.latitude, center.longitude,
            get_osm_zoom_to_fit(t.get_bounds(), 4))
        last_geocode = time.time()
        parts = location['full_address'].split(',')
        return ', '.join([parts[i].strip() for i in [0, 2] if i < len(parts)])
    except Exception, e:
        print e
        return None

def process_tracks(gpx_path, output_dir, overwrite=False):
    f = open(gpx_path, 'r')
    gpx = gpxpy.parse(f)
    n_processed = 0
    n_written = 0

    for t in gpx.tracks:
        if len(t.segments) > 0 and len(t.segments[0].points) > 0:
            p = t.segments[0].points[0]
            name = '%s-%s' % (p.time.strftime('%Y-%m-%d'), re.sub(r'\W+','-', t.name))
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
                            'location': geocode(t)
                        }, cls=DateTimeJSONEncoder, indent=True))

                    n_written = n_written + 1

        n_processed = n_processed + 1

    return (n_processed, n_written)

def tracks_json(tracks_dir):
    for fn in glob(path.join(tracks_dir, '*.json')):
        with open(fn, 'r') as meta_file:
            try:
                yield((fn, json.loads(meta_file.read())))
            except ValueError:
                print 'Invalid json in', fn

def tracks_gpx(tracks_dir):
    for fn in glob(path.join(tracks_dir, '*.gpx')):
        with open(fn, 'r') as track:
            yield((fn, gpxpy.parse(track)))

def generate_index(tracks_dir):
    tracks = [metadata for (fn, metadata) in tracks_json(tracks_dir)]

    with open(path.join(tracks_dir, 'index.json'), 'w') as index_file:
        index_file.write(json.dumps(tracks))

    return len(tracks)

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
    parser.add_argument('--re-index', action='store_true', default=False)
    parser.add_argument('files', nargs='*')

    args = parser.parse_args(sys.argv[1:len(sys.argv)])

    if not args.re_index:
        if args.from_device and len(args.files) == 0:
            f, gpx_path = tempfile.mkstemp()
            if not import_from_device(args.from_device, gpx_path):
                print "Import from device failed"
                sys.exit(1)
            files = [gpx_path]
        else:
            files = args.files

        tracks_dir = path.expanduser('~/.gps-log/tracks')

        c = 0
        for f in files:
            process_tracks(f, tracks_dir, args.overwrite)
            if c % 10 == 0:
                sys.stdout.write('.')
                sys.stdout.flush()
            c = c + 1
        generate_index(tracks_dir)
    else:
        tracks_dir = path.expanduser('~/.gps-log/tracks')
        generate_index(tracks_dir)

    sys.stdout.write('\n')
