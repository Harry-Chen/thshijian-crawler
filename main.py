#!/usr/bin/env python3

import os
import json
import io
import csv
from multiprocessing import Pool
import traceback

import requests
from tqdm import tqdm


COOKIE_FILE = 'cookies.txt'
session = requests.Session()
if os.path.isfile(COOKIE_FILE):
    with open(COOKIE_FILE) as f:
        for f in [c.strip() for c in f.read().split(';')]:
            k, v = f.split('=')
            session.cookies[k.strip()] = v.strip()
else:
    print(f'Error: {COOKIE_FILE} not found')
    exit(1)


def check_response(r: requests.Response, force=True):
    assert (r.status_code == 200)
    r_obj = json.loads(r.content)
    if r_obj['result'] == 'success':
        return r_obj['object']
    else:
        print(f'Request {r.url} failed: {r_obj}')
        if force:
            exit(1)
        else:
            return None


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

    app_dep = check_response(session.post(
        f"http://thshijian.tsinghua.edu.cn/b/xs/xmsq/queryDepCount/{project_id}"
    ))
    assert (len(app_dep) == 1), f"More than one department groups allowed in project {rp}"
    project['1st_applied_dep'] = app_dep[0]['DWJC']

    applied_num = [0] * 4
    applied_num[0] = app_dep[0]['COUNT']

    # applied_departments = {}
    # for r in app_dep_r:
    #     applied_departments[r['DWJC']] = r['COUNT']
    # project['applied_departments'] = applied_departments

    app_level = check_response(session.post(
        f"http://thshijian.tsinghua.edu.cn/b/xs/xmsq/queryApplyCounts/{project_id}"
    ))
    for r in app_level:
        zyxh = r['ZYXH']
        if zyxh is None:
            seq = 0
            print(f'Warning: wrong count for project {project}: {r}, fixing...')
        else:
            seq = int(zyxh) - 1
        applied_num[seq] = r['COUNT']

    for i, n in enumerate(applied_num):
        project[f'applied_{i+1}'] = n

    return project


def try_process_project(rp):
    try:
        return process_project(rp)
    except Exception as e:
        print(f'Error processing {rp}')
        traceback.print_exc()
        

if __name__ == '__main__':

    raw_projects = check_response(session.post(
        "http://thshijian.tsinghua.edu.cn/b/xs/xmsq/allData?pageNum=1&param=sq",
        data="pageNum=1&xmmc=&jdmc=&ssm=&xqrs=&includeQxkx=true&dwssm="))

    print(f'Got {len(raw_projects)} projects in total')

    projects = list(
        tqdm(Pool(8).imap_unordered(try_process_project, raw_projects),
             total=len(raw_projects)))

    with open('result.json', 'w') as f:
        json.dump(projects, f, indent=4, ensure_ascii=False)

    with io.open("result.csv", 'w', encoding='utf-8-sig') as f:
        fieldnames = projects[0].keys()
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(projects)
