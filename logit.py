from multiprocessing import cpu_count, Pool
import time
import csv


class LogitMultiprocessing(object):

    def __init__(self, user_agents, ips=None, processes=None):
        self.user_agents = user_agents  # List of user agents we want to validate
        self.ips = ips  # IP's in list
        self.results = []
        self.processes = cpu_count() if not processes else processes

    def __date_clean(self, dirty_date):
        date_tuple = time.strptime(dirty_date, "%d/%b/%Y")
        return '{}-{}-{}'.format(date_tuple.tm_year, date_tuple.tm_mon, date_tuple.tm_mday)

    def __parse_date_time(self, item):
        time_split = item.split(':')
        return self.__date_clean(time_split[0]), ':'.join(time_split[1:])

    def verify(self, ua, current_ip):
        if any(i in ua for i in self.user_agents):
            for ip in self.ips:
                if current_ip.startswith(ip):
                    return True
        return False

    def open_file(self, filename):
        file = open(filename, encoding="utf-8")
        return file

    def chunks(self, l, n):
        for i in range(0, len(l), n):
            yield l[i:i + n]

    def parse_chunk(self, data):
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
                parsed['verified'] = str(self.verify(parsed['user_agent'], parsed['ip']))
                results.append(parsed)
            except Exception as e:
                print(e)
        return results

    def run_process(self, file):
        listify = [line.split() for line in self.open_file(file).readlines()]

        data = self.chunks(listify, int(len(listify) / self.processes))
        p = Pool(processes=self.processes)
        results = [p.apply_async(self.parse_chunk, args=(list(x),)) for x in data]

        # wait for results
        results = [item.get() for item in results]
        self.results = [item for sublist in results for item in sublist]

    def results_to_csv(self, output_file):
        headers = self.results[0].keys()
        with open(output_file, 'w', newline='\n') as csvfile:
            writer = csv.DictWriter(csvfile, headers)
            writer.writeheader()
            writer.writerows(self.results)

    def clear_results(self):
        self.results = []


if __name__ == '__main__':
    c = LogitMultiprocessing(user_agents=['Googlebot','Mediapartners-Google'],
                     ips=['64.233', '66.102', '66.249', '72.14', '74.125', '209.85', '216.239', '66.184'])
    c.run_process('logs.demo')
    c.results_to_csv('example-multi.csv')