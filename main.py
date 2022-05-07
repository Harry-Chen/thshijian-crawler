#!/usr/bin/env python3

import os
import requests
import json
import csv
from tqdm import tqdm
from multiprocessing import Pool


COOKIE_FILE = 'cookies.txt'
session = requests.Session()
if os.path.isfile(COOKIE_FILE):
    with open(COOKIE_FILE) as f:
        for f in [c.strip() for c in f.read().split(';')]:
            k, v = f.split('=')
            session.cookies[k] = v
else:
    print(f'Error: {COOKIE_FILE} not found')
    exit(1)


def process_project(rp):
        project_id = rp['XMID']

        project = {
            'id': project_id,
            'name': rp['XMMC'],
            'requirement_number': int(rp['XQRS']),
            'base': rp['JDMC'],
            'department_level': rp['SFXJJD'] == '是',
            'province_id': rp['SSM'],
            'province_name': rp['SSMC']
        }

        r = session.post(f"http://thshijian.tsinghua.edu.cn/b/xs/xmsq/queryDepCount/{project_id}")
        assert(r.status_code == 200)
        app_dep_r = json.loads(r.content)['object']
        assert(len(app_dep_r) == 1)
        project['1st_applied_dep'] = app_dep_r[0]['DWJC']

        applied_num = [0] * 4
        applied_num[0] = app_dep_r[0]['COUNT']

        # applied_departments = {}
        # for r in app_dep_r:
        #     applied_departments[r['DWJC']] = r['COUNT']
        # project['applied_departments'] = applied_departments

        r = session.post(f"http://thshijian.tsinghua.edu.cn/b/xs/xmsq/queryApplyCounts/{project_id}")
        assert(r.status_code == 200)
        for r in json.loads(r.content)['object']:
            applied_num[int(r['ZYXH']) - 1] = r['COUNT']
        
        for i, n in enumerate(applied_num):
            project[f'applied_{i+1}'] = n

        return project


if __name__ == '__main__':

    r = session.post("http://thshijian.tsinghua.edu.cn/b/xs/xmsq/allData?pageNum=1&param=sq", data="pageNum=1&xmmc=&jdmc=&ssm=&xqrs=&includeQxkx=true&dwssm=")
    assert(r.status_code == 200)
    raw_projects = json.loads(r.content)['object']

    print(f'Got {len(raw_projects)} projects in total')

    projects = [p for p in tqdm(Pool(8).imap_unordered(process_project, raw_projects), total=len(raw_projects))]

    with open('result.json', 'w') as f:
        json.dump(projects, f, indent=4, ensure_ascii=False)
    
    with open('result.csv', 'w') as f:
        fieldnames = projects[0].keys()
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(projects)
