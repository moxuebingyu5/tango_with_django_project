import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tango_with_django_project.settings')

import django
django.setup()
from rango.models import Category, Page

def populate():
    # 首先创建一些字典，列出想添加到各分类的网页
    # 然后创建一个嵌套字典，设置各分类
    # 这么做看起来不易理解，但是便于迭代，方便为模型添加数据
    python_pages = [{"title": "Official Python Tutorial", "url":"http://docs.python.org/2/tutorial/"},
                    {"title":"How to Think like a Computer Scientist", "url":"http://www.greenteapress.com/thinkpython/"},
                    {"title":"Learn Python in 10 Minutes", "url":"http://www.korokithakis.net/tutorials/python/"}]
    django_pages = [{"title":"Official Django Tutorial", "url":"https://docs.djangoproject.com/en/1.9/intro/tutorial01/"},
                    {"title":"Django Rocks", "url":"http://www.djangorocks.com/"},
                    {"title":"How to Tango with Django", "url":"http://www.tangowithdjango.com/"} ]
    other_pages = [{"title": "Bottle", "url": "http://bottlepy.org/docs/dev/"},
                   {"title": "Flask", "url": "http://flask.pocoo.org"}]
    cats = {"Python": {"pages": python_pages},
            "Django": {"pages": django_pages},
            "Other Frameworks": {"pages": other_pages}}

    # 如果想添加更多分类或网页，添加到前面的字典中即可
    # 下述代码迭代 cats 字典，添加各分类，并把相关的网页添加到分类中
    # 如果使用的是 Python 2.x，要使用 cats.iteritems() 迭代
    # 迭代字典的正确方式参见
    # http://docs.quantifiedcode.com/python-anti-patterns/readability/
    for cat, cat_data in cats.items():
        c = add_cat(cat)
        for p in cat_data["pages"]:
            add_page(c, p["title"], p["url"])
    # 打印添加的分类
    for c in Category.objects.all():
        for p in Page.objects.filter(category=c):
            print("- {0} - {1}".format(str(c), str(p)))

def add_page(cat, title, url, views=0):
    print(cat)
    print("标题：" + title)
    print("链接：" + url)
    print(Page.objects.get_or_create(category=cat, title=title))
    p = Page.objects.get_or_create(category=cat, title=title)[0]
    p.url=url
    p.views=views
    p.save()
    return p

def add_cat(name):
    c = Category.objects.get_or_create(name=name)[0]
    c.save()
    return c
# 从这开始执行
if __name__ == '__main__':
    print("Starting Rango population script...")
    populate()