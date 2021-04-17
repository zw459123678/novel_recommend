# -*- coding: UTF-8 -*- 
from requests_html import HTMLSession, HTML
from parsel import Selector
import pandas as pd
import time
import sqlite3
import uuid
import os
import json
import re
from urllib.parse import urlparse, parse_qs, parse_qsl
import requests

DATABASE = 'database.db'

def connect_db():
    return sqlite3.connect(DATABASE)

def query_db(query, args=(), one=False):
    db = connect_db()
    cur = db.execute(query, args)
    rv = [dict((cur.description[idx][0], value)
               for idx, value in enumerate(row)) for row in cur.fetchall()]
    return (rv[0] if rv else None) if one else rv

class Crawler():
    def __init__(self, taskid = None, keywords = None, delay = 1):
        self.session = HTMLSession()
        self.keyword_list = keywords
        self.taskid = taskid
        self.base_url = 'http://www.jjwxc.net'
        self.channel_url = '/fenzhan/by/'
        self.novel_url = '/onebook_vip.php'
        self.channel_address_list = []
        self.novel_address_list = []
        self.data_list = []
        self.delay = delay



    def get_keywords(self):
        with open('keywords.txt', 'r', encoding='utf-8-sig') as f:
            keywords = [i.strip() for i in f.readlines() if i.strip()]
        return keywords

    def search_channel_address(self):
        print('>>>>>>>检查是否有频道地址缓存数据')
        if os.path.exists('channel.txt'):
            channel_file = open('channel.txt', 'r')
            channel_data = channel_file.read()
            channel_file.close()
            self.channel_address_list = channel_data.split('\n')
            print(len(self.channel_address_list))
        else:
            print(f'>>>>>>爬取频道地址中')
            url = f'{self.base_url}{self.channel_url}'
            r = self.session.get(url)
            for i in Selector(r.text).css('#box > ul > li > h1 > div.tabbody.more > div[name=half] > a'):
                self.channel_address_list.append(i.attrib['href'])
            print(self.channel_address_list)

            out_file = open('channel.txt', 'w')
            out_file.write('\n'.join(self.channel_address_list))
            out_file.close()
        return self.channel_address_list

    def search_novel_address(self):
        print('>>>>>>>检查是否有小说地址缓存数据')
        if os.path.exists('novel_address.txt'):
            novel_address_file = open('novel_address.txt', 'r')
            novel_address_data = novel_address_file.read()
            novel_address_file.close()
            self.novel_address_list = novel_address_data.split('\n')
            print(len(self.novel_address_list))
        else:
            print(f'>>>>>>爬取小说地址中')
            for url in self.channel_address_list:
                time.sleep(self.delay)
                full_url = f'{self.base_url}{url}'
                print(full_url)
                r = self.session.get(full_url)
                for j in Selector(r.text).css('body > table > tbody > tr > td:nth-child(3) > a'):
                    self.novel_address_list.append(j.attrib['href'])
                # print(self.novel_address_list)
            print(len(self.novel_address_list))

            out_file = open('novel_address.txt', 'w')
            out_file.write('\n'.join(self.novel_address_list))
            out_file.close()
        return self.novel_address_list

    def novel_address(self, channelid, channelstr):
        """
        爬取指定频道的小说地址
        """
        time.sleep(self.delay)
        addresses = []
        full_url = f'{self.base_url}/channeltoplist.php?channelid={channelid}&str={channelstr}'
        print(f'>>>>>>爬取小说地址中: {full_url}')
        r = self.session.get(full_url)
        for j in Selector(r.text).css('body > table > tbody > tr > td:nth-child(3) > a'):
            addresses.append(j.attrib['href'])
        return addresses

    def novel_info(self, addresses, limit = -1):
        """
        爬取指定小说的基本信息
        """
        infos = []
        for address in addresses:
            time.sleep(self.delay)
            url = f'{self.base_url}/{address}'
            print(f'>>>>>>爬取小说基本信息中: {url}')
            r = self.session.get(url)# 解决中文乱码问题
            r.encoding = r.apparent_encoding
            tags = []
            querys = parse_qs(urlparse(url).query)

            novelid = querys['novelid'][0]

            # 标题
            i = Selector(r.text).css('#oneboolt > tbody > tr:nth-child(1) > td > div > span > h1 > span')
            title = i.xpath('./text()').get('').strip()
            print(title)

            # 作者
            i = Selector(r.text).css('#oneboolt > tbody > tr:nth-child(1) > td > div > h2 > a > span')
            author = i.xpath('./text()').get('').strip()

            # 标签
            for i in Selector(r.text).css('body > table:nth-child(23) > tr > td:nth-child(1) > div:nth-child(3) > span > a'):
                tags.append(i.xpath('./text()').get('').strip())
            
            # 文字类型（用作标签）
            i = Selector(r.text).css('body > table:nth-child(23) > tr > td:nth-child(3) > div.righttd > ul > li:nth-child(1) > span:nth-child(2)')
            types = i.xpath('./text()').get('').strip().split('-')
            tags.extend(types)
            print(tags)

            # 按章检索地址
            sections = []
            for i in Selector(r.text).css('#oneboolt > tbody > tr > td:nth-child(2) > span > div:nth-child(1) > a:nth-child(1)'):
                section = {}
                if i.attrib.get('href', None):
                    section = {
                        'title': i.xpath('./text()').get('').strip(),
                        'url': i.attrib.get('href', None),
                        'vip': False
                    }
                elif i.attrib.get('rel', None):
                    section = {
                        'title': i.xpath('./text()').get('').strip(),
                        'url': i.attrib.get('rel', None),
                        'vip': True
                    }
                else:
                    section = {
                        'title': i.xpath('./text()').get('').strip()
                    }
                sections.append(json.dumps(section))
            infos.append([
                title,
                author,
                tags,
                sections,
                novelid
            ])
            if limit > 0 and len(infos) >= limit:
                return infos
        return infos

    def search_one_novel_info(self, novel_id):
        """
        搜索一篇小说的基本信息
        """

        print('>>>>>>>检查是否有小说基本信息缓存数据')
        if os.path.exists(f'novel_info/{novel_id}.txt'):
            in_file = open(f'novel_info/{novel_id}.txt', 'r')
            data = in_file.read()
            in_file.close()
            data_list = data.split('\n')
            title = json.loads(data_list[0])
            author = json.loads(data_list[1])
            tags = json.loads(data_list[2])
            sections = data_list[3:]
            # print(title)
            # print(author)
            # print(tags)
            # print('\n'.join(sections))

            return [
                title,
                author,
                tags,
                sections
            ]
        else:

            url = f'{self.base_url}/{self.novel_url}?novelid={novel_id}'
            print(url)
            r = self.session.get(url)
            # 解决中文乱码问题
            r.encoding = r.apparent_encoding
            tags = []

            # 标题
            i = Selector(r.text).css('#oneboolt > tbody > tr:nth-child(1) > td > div > span > h1 > span')
            title = i.xpath('./text()').get('').strip()

            # 作者
            i = Selector(r.text).css('#oneboolt > tbody > tr:nth-child(1) > td > div > h2 > a > span')
            author = i.xpath('./text()').get('').strip()

            # 标签
            for i in Selector(r.text).css('body > table:nth-child(23) > tr > td:nth-child(1) > div:nth-child(3) > span > a'):
                tags.append(i.xpath('./text()').get('').strip())
            
            # 文字类型（用作标签）
            i = Selector(r.text).css('body > table:nth-child(23) > tr > td:nth-child(3) > div.righttd > ul > li:nth-child(1) > span:nth-child(2)')
            types = i.xpath('./text()').get('').strip().split('-')
            tags.extend(types)
            print(tags)

            # 按章检索地址
            sections = []
            for i in Selector(r.text).css('#oneboolt > tbody > tr > td:nth-child(2) > span > div:nth-child(1) > a:nth-child(1)'):
                section = {}
                if i.attrib.get('href', None):
                    section = {
                        'title': i.xpath('./text()').get('').strip(),
                        'url': i.attrib.get('href', None),
                        'vip': False
                    }
                elif i.attrib.get('rel', None):
                    section = {
                        'title': i.xpath('./text()').get('').strip(),
                        'url': i.attrib.get('rel', None),
                        'vip': True
                    }
                else:
                    section = {
                        'title': i.xpath('./text()').get('').strip()
                    }
                sections.append(json.dumps(section))
                
                out_file = open(f'novel_info/{novel_id}.txt', 'w')
                out_file.write(json.dumps(title))
                out_file.write('\n')
                out_file.write(json.dumps(author))
                out_file.write('\n')
                out_file.write(json.dumps(', '.join(tags)))
                out_file.write('\n')
                out_file.write('\n'.join(sections))
                out_file.close()
            print(len(sections))
            return self.search_one_novel_info(novel_id)

    def novel_content(self, novel_info, limit = -1):
        """
        搜索一篇小说的内容
        """

        print('>>>>>>>检查是否有小说基本信息缓存数据')
        sections = eval(novel_info.chapterInfo)
        # print(sections)
        contents = []
        buy = False
        for section in sections:
            item = json.loads(section)
            time.sleep(self.delay)
            print(item)
            url = item.get('url')
            querys = parse_qs(urlparse(url).query)

            novelid = querys['novelid'][0]
            chapterid = querys['chapterid'][0]
            if not buy:
                self.buy_novel(novelid)
                buy = True

            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Cookie': '__yjs_duid=1_497e175e6ebaf07fcf9e81c150b9ba361615779888046; UM_distinctid=17833fc692e856-0e44b3f268bb4b-5771133-144000-17833fc692f724; token=NTA5NDg2NDN8YjkxY2EwM2IxYjcxNmQ5NWRhMWJhMjA2NTkxNGIwOTh8fDIwNioqKioqKipAcXEuY29tfHwyNTkyMDAwfDF8fHzmmYvmsZ/nlKjmiLd8MHxlbWFpbHwx; smidV2=20210315094244a184d9c1f8028619f7db29d8f9aaaa77009219be8c17b5370; timeOffset_o=1542; JJEVER={"foreverreader":"50948643","desid":"7K1nHIMQpzqgipzEHD0qUa84mIQvlWG2","sms_total":"1","user_signin_days":"20210325_50948643_0","fenzhan":"by"}; CNZZDATA30075907=cnzz_eid=1874283126-1615768092-&ntime=1616632092; testcookie=yes; Hm_lvt_bc3b748c21fe5cf393d26c12b2c38d99=1616038259,1616484069,1616551687,1616633556; JJSESS={"nicknameAndsign":"undefined~)%24","clicktype":""}; Hm_lpvt_bc3b748c21fe5cf393d26c12b2c38d99=1616633563',
                'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'
            }
            r = self.session.get(url, headers=headers)
            # 解决中文乱码问题
            r.encoding = r.apparent_encoding

            # 标题
            if item.get('vip') == False:
                res = Selector(r.text).css('#oneboolt > tr:nth-child(2) > td:nth-child(1) > div > div:nth-child(2) > h2')
            else:
                res = Selector(r.text).css('#oneboolt > tr:nth-child(2) > td:nth-child(1) > div > div:nth-child(3) > h2')

            title = res.xpath('./text()').get('').strip()
            print(title)

            # 获取小说区域
            # res = r.html.find('#oneboolt > tbody > tr:nth-child(2) > td:nth-child(1) > div')
            res = r.html.find('.noveltext')[0]
            print(res)

            # 构造正则表达式，去掉与小说文本无关的内容
            pattern = re.compile('<(div|button|a|img) [\s\S]*?</(div|button|a|img)>')
            if type(res).__name__ == 'list':
                new = re.sub(pattern, '', res[0].html)
            else:
                new = re.sub(pattern, '', res.html)

            # 提取小说纯文本
            s = HTML(html=new)
        
            contents.append({
                'novelid': novelid,
                'chapterNo': chapterid,
                'title': title,
                'url': url,
                'content': s.text
            })
            
            if limit > 0 and len(contents) >= limit:
                return contents
        return contents
            
            
    def search_one_novel(self, novel_id):
        """
        搜索一篇小说的内容
        """

        print('>>>>>>>检查是否有小说基本信息缓存数据')
        [title,
        author,
        tags,
        sections ] = self.search_one_novel_info(novel_id)
        # print(sections)

        for section in sections:
            item = json.loads(section)
            print(item)
            if item.get('vip') == False:
                url = item.get('url')
                r = self.session.get(url)
                # 解决中文乱码问题
                r.encoding = r.apparent_encoding

                # 获取小说区域
                res = r.html.find('#oneboolt > tr:nth-child(2) > td:nth-child(1) > div')[0]
                # 构造正则表达式，去掉与小说文本无关的内容
                pattern = re.compile('<(div|button|a|img) [\s\S]*?</(div|button|a|img)>')
                new = re.sub(pattern, '', res.html)

                # 提取小说纯文本
                s = HTML(html=new)
                print(s.text)
                return

    def buy_novel(self, novelid):
        
        session = requests.session()
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Cookie': '__yjs_duid=1_497e175e6ebaf07fcf9e81c150b9ba361615779888046; UM_distinctid=17833fc692e856-0e44b3f268bb4b-5771133-144000-17833fc692f724; token=NTA5NDg2NDN8YjkxY2EwM2IxYjcxNmQ5NWRhMWJhMjA2NTkxNGIwOTh8fDIwNioqKioqKipAcXEuY29tfHwyNTkyMDAwfDF8fHzmmYvmsZ/nlKjmiLd8MHxlbWFpbHwx; smidV2=20210315094244a184d9c1f8028619f7db29d8f9aaaa77009219be8c17b5370; JJEVER={"foreverreader":"50948643","desid":"7K1nHIMQpzqgipzEHD0qUa84mIQvlWG2","sms_total":"1","user_signin_days":"20210323_50948643_0","fenzhan":"by"}; testcookie=yes; Hm_lvt_bc3b748c21fe5cf393d26c12b2c38d99=1615976361,1615988691,1616038259,1616484069; JJSESS={"nicknameAndsign":"undefined~)%24","clicktype":""}; CNZZDATA30075907=cnzz_eid=1026667743-1615768092-http%3A%2F%2Fmy.jjwxc.net%2F&ntime=1616507892; timeOffset_o=2802.89990234375; Hm_lpvt_bc3b748c21fe5cf393d26c12b2c38d99=1616513063',
            'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'
        }
        url = 'http://my.jjwxc.net/backend/buynovel_ajax.php'
        data = {
            't': 2,
            'novelid': novelid
        }
        r = session.post(url,headers=headers,data=data)
        r.encoding = r.apparent_encoding
        
        url = 'http://my.jjwxc.net/backend/buynovel.php'
        data = {
            'action': 'check',
            'novelid': novelid
        }
        r = session.post(url,headers=headers,data=data)
        r.encoding = r.apparent_encoding
        
        url = 'http://my.jjwxc.net/backend/buynovel.php'
        data = {
            'action_type': 2,
            'action': 'add',
            'novelid': novelid,
            'renew_status': 0
        }
        r = session.post(url,headers=headers,data=data)
        r.encoding = r.apparent_encoding
        print(f'buy novel {novelid}')


    def save(self):
        df = pd.DataFrame(self.data_list)
        path = f'{str(int(time.time()))}.xlsx'
        with pd.ExcelWriter(path, engine='xlsxwriter', options={'strings_to_urls': False}) as writer:
            df.to_excel(writer, index=False, encoding='utf-8-sig')

        task_id = self.taskid
        print(self.data_list)
        for item in self.data_list:
            print(item)
            url = item['url']

            datas = query_db('select * from datas where url = \'' + url + '\'', one=True)
            if datas == None:
                data_id = str(uuid.uuid4())
                with sqlite3.connect("database.db") as con:
                        cur = con.cursor()
                        cur.execute("INSERT INTO datas (data_id,task_id,keyword,page,title,desc,url) VALUES (?,?,?,?,?,?,?)",(data_id,task_id,item['keyword'],item['page'],item['title'],item['desc'],item['url']) )
                        con.commit()
        msg = "Record successfully added"
        return msg


if __name__ == '__main__':
    print('start')
    c = Crawler()
    # print('start search_channel_address')
    # c.search_channel_address()
    # print('start search_novel_address')get
    # novel_url = c.search_novel_address()
    # print('start search_one_novel_info')
    c.search_one_novel(4217585)
