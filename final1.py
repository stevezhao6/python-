import requests
# mongodb
import pymongo
import self as self
# 解析html的库
from lxml import html, etree
import jieba
from PIL import  Image
from wordcloud import WordCloud

headers = {
        'User-Agent': 'Mozilla/4.0(compatible;MSIE8.0;WindowsNT6.0;Trident/4.0)'
}

url = 'https://www.kingname.info/archives/'
path = 'E:\python课程设计\images/'
suffix = ".txt"

# mongodb数据库连接
self.client = pymongo.MongoClient('mongodb://root:564929@localhost:27017/')

# 指定数据库
self.db = self.client.stevezhao

# 指定要操作集合stevezhao
self.collection_stevezhao = self.db.stevezhao

# 获取标题
def get_title():
    #页数
    n = 1
    #文章数
    m=0
    for i in range(0,13):
        if n != 1:
            html1 = requests.get(url=url + '/page/' + str(n))
        elif n==1:
            html1 = requests.get(url=url)

        # 转码
        html1.encoding = 'utf-8'
        # 获取源代码
        html_text = html1.text
        # 格式化解析网页代码的工具  etree补充不完整的标签
        etree_tools = html.etree
        # 格式化获取的网页代码
        format_html = etree_tools.HTML(html_text)
        # 获取标题的所有article标签
        article_anchors = format_html.xpath('//article[@class="post post-type-normal"]//header')
        for article in article_anchors:
            #一个li标签中只有一个a标签 用标签下一级要加.
            #文章标题
            title=article.xpath('./h2/a/span/text()')
            #文章时间
            new_date = article.xpath('./div/time/@content')
            #文章链接
            addr = 'https://www.kingname.info' +article.xpath('./h2/a/@href')[0]
            #文章标签
            new_type=get_type(addr)
            #文章内容
            content=get_content(addr)
            # title转换为字符串格式
            title =title[0]
            intab = '?/"|.><:*'
            for s in intab:
                if s in title:
                    title = title.replace(s, '')
            # 打印当前爬取的文章标题
            print(title)
            # 保存到mongodb数据库
            temp_data = {"文章标题":title,"文章内容":content,"文章链接":addr,"文章标签":new_type,"文章日期":new_date}
            result = self.collection_stevezhao.insert_one(temp_data)

            # 文件保存操作
            filePath = path + title + suffix
            with open(filePath, "w+", encoding='utf-8') as file:
                file.write(title[0])
                file.write(content)

            #制作云图
            print_cloud(str(get_content_list(addr)),title)
        n=n+1
        print(n)



# 返回文章类型
def get_type(addr):
    type_html = etree.HTML(requests.get(addr, headers).text)
    new_type = type_html.xpath('//span[contains(@itemprop,"name")]/text()')
    return new_type


# 返回文章正文
def get_content(addr):
    content_html = etree.HTML(requests.get(addr, headers).text)
    #content = content_html.xpath('//div[@class="post-body"]//p/text()')
    content = content_html.xpath('//div[contains(@itemprop,"articleBody")]')[0]
    return str(etree.tostring(content, encoding='utf-8'), 'utf-8')

# 返回文章正文的列表 用于制作词云
def get_content_list(addr):
    content_html = etree.HTML(requests.get(addr, headers).text)
    content = content_html.xpath('//div[@class="post-body"]//p/text()')
    return content

#生成词云
def print_cloud(content,tittle):
    #制作词云
    wl_space_split=' '.join(jieba.lcut(content)) #jieba返回分好的词
    #stop_words=set(STOPWORDS)
    import numpy as np
    abel_mask=np.array(Image.open('003.jpg'))
    #生成词云
    wc=WordCloud(
        background_color='white',#背景颜色
        font_path='simfang.ttf',#字体
        max_words=3000,#最大词数
        max_font_size=100,#显示字体最大值
        random_state=42,#为每个词放回一个PIL颜色
        mask=abel_mask#以该参数值作图绘制词云
        #stopwords=STOPWORDS#屏蔽词
    ).generate(wl_space_split)#生成词云

    #保存生成的词云图片
    wc.to_file('E:\python课程设计\images/'+tittle+'.jpg')

if __name__ == '__main__':
    get_title()
