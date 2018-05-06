# -*- coding: utf-8 -*-
# project = https://github.com/Xyntax/FileSensor
# author = i@cdxy.me

import os
import hashlib
import random
import time
from urllib.parse import urlparse
from .cmdparse import get_arguments
from .data import spider_data, dict_data, paths, conf


def init_options():
    set_path()

    args = get_arguments()
    spider_data.start_urls = args.get('URL')
    spider_data.custom_404_regex = args.get('--404')
    spider_data.found = []
    spider_data.crawled = []
    conf.save_results = args.get('-o')

    load_dict_suffix()
    load_dict_filename()


def set_path():
    paths.root_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    paths.dict_path = os.path.join(paths.root_path, 'dict')
    paths.default_suffix_dict = os.path.join(paths.dict_path, 'suffix.txt')
    paths.default_filename_dict = os.path.join(paths.dict_path, 'filename.txt')
    paths.output_path = os.path.join(paths.root_path, 'output')

    if not all(os.path.exists(p) for p in paths.values()):
        exit('[CRITICAL]Some folders or files are missing, '
             'please download the project in https://github.com/Xyntax/FileSensor/')


def load_dict_suffix():
    with open(paths.default_suffix_dict) as f:
        dict_data.url_suffix = set(f.read().split('\n')) - {'', '#'}

def load_dict_filename():
    with open(paths.default_filename_dict) as f:
        dict_data.url_filename = set(f.read().split('\n')) - {'', '#'}

def gen_urls(base_url):
    def _split_filename(filename):

        full_filename = filename.rstrip('.')
        extension = full_filename.split('.')[-1]
        name = '.'.join(full_filename.split('.')[:-1])

        return name, extension

    url = base_url.split('?')[0].rstrip('/')
    if not urlparse(url).path:
        return []

    path = '/'.join(url.split('/')[:-1])
    filename = url.split('/')[-1]

    # Check if target CMS uses route instead of static file
    isfile = True if '.' in filename else False

    if isfile:
        name, extension = _split_filename(filename)

    final_urls = []
    for each in dict_data.url_suffix:
        new_filename = path + '/' + each.replace('{FULL}', filename)
        if isfile:
            new_filename = new_filename.replace('{NAME}', name).replace('{EXT}', extension)
        else:
            if '{NAME}' in each or '{EXT}' in each:
                continue
        final_urls.append(new_filename.replace('..', '.'))

    return final_urls
def gen_urls_filename(base_url):

    def _split_filename(filename):

        full_filename = filename.rstrip('.')
        extension = full_filename.split('.')[-1]
        name = '.'.join(full_filename.split('.')[:-1])

        return name, extension
    # print("1234")
    url = base_url.split('?')[0].rstrip('/')
    # print("123")
    up = urlparse(base_url)
    path = up.path
    if path:
    	path =  path[:path.rfind("/")+1]
    else:
    	path = "/"
    # print("123")
    # if not urlparse(url).path:
    #     return []

    # path = up.path
    # print(path)
    filename = url.split('/')[-1]

    isfile = True if '.' in filename else False

    if isfile:
        name, extension = _split_filename(filename)

    final_urls = []
    # print("123")

    for each in dict_data.url_filename:
        # print(up)
        new_filename = up.scheme + "://" +up.netloc + path + each
        # print("new_filename")
        # if isfile:
        #     new_filename = new_filename.replace('{NAME}', name).replace('{EXT}', extension)
        # else:
        #     if '{NAME}' in each or '{EXT}' in each:
        #         coninue
        final_urls.append(new_filename.replace('..', '.'))
    print(final_urls)

    return final_urls

def final_message():
    print('-' * 10)
    print('Crawled Page: %d' % len(spider_data.crawled))
    print('Sensitive File Found: %d' % len(spider_data.found))
    for each in spider_data.found:
        print(each)

    save_results()


def random_string():
    return hashlib.md5(str(random.uniform(1, 10)).encode('utf-8')).hexdigest()


def save_results():
    if not conf.save_results:
        return

    site = urlparse(spider_data.start_urls).netloc
    filepath = site if site else spider_data.start_urls.replace('/', '')
    filepath += time.strftime('-%Y%m%d-%H%M%S', time.localtime(time.time()))
    filepath = os.path.join(paths.output_path, filepath)

    try:
        with open(filepath, 'w') as f:
            f.write('\n'.join(spider_data.found))
    except Exception as e:
        exit(e)

    print('\nResults saved in %s' % filepath)
