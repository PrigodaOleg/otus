#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import os
import re
import datetime
import tarfile


LOG_DIR = 'C:\\Users\\Oleg.OLEGNOTEBOOK\\Downloads\\01_advanced_basics\\01_advanced_basics\\homework'


# log_format ui_short '$remote_addr  $remote_user $http_x_real_ip [$time_local] "$request" '
#                     '$status $body_bytes_sent "$http_referer" '
#                     '"$http_user_agent" "$http_x_forwarded_for" "$http_X_REQUEST_ID" "$http_X_RB_USER" '
#                     '$request_time';

config = {
    "REPORT_SIZE": 1000,
    "REPORT_DIR": "./reports",
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
    else:
        raise AttributeError(f"Path {path} is not a directory, please specify log directory")
    return os.path.join(path, candidate_file_name)


def main():
    # Get actual log file
    logfile = get_actual_log_file(config['LOG_DIR'])
    print(logfile)


if __name__ == "__main__":
    main()
