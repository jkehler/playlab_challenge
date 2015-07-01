import csv
import re
from collections import Counter
import sys
import os


endpoints = [
    {
        'method': 'GET',
        'path': '/api/users/{user_id}/count_pending_messages',
        'records': []
    },
    {
        'method': 'GET',
        'path': '/api/users/{user_id}/get_messages',
        'records': []
    },
    {
        'method': 'GET',
        'path': '/api/users/{user_id}/get_friends_progress',
        'records': []
    },
    {
        'method': 'GET',
        'path': '/api/users/{user_id}/get_friends_score',
        'records': []
    },
    {
        'method': 'POST',
        'path': '/api/users/{user_id}',
        'records': []
    },
    {
        'method': 'GET',
        'path': '/api/users/{user_id}',
        'records': []
    }
]


class LogRecord(object):
    """Stores formatted values for a single line from the log file

    Unwanted string characters such as 'ms' and prefixes are removed
    from the values.

    Python special attributes __lt__, __gt__, __eq__ are implemented
    to enable sorting of LogRecords by response time.

    :param row: A list of columns parsed from the log file
    """

    def __init__(self, row):
        self.method = row[3][7:]
        self.path = row[4][5:]
        self.dyno = row[7][5:]
        self.connect = int(re.sub('ms', '', row[8][8:]))
        self.service = int(re.sub('ms', '', row[9][8:]))
        self.response_time = self.service + self.connect

    def __lt__(self, record):
        if record.response_time < self.response_time:
            return True
        return False

    def __gt__(self, record):
        if record.response_time > self.response_time:
            return True
        return False

    def __eq__(self, record):
        if record.response_time == self.response_time:
            return True
        return False


def median_response(records):
    """Returns the median response time from a list of records.

    :param records: A list of :class:`LogRecord`
    :rtype: float rounded to a single decimal place
    """
    length = len(records)
    if length == 0:
        return float(0.0)

    records = sorted(records)

    # Check if divisible by 2
    if not length % 2:
        return round(float(
            records[int(length / 2)].response_time +
            records[int(length / 2 - 1)].response_time
        ) / 2.0, 1)

    return round(float(records[int(length / 2)].response_time), 1)


def mean_response(records):
    """Returns the mean response time from a list of records.

    :param records: A list of :class:`LogRecord`
    :rtype: float rounded to a single decimal place
    """
    if len(records) == 0:
        return float(0.0)
    return round(
        float(sum([r.response_time for r in records])) / float(len(records)),
        1
    )


def mode_response(records):
    """Returns the mode response time from a list of records.

    :param records: A list of :class:`LogRecord`
    :rtype: int
    """
    if len(records) == 0:
        return 0
    v, count = Counter([r.response_time for r in records]).most_common(1)[0]
    return v


def mode_dyno(records):
    """Returns the mode dyno from a list of records.

    :param records: A list of :class:`LogRecord`
    :rtype: str
    """
    if len(records) == 0:
        return None
    v, count = Counter([r.dyno for r in records]).most_common(1)[0]
    return v


def parse_log_file(file_name):
    """Parses the log file using csv reader

    :param file_name: The file name of the log file to parse
    :return: A list of :class:`LogRecord` objects
    """
    assert os.path.isfile(file_name), 'Argument is not a file.'
    with open(file_name, 'r') as f:
        try:
            # Parse the records. Omit any paths that do not begin with
            # path=/api/users to save memory
            return [
                LogRecord(r)
                for r in csv.reader(f, delimiter=' ')
                if r[4].startswith('path=/api/users/')
            ]
        except Exception as e:
            print('Exception occured while parsing the log file.')
            print(e)
            sys.exit(1)


def main(args):
    assert len(args) == 2, 'Log filename not provided.'

    # Generate the regex match objects for the endpoints
    # Replaces {user_id} with regex [0-9]+ and adds ^ and $ to
    # beginning and end of path.
    for endpoint in endpoints:
        endpoint['path_rx'] = re.compile(
            '^' + endpoint['path'].format(user_id='[0-9]+') + '$'
        )

    for record in parse_log_file(file_name=args[1]):
        for endpoint in endpoints:
            if endpoint['method'] == record.method \
                    and endpoint['path_rx'].match(record.path):
                # Record matched this endpoint. Add it to the records list
                endpoint['records'].append(record)
                # If there is a match break to save wasted cycles since a
                # record should not match multiple endpoints
                break

    for endpoint in endpoints:

        records = endpoint['records']

        print('Endpoint:          {method} {path}'.format(
            method=endpoint['method'], path=endpoint['path'])
        )
        print('Called:            {} times'.format(len(records)))
        print('Mean response:     {} ms'.format(mean_response(records)))
        print('Median Response:   {} ms'.format(median_response(records)))
        print('Mode response:     {} ms'.format(mode_response(records)))
        print('Most active Dyno:  {}'.format(mode_dyno(records)))
        print('--------------------------------------------------------------')


if __name__ == '__main__':
    main(sys.argv)
