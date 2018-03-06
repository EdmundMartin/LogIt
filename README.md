# LogIt
Fast and simple SEO log file parser written in Python

## Example Usage
```python3
c = LogIt(ip_filter=['64.233', '66.102', '66.249', '72.14', '74.125', '209.85', '216.239', '66.184'])
c.parse_log_file('logs.demo')
c.results_to_csv('example.csv')
c.clear_results()
```
LogIt contains only one Python class, taking two keyword arguments. user_agent_filter - filters results down to the user agent based in and this is 'Googlebot' as default. ip_filter - takes an iterable of verified IP's whether they be Google, Bing or Yandex.

Log files can be passed to the parse_log_file method which will parse the file and save the results in memory. This can be called on multiple files or the results can be then easily put into a some sort of datastore. Results are accessible using .results on your initilaized class and our a list of dictionary objects. Additionally, there is a results_to_csv method which dumps the results into a CSV file.

The clear_results method simply empties the list of collected results, freeing up memory should you have additional files to parse.
