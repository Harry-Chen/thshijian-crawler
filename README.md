# thshijian-crawler

Crawl data from <https://thshijian.tsinghua.edu.cn>.

## Usage:

1. Install requirements: `python3 -m pip install -r requirements.txt`
2. Put your cookies into `cookies.txt`: e.g. `serverid=1425456; JSESSIONID=xxxx.yjsshsj1` (can be obtained from browser developer tools)
3. Run `python3 ./main.py`
4. Results are stored in `result.csv` and `result.json`
