 
from dataclasses import dataclass
import codecs
import pymysql
import leancloud

@dataclass
class CommentData:
    post_name: str
    comment_ID: int
    comment_post_ID: int
    comment_author: str
    comment_author_email: str
    comment_author_url: str
    comment_author_IP: str
    comment_date: str
    comment_date_gmt: str
    comment_content: str
    comment_karma: int
    comment_approved: int
    comment_agent: str
    comment_type: str
    comment_parent: int
    user_id: int
    comment_mail_notify: int

# url may change 
title_change = {}
with codecs.open('title-change.csv', 'r', encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if line:
            line = line.split(',')
            title_change[line[0]] = line[2]
print(title_change)

# get all comment
db = pymysql.connect("localhost","root","","wordpress" )
cursor = db.cursor()
cursor.execute("SELECT p.post_name, c.* FROM `wp_comments` c , `wp_posts` p WHERE c.comment_post_ID = p.ID")
results = cursor.fetchall()
comment_list = []
for row in results:
    data = CommentData(*row)
    data.comment_date = data.comment_date.isoformat()
    if data.post_name in title_change:
        data.post_name = title_change[data.post_name]
    comment_list.append(data)
db.close()

"""
example
{
  "nick": "12515",
  "ip": "39.155.192.81",
  "ACL": {
    "*": {
      "read": true
    }
  },
  "mail": "125125",
  "ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36",
  "insertedAt": {
    "__type": "Date",
    "iso": "2020-11-05T15:18:14.128Z"
  },
  "pid": "5fa417827e502a242397edc3",
  "link": "112",
  "comment": "1111\n",
  "url": "/about-me/",
  "QQAvatar": "",
  "rid": "5fa417827e502a242397edc3",
  "objectId": "5fa417b6ab05356ee26b9bfc",
  "createdAt": "2020-11-05T15:18:14.503Z",
  "updatedAt": "2020-11-05T15:18:14.503Z"
}
"""

leancloud.init("", "")
TestObject = leancloud.Object.extend('Comment')
coment_object_id = {}
comment_list.sort(key=lambda x: x.comment_ID)
for comment in comment_list:
    test_object = TestObject()
    test_object.set('nick', comment.comment_author)
    test_object.set('insertedAt', {
        "__type": "Date",
        "iso": comment.comment_date
    })
    test_object.set('status', 1)
    test_object.set('comment', comment.comment_content)
    test_object.set('comment_id', comment.comment_ID)
    test_object.set('mail', comment.comment_author_email)
    test_object.set('ua', comment.comment_agent)
    test_object.set('ip', comment.comment_author_IP)

    test_object.set('url', '/{}/'.format(comment.post_name))
    test_object.fetch_when_save = True
    if comment.comment_parent != 0:
        test_object.set('pid', coment_object_id[comment.comment_parent])
        test_object.set('rid', coment_object_id[comment.comment_parent])
    try:
        test_object.save()
        coment_object_id[comment.comment_ID] = test_object.get('objectId')
    except leancloud.LeanCloudError as e:
        print('error', e, comment)