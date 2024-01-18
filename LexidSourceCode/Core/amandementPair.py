import json
import math
import re
from random import random

import pandas
from json import JSONEncoder

from SPARQLWrapper import SPARQLWrapper, JSON

pandas.set_option('display.max_rows', 200)
pandas.set_option('display.max_colwidth', 300)
pandas.set_option('display.width', None)

amendmentPair = pandas.read_csv('amendmentPair.csv').drop_duplicates()
print(len(amendmentPair))

content_prev = amendmentPair[['change', 'path']].drop_duplicates()

print(content_prev[content_prev['change']=='Perpres_2018_82'])
print(len(content_prev))

def get_body_parse(prev_ids, prev, parts):
    prevType = re.search('(?i)chapter|part|paragraph|article|change', prev).group(0).lower() + 's'
    nexts = {'chapters': 'parts', 'parts': 'paragraphs', 'paragraphs': 'articles'}
    res = []
    if prevType == 'changes':
        for next_chap in parts.keys():
            res.append({'change': prev_ids, 'parts': next_chap, 'partOf': prev})
            print(prev_ids, next_chap, prev)
            currentType = re.search('(?i)chapter|part|paragraph|article|change', next_chap).group(0).lower() + 's'
            if currentType != 'articles':
                res += get_body_parse(prev_ids, next_chap, parts[next_chap])
    elif not (prevType == 'articles') and len(parts[nexts[prevType]]) != 0:
        for next_chap in parts[nexts[prevType]].keys():
            res.append({'change': prev_ids, 'parts': next_chap, 'partOf': prev})
            print(prev_ids, next_chap, prev)
            res += get_body_parse(prev_ids, next_chap, parts[nexts[prevType]][next_chap])
    elif not (prevType == 'articles'):
        for next_chap in parts['articles'].keys():
            res.append({'change': prev_ids, 'parts': next_chap, 'partOf': prev})
            print(prev_ids, next_chap, prev)
            res += get_body_parse(prev_ids, next_chap, parts['articles'][next_chap])
    return res


file_num = 0
res_parse = []
for prevs in content_prev.iterrows():
    prev_id = prevs[1]['change']
    prev_path = prevs[1]['path']
    print(prevs[1]['change'], prev_path)
    file = json.load(open(prev_path, 'r'))
    contents = file['body']
    if len(contents) == 0:
        file_num += 1
        continue
    for content in contents.keys():
        res_parse += [{'change': prev_id, 'parts': content}]
        res_parse += get_body_parse(prev_id, content, contents[content])
    print(file_num, len(content_prev))
    file_num += 1
    # if prevs[1]zl21
    # if prev_id == 'Perpres_2018_82':
    #     print(contents)
    #     break
    # break
res_parse = pandas.DataFrame(res_parse)
res_parse = res_parse[~(res_parse['parts'].str.contains(r'_(\d+|[IVXLCDM]+)$', regex=True) &
                        res_parse['partOf'].str.contains(r'(?i)^change', regex=True))]
existed_content = amendmentPair.merge(res_parse.add_suffix('_existed'), left_on='change', right_on='change_existed')
print(existed_content[existed_content['change']=='Perpres_2018_82'])
existed_content = existed_content[['reg_id', 'parts_existed', 'partOf_existed']].drop_duplicates()
existed_content.to_csv('existedContentAmendment.csv', index=False)
# for ori in rand_ori:
#     print(ori)
#     print(amendmentPair[amendmentPair['change'] == ori].sort_values(['year', 'number']))
#     num += 1
#     if num > 10:
#         break
