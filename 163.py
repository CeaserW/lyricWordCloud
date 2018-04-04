#-*- coding:utf-8 -*-
import requests
from bs4 import BeautifulSoup
import sqlite3
import sys
import re
import os
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import jieba
from PIL import Image
import numpy as np
import time  
DB_PATH = sys.path[0] + '/song_info.db'
headers = {
		'Referer'	:'http://music.163.com',
		'Host'	 	:'music.163.com',
		'Accept' 	: 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
		'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'
	}

# s = requests.Session()
# r = s.get(song_url,headers = headers).content
# bs = BeautifulSoup(r)
# print (bs.prettify())
# main_table = bs.find('ul',{'class':'f-hide'})

# for m in main_table.find_all('a'):
# 	print ('{}'.format(m.text))
def get163SongList(song_url,headers):
	res = requests.request('GET',song_url,headers=headers)
	# print (type(res.json()))
	song_list = res.json()['result']['tracks']
	return song_list
	# insetDataToDB(DB_PATH,song_list)
	# for song_info in song_list:
	# 	lyric_url = 'http://music.163.com/api/song/lyric?os=pc&id=' + str(song_info['id']) + '&lv=-1&kv=-1&tv=-1'
	# 	getSongLyric(headers,lyric_url)
	# 	print (song_info['name']+'___'+ song_info['artists'][0]['name'])


def createDB(path):
	conn = sqlite3.connect(path)
	cursor = conn.cursor()
	sqlStr = '''create table if not exists song_info (
		name text,
		singer text,
		id integer primary key autoincrement,
		song163id integer unique 
	)
	'''
	cursor.execute(sqlStr)
	cursor.close()



def insetDataToDB(path,song_list):
	conn = sqlite3.connect(path)
	cursor = conn.cursor()
	for song_info in song_list:
		# print (song_info['name']+'___'+ song_info['artists'][0]['name'])
		song_name = song_info['name']
		singer_name =  song_info['artists'][0]['name']
		song_163id = song_info['id']
		sqlStr = '''replace into song_info (name, singer,song163id) values (?,?,?)'''
		# try:
		cursor.execute(sqlStr,(song_name,singer_name,song_163id))
		conn.commit()
		# except Exception as e:
		# 	conn.rollback()
			# sys.exit() 

	cursor.close()
	conn.close()
	print ('结束')

def getSongLyric(headers,lyric_url):
	res = requests.request('GET',lyric_url,headers=headers)
	# print(res.json())
	if 'lrc' in res.json():
		lyric = res.json()['lrc']['lyric']
		lyric_without_time = re.sub(r'[\d:.[\]]','',lyric)
		return lyric_without_time
	else:
		return ''
		print(res.json())
	# print(lyric_without_time.readLines())
	# writeLyricTofile(lyric_without_time,'喜欢你')

def writeLyricTofile(song_lyric,song_name):
	print('正在写入：' + song_name)
	with open('lyric/'+'only'+'.text','a+',encoding='utf-8') as f:
		f.write(song_lyric)
	with open('lyric/'+ song_name +'.text','a+',encoding='utf-8') as f:
		f.write(song_lyric)

def createLyricFile():
	isExists = os.path.exists('lyric')
	if not isExists:
		os.makedirs('lyric')

def createWordCloud(f):
	print('根据词频，开始生成词云!')
	f1 = f.replace('作词','')
	f2 = f1.replace('作曲','')
	cut_text = "   ".join(jieba.cut(f2,cut_all=False, HMM=True))
	# print(cut_text)
	# color_mask = plt.imread("dy.png")
	# color_mask = np.array(Image.open(os.path.join(os.path.dirname(__file__), "aa.jpg")))
	wc = WordCloud(
		font_path="aaa.ttf",
		# mask=color_mask,
		max_words=100,
		width=2000,
		height=1200,
		margin=2,
    )

	wordcloud = wc.generate(cut_text)
	wordcloud.to_file(os.path.join(os.path.dirname(__file__), "h11.jpg"))
	print('打开词云图片')
	plt.imshow(wordcloud)
	plt.axis("off")
	plt.show()
	
	print('生成词云成功!')

def main():
	SONGLISTID = sys.argv[1]
	createLyricFile()
	createDB(DB_PATH)
	# 1获取歌单 歌曲列表信息
	song_url = 'http://music.163.com/api/playlist/detail?id=' + SONGLISTID
	song_list = get163SongList(song_url,headers)
	# 2 存入本地数据库
	insetDataToDB(DB_PATH,song_list)

	# 3获取每首歌歌词
	for song in song_list:
		# time.sleep(0.3)
		lyric_url = 'http://music.163.com/api/song/lyric?os=pc&id=' + str(song['id']) + '&lv=-1&kv=-1&tv=-1'
		lyric = getSongLyric(headers,lyric_url)
		song_name = song['name'].replace('/','_')
		writeLyricTofile(lyric,song_name)
	f = open('lyric/'+'only'+'.text','r',encoding='utf-8').read()

	#根据词频 生成词云
	createWordCloud(f)
	



main()