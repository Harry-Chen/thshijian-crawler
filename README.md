# thshijian-crawler

Crawl structured data from <https://thshijian.tsinghua.edu.cn>. Use at your own risk.

## Usage

1. Install dependencies: `python3 -m pip install -r requirements.txt`
2. Put your cookies into `cookies.txt`: e.g. `serverid=1425456; JSESSIONID=xxxx.yjsshsj1` (can be obtained from browser developer tools)
3. Run `python3 ./main.py`
4. Results are stored in `result.csv` and `result.json`

## Example

An object in JSON looks like:

```json5
{
    "id": "[REDACTED]",
    "name": "[REDACTED]",
    "requirement_number": 2, // 需求人数
    "base": "[REDACTED]", // 基地名称
    "department_level": true, // true: 系级基地, false: 校级基地
    "province_id": "11",
    "province_name": "北京市",
    "1st_applied_dep": "开放全校可选", // 一志愿人数最多的院系组合
    "applied_1": 2, // 一志愿申请人数
    "applied_2": 1, // 二志愿申请人数
    "applied_3": 1, // 三志愿申请人数
    "applied_4": 0  // 四志愿申请人数
}
```

Columns in CSV are the same as fields in the JSON object above.

## Note

This crawler currently does not support any project with multiple competing department groups.
