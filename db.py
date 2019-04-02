from config import *
import pymysql


def save(drivers):
    try:
        db = pymysql.connect(host=HOST, user=USER, passwd=PASSWORD, db=DB, use_unicode=True,
                             charset="utf8")
        cursor = db.cursor()
        insert_color = ('''INSERT INTO tag_driver_info_decode(brand_name,name,version,storage_name,color_name,price,img_url,app_code,url)
                               VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)''')
        for driver in drivers:
            data_house = (
                driver['brand_name'], driver['name'], driver['version'], driver['storage_name'], driver['color_name'],
                driver['price'], driver['img_url'], driver['app_code'], driver['url'])
            cursor.execute(insert_color, data_house)
        db.commit()
        print('插入成功')
    except Exception as e:
        print("插入失败,e:", e)
