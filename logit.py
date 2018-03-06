import time
import csv


class LogIt:

    def __init__(self, user_agent_filter='Googlebot', ip_filter=None):
        self.connection = None
        self.user_agent_filter = user_agent_filter
        self.ip_filter = ip_filter
        self.results = []

    def __check_membership(self, item):
        for i in self.ip_filter:
            if item.startswith(i):
                return True

    def __filter(self, item):
        if not self.ip_filter:
            if self.user_agent_filter in item:
                return True
        else:
            if self.user_agent_filter and self.__check_membership(item):
                return True

    def __date_clean(self, dirty_date):
        date_tuple = time.strptime(dirty_date, "%d/%b/%Y")
        return '{}-{}-{}'.format(date_tuple.tm_year, date_tuple.tm_mon, date_tuple.tm_mday)

    def __parse_date_time(self, item):
        time_split = item.split(':')
        return self.__date_clean(time_split[0]), ':'.join(time_split[1:])

    def parse_log_file(self, file):
        file = open(file)
        filtered = list(filter(self.__filter, file.readlines()))
        filtered = [line.split() for line in filtered]
        for line in filtered:
            parsed = dict()
            parsed['ip'] = line[0]
            parsed['date'], parsed['time'] = self.__parse_date_time(line[3].lstrip('['))
            parsed['url'] = line[6]
            parsed['status'] = line[8]
            parsed['request_size'] = line[9]
            parsed['user_agent'] = ' '.join(line[11:])
            self.results.append(parsed)

    def results_to_csv(self, output_file):
        headers = self.results[0].keys()
        with open(output_file, 'w') as csvfile:
            writer = csv.DictWriter(csvfile, headers)
            writer.writeheader()
            writer.writerows(self.results)

    def clear_results(self):
        self.results = []
