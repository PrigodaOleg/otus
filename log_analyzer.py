#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import os
import re
import datetime
import gzip
import sys


# log_format ui_short '$remote_addr  $remote_user $http_x_real_ip [$time_local] "$request" '
#                     '$status $body_bytes_sent "$http_referer" '
#                     '"$http_user_agent" "$http_x_forwarded_for" "$http_X_REQUEST_ID" "$http_X_RB_USER" '
#                     '$request_time';

config = {
    "REPORT_SIZE": 1000,
    "REPORT_DIR": "C:\\Users\\Oleg.OLEGNOTEBOOK\\Downloads\\01_advanced_basics\\01_advanced_basics\\homework",
    # "REPORT_DIR": "./reports",
    # "LOG_DIR": "./log"
    "LOG_DIR": "C:\\Users\\Oleg.OLEGNOTEBOOK\\Downloads\\01_advanced_basics\\01_advanced_basics\\homework"

}


def get_actual_log_file(path):
    candidate_file_name = None
    candidate_file_date = None
    if os.path.isdir(path):
        re_log = re.compile(r'nginx-access-ui\.log-(\d+).*')
        for dirpath, dirnames, filenames in os.walk(path):
            for file in filenames:
                match = re_log.match(file)
                if match:
                    log_date = datetime.datetime.strptime(match.group(1), "%Y%m%d").date()
                    if candidate_file_name:
                        if log_date >= candidate_file_date:
                            candidate_file_name = file
                            candidate_file_date = log_date
                    else:
                        candidate_file_name = file
                        candidate_file_date = log_date
            break
        candidate_file_name = os.path.join(path, candidate_file_name) if candidate_file_name else None
    else:
        raise AttributeError(f"Path {path} is not a directory, please specify log directory")
    return candidate_file_name, candidate_file_date


def parse_lines(file_name):
    # Try to open it according to its format
    logfile = gzip.open(file_name, 'rt') if file_name.endswith('.gz') else open(file_name, 'r')
    skipped_lines = 0
    total_lines = 0
    try:
        re_fields = re.compile(r'(\d+\.\d+\.\d+\.\d+) '                                 # $remote_addr
                               r'([\da-f]+|-)\s{1,2}'                                   # $remote_user
                               r'(.|-) '                                                # $http_x_real_ip
                               r'(\[\d+\/\w+\/\d+:\d+:\d+:\d+ \+\d+]) '                 # [$time_local]
                               r'"((?:(?:GET|POST|HEAD|PUT|OPTIONS) .+)|0)" '           # $request
                               r'(\d+) '                                                # $status
                               r'(\d+) '                                                # $body_bytes_sent
                               r'"(.*)" '                                               # $http_referer
                               r'"(.*)" '                                               # $http_user_agent
                               r'"(.*)" '                                               # $http_x_forwarded_for
                               r'"((?:\d+-\d+-\d+-\d+|.+))" '                           # $http_X_REQUEST_ID
                               r'"(.+)" '                                               # $http_X_RB_USER
                               r'(\d+\.\d+)'                                            # $request_time
                               )
        c = 200000
        for line in logfile:
            total_lines += 1
            match = re_fields.match(line)
            if match:
                yield match.groups()
            else:
                logging.info(f'Line skipped: {line}')
                skipped_lines += 1
            c -= 1
            if not c:
                break

    finally:
        logfile.close()
        errors_threshold = 50
        error_lines_percentage = round(skipped_lines / total_lines, 3) * 100
        if error_lines_percentage > errors_threshold:
            logging.error(f'Too many errors occurred while parsing: {error_lines_percentage}%')
            raise RuntimeError(f'Too many error lines in file {file_name}')


def main():
    # Get actual log file
    logfile_name, logfile_date = get_actual_log_file(config['LOG_DIR'])
    if logfile_name is None:
        logging.info('Log file has not found.')
    else:
        if os.path.isfile(os.path.join(config['REPORT_DIR'], f'{logfile_name}.log')):
            logging.info('Log file already exists, skip this time.')
            return 1
    statistics = {}
    total_request_time = 0
    total_count = 0
    for _, _, _, _, request, _, _, _, _, _, _, _, request_time in parse_lines(logfile_name):
        request_time = float(request_time)
        id = request.split()
        id = id[1] if len(id) > 1 else id[0]
        if id not in statistics:
            statistics[id] = {'count': 1,
                              'time_sum': request_time,
                              'time_avg': request_time,
                              'time_max': request_time,
                              'time_med': request_time}
        else:
            statistics[id]['time_sum'] = round(statistics[id]['time_sum'] + request_time, 3)
            statistics[id]['time_avg'] = round((statistics[id]['time_avg'] *
                                                statistics[id]['count'] + request_time) /\
                                               (statistics[id]['count'] + 1), 3)
            statistics[id]['time_max'] = statistics[id]['time_max'] \
                if statistics[id]['time_max'] > request_time \
                else request_time
            statistics[id]['count'] += 1
        total_request_time += request_time
        total_count += 1
    report = []
    for address in statistics:
        statistics[address]['count_perc'] = round(statistics[address]['count'] / total_count * 100, 3)
        statistics[address]['time_perc'] = round(statistics[address]['time_sum'] / total_request_time * 100, 3)
        statistics[address]['url'] = address
        report.append(statistics[address])

    # Render report
    report_template_filename = f"{config['LOG_DIR']}/report.html"
    report_filename = f"{os.path.dirname(logfile_name)}/report-{logfile_date}.html"
    with open(report_template_filename, 'r') as template:
        with open(report_filename, 'w') as report_file:
            report_file.write(template.read().replace('$table_json', str(report)))


if __name__ == "__main__":
    sys,exit(main())
