"""Extract the latitude and longitude coordinates for ZCTA."""

import csv
import os.path
import unittest

_ZCTA_PREFIX = 'GEOID'
"""String prefix for the column containing the ZCTA."""

_LATITUDE_PREFIX = 'INTPTLAT'
"""String prefix for the column containing the latitude."""

_LONGITUDE_PREFIX = 'INTPTLONG'
"""String prefix for the column containing the longitude."""

def _is_coordinate(value):
    """Return True if the string value contains a coordinate."""
    if len(value) <= 0:
        return False
    if value.startswith(('+', '-')):
        value = value[1:]
    count = value.count('.')
    if count <= 0:
        return value.isdigit()
    if count == 1:
        return value.replace('.', '').isdigit()
    return False

def _extract(path, delimiter='\t'):
    """Return a list of string ZCTA, latitude, and longitude tuples.

    Args:
        path: String path to the raw, decompressed U.S. Census gazetteer file.
        delimiter: Optional string delimiter used in the U.S. Census gazetteer
            file. Defaults to tab.
    Returns:
        List of string ZCTA, its string latitude, and its string longitude
        tuples.
    """
    if not isinstance(delimiter, str):
        raise TypeError('delimiter must be an 1 character string.')
    if len(delimiter) != 1:
        raise ValueError('delimiter must be an 1 character string.')

    result = []
    zcta_name = None
    latitude_name = None
    longitude_name = None
    with open(path, encoding='utf-8', newline='') as f:
        reader = csv.DictReader(f, delimiter=delimiter)
        # Workaround the trailing spaces in the gazetteer file
        # Look for the column names programmatically
        for name in reader.fieldnames:
            if name.startswith(_ZCTA_PREFIX):
                zcta_name = name
            elif name.startswith(_LATITUDE_PREFIX):
                latitude_name = name
            elif name.startswith(_LONGITUDE_PREFIX):
                longitude_name = name
        if (isinstance(zcta_name, str) and
            isinstance(latitude_name, str) and
            isinstance(longitude_name, str)):
            for row in reader:
                zcta = row.get(zcta_name)
                if not isinstance(zcta, str):
                    continue
                zcta = zcta.strip()
                if not zcta.isdigit():
                    continue

                latitude = row.get(latitude_name)
                if not isinstance(latitude, str):
                    continue
                latitude = latitude.strip()
                if not _is_coordinate(latitude):
                    continue
                latitude = latitude.lstrip('+')

                longitude = row.get(longitude_name)
                if not isinstance(longitude, str):
                    continue
                longitude = longitude.strip()
                if not _is_coordinate(longitude):
                    continue
                longitude = longitude.lstrip('+')

                result.append((zcta, latitude, longitude))
    return result


class _UnitTest(unittest.TestCase):
    def test_is_coordinate(self):
        """Test if a string contains a coordinate."""
        for value in ['', '+', '-', 'foo', 'bar', 'foobar',
                      '+foo', '+bar', '+foobar', '-foo', '-bar', '-foobar',
                      '2+2', '4-2', '42+', '42-',
                      '4.2.0', '+4.2.0', '-4.2.0']:
            self.assertFalse(_is_coordinate(value))
        for value in ['42', '42.', '42.0', '.42', '0.42',
                      '37', '122', '37.', '122.',
                      '37.4', '122.1', '37.386051', '122.083851']:
            self.assertTrue(_is_coordinate(value))
            for prefix in ['+', '-']:
                self.assertTrue(_is_coordinate(prefix + value))
                self.assertFalse(_is_coordinate(prefix + prefix + value))
                self.assertFalse(_is_coordinate(value + prefix))

    def test_extract(self):
        """Test the guard clauses in _extract()."""
        for value in [None, 42, []]:
            self.assertRaises(TypeError, _extract, 'foobar', value)
        for value in ['', 'foo', 'bar', 'foobar']:
            self.assertRaises(ValueError, _extract, 'foobar', value)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        '-c', '--csv', action='store_true',
        help='output the ZIP codes as csv')
    parser.add_argument(
        '-d', '--delimiter', default='\t',
        help='delimiter separating the columns (default: tab)')
    parser.add_argument(
        'path', nargs='?', default='',
        help='path to the raw, decompressed U.S. Census gazetteer file')
    args = parser.parse_args()

    if os.path.isfile(args.path):
        areas = _extract(args.path, args.delimiter)
        areas.sort()
        if args.csv:
            # Print the CSV header line
            print(args.delimiter.join(
                [_ZCTA_PREFIX, _LATITUDE_PREFIX, _LONGITUDE_PREFIX]))
        for zcta, latitude, longitude in areas:
            if args.csv:
                print(args.delimiter.join([zcta, latitude, longitude]))
            else:
                print('  {{"zip": "{0}", "lat": {1}, "lon": {2}}},'.format(
                    zcta, latitude, longitude))
    else:
        suite = unittest.defaultTestLoader.loadTestsFromTestCase(_UnitTest)
        unittest.TextTestRunner(verbosity=2).run(suite)
