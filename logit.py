import multiprocessing
from multiprocessing import Pool
import time
import csv
import datetime

# Multiprocessing example

class logger_multi(object):

    def __init__(self,user_agent,ips=None):
        self.user_agent = user_agent # List of user agents we want to validate
        self.ips = ips # IP's in list
        self.results = []

    def __date_clean(self, dirty_date):
        date_tuple = time.strptime(dirty_date, "%d/%b/%Y")
        return '{}-{}-{}'.format(date_tuple.tm_year, date_tuple.tm_mon, date_tuple.tm_mday)

    def __parse_date_time(self, item):
        time_split = item.split(':')
        return self.__date_clean(time_split[0]), ':'.join(time_split[1:])

    def verify(self, UA, IP):
        for user in self.user_agent:
            if user in UA:
                for ip in self.ips:
                    if IP.startswith(ip):
                        return True
                    else:
                        continue
        return False

    def open_file(self,filename):
        file = open(filename,encoding="utf-8")
        return file

    def chunks(self, l, n):
        for i in range(0, len(l), n):
            yield l[i:i + n]

    def parse_chunk(self,data):
        results = []
        for line in data:
            try:
                parsed = dict()
                parsed['ip'] = line[0]
                parsed['date'], parsed['time'] = self.__parse_date_time(line[3].lstrip('['))
                parsed['url'] = line[6]
                parsed['status'] = line[8]
                parsed['request_size'] = line[9]
                parsed['user_agent'] = ' '.join(line[11:])
                parsed['verify'] = str(self.verify(parsed['user_agent'],parsed['ip']))
                results.append(parsed)
            except Exception as e:
                print(e)
        return results

    def run_process(self, file):
        file = self.open_file(file).readlines()
        listify = [line.split() for line in file]

        data = self.chunks(listify, int(len(listify) / (multiprocessing.cpu_count() - 2)))
        p = Pool(processes=multiprocessing.cpu_count() - 2)
        results = [p.apply_async(self.parse_chunk, args=(list(x),)) for x in data]

        # wait for results
        results = [item.get() for item in results]
        self.results = sum(results, [])

    def results_to_csv(self, output_file):
        headers = self.results[0].keys()
        with open(output_file, 'w', newline='\n') as csvfile:
            writer = csv.DictWriter(csvfile, headers)
            writer.writeheader()
            writer.writerows(self.results)

    def clear_results(self):
        self.results = []

if __name__ == '__main__':
    c = logger_multi(user_agent=['Googlebot','Mediapartners-Google'],
                     ips=['64.233', '66.102', '66.249', '72.14', '74.125', '209.85', '216.239', '66.184'])
    c.run_process('log-new.txt')
    c.results_to_csv('example-multi.csv')