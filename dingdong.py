import json
import os
import sys
import time
from os import system
from random import random
import execjs

import requests
import uuid
import _thread
import threading

uid = "62537365adeb2f0001f91352"
longitude = "121.498563"
latitude = "31.290792"
station_id = "5cc7ad3a716de1c6058b456d"
s_id = "22a22294f5dad7829e43c0e290bb6b15"
openid = "osP8I0dpnlIJ6HiW9R5Otj29rRkk"
address_id = "625374b8902c1500016c8088"
device_token = "WHJMrwNw1k/FKPjcOOgRd+PYu/fG6mKMpPK4AAR+E3AGZ/MFq1fYz1/h4HvMzOJjQLY6kJxvSzvHTGSQia8QqypP9HbamO0DVdCW1tldyDzmauSxIJm5Txg==1487582755342"
Cookie = "DDXQSESSID=xxx"
notifyurl="https://api.day.app/barkid/"
#以下固定 不修改
reserved_time_start="1680123600"
reserved_time_end="1680188400"
user_ticket_id = ""
new_order_product_list = []
keylist = ["id","category_path","count","price","total_money","instant_rebate_money","activity_id","conditions_num","product_type","sizes","type","total_origin_money","price_type","batch_type","sub_list","order_sort","origin_price"]
header = {
    "method": "POST",
    "scheme": "scheme",
    "path": "/order/getMultiReserveTime",
    "authority": "maicai.api.ddxq.mobi",
    "accept-language": "zh-cn",
    "accept": "*/*",
    "ddmc-station-id": station_id,
    "content-type": "application/x-www-form-urlencoded",
    "ddmc-city-number": "0101",
    "ddmc-build-version": "2.82.0",
    "ddmc-device-id": "osP8I0UQ8IZ2TwQGGoUjsFTARfj8",
    "ddmc-channel": "applet",
    "ddmc-os-version": "[object Undefined]",
    "ddmc-app-client-id": "4",
    "ddmc-ip": "",
    "ddmc-longitude": longitude,
    "ddmc-latitude": latitude,
    "ddmc-api-version": "9.49.2",
    "ddmc-uid": uid,
    "accept-encoding": "gzip,compress,br,deflate",
    "Cookie": Cookie,
    "referer": "https://servicewechat.com/wx1e113254eda17715/422/page-frame.html",
    "user-agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.18(0x1800123f) NetType/4G Language/zh_CN"
}

#代购商品
products = dict()
parent_order_sign = ""
prd = dict()
#仓库
cart = dict()


with open('sign.js', 'r', encoding='UTF-8') as f:
    signjs_code = f.read()
contextjs = execjs.compile(signjs_code)


#生成时间
def generatetime(product):

    """
    zeroPoint = int(time.time()) - int(time.time() - time.timezone) % 86400
    reserved_time_start = str(zeroPoint+ 3600*7)
    reserved_time_end = str(zeroPoint+ 3600*22)

    if int(time.time()) > int(reserved_time_start):
        reserved_time_start = int(time.time())+3600*2
    """
    plist = json.loads(product).get('data').get('new_order_product_list')

    if len(plist) == 0:
        print('没货了，购物车加进来没，重新跑吧')
        sys.exit()
    plist = plist[0];
    plist = plist.get('products')
    newlist = []
    newlist.append(plist)
    payload ={
     "uid": uid,
     "longitude": longitude,
     "latitude": latitude,
     "station_id": station_id,
     "city_number": "0101",
     "api_version": "9.49.2",
     "app_version": "2.82.0",
     "applet_source": "",
     "channel": "applet",
     "app_client_id": 4,
     "sharer_uid": "",
     "s_id": s_id,
     "openid": openid,
     "h5_source": "",
     "device_token": device_token,
     "address_id": address_id,
     "group_config_id": "",
     "products": str(newlist),
     "isBridge": "false",
     "nars": "4a6be357220b0edec093691f6a66f430",
     "sesi": "yQJL6tP21bf5a2e5f19d3f35adfdd3595744d2d"
}
    print(payload)
    r_json = requests.post('https://maicai.api.ddxq.mobi/order/getMultiReserveTime', data = payload, headers = header)
    while True:
        if json.loads(r_json.text).get('success'):
            break
        else:
            r_json = requests.post('https://maicai.api.ddxq.mobi/order/getMultiReserveTime', data = payload, headers = header)
    plist = json.loads(r_json.text).get('data')
    if len(plist) == 0:
        print('拉取时间失败重新启动拉取吧')
        sys.exit()
    onlyplist = (plist[0].get('time'))[0].get('times')[0]
    #plist = json.loads(plist)
    timelist = (plist[0].get('time'))[0].get('times')

    global reserved_time_start
    global  reserved_time_end
    for mytime in timelist:
        if mytime.get('fullFlag') == False:
            print(mytime.get('start_timestamp'))
            print(mytime.get('end_timestamp'))
            reserved_time_start = mytime.get('start_timestamp')
            reserved_time_end = mytime.get('end_timestamp')
            return
    print('预约时间满了，等会再来吧')
    sys.exit()
    #print(onlyplist.get('start_timestamp'))
    #print(onlyplist.get('end_timestamp'))


#检查购物车状态
def getcart():
    url = "https://maicai.api.ddxq.mobi/cart/allCheck?uid=" + uid + "&longtitude=" + longitude + "&latitude=" + latitude + "&station_id=" + station_id + "&city_number=0101&api_version=9.49.2&app_version=2.82.0&applet_source=&channel=applet&app_client_id=4&sharer_uid=&s_id=" + s_id + "&openid=" + openid + "&device_token=" + device_token + "&is_check=1&is_load=1"
    result = requests.get(url=url, headers=header)
    while True:
        if json.loads(result.text).get('code') == 1111:
            print('会话过期了')
            sys.exit()
        if len(json.loads(result.text).get('data').get('new_order_product_list')) == 0:
            print(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+'没货了，继续刷')
            time.sleep(5)
            continue
        elif json.loads(result.text).get('success'):
            break
        else:
            result = requests.get(url=url, headers=header)
    print(result.text)
    return result.text
#检查订单
def checkorder(order):
    plist = json.loads(order).get('data').get('new_order_product_list')

    global  new_order_product_list
    new_order_product_list = plist


    """
    if len(plist) == 0:
        print('没货了，购物车加进来没，重新跑吧')
        sys.exit()
    """
    global parent_order_sign
    parent_order_sign = json.loads(order).get('data').get('parent_order_info').get('parent_order_sign')

    plist = plist[0];
    #保存prodcuct
    prd = plist['products']
    products['packages']=prd
    for key in plist:
        if key == "products":
            portList = plist[key]
            dicNum = 0
            for portDict in portList:
                dicNum += 1
                #for portDictKey in portDict:
                for portDictKey in list(portDict.keys()):
                    if portDictKey == "sale_batches":
                        portDict['batch_type'] = portDict['sale_batches']['batch_type']
                        del portDict[portDictKey]
                    elif portDictKey == "total_price":
                        portDict['total_money'] = portDict[portDictKey]
                        del portDict[portDictKey]
                    elif portDictKey == "total_origin_price":
                        portDict['total_origin_money'] = portDict[portDictKey]
                        del portDict[portDictKey]
                    elif portDictKey not in keylist:
                        del portDict[portDictKey]
    reserved_time = dict()
    reserved_time['reserved_time_start'] = reserved_time_start
    reserved_time['reserved_time_end'] = reserved_time_end
    plist['reserved_time'] = reserved_time


    #print(plist)
    str1 = "["+str(plist)+"]";
    global cart
    cart = plist
    #print(cart)

    str1 = str1.replace("'","\"")
    #print(str1)

    #str2 = urllib.parse.quote(str1, safe="")

    #开始检查订单
    postdata ={
     "uid": uid,
     "longitude": longitude,
     "latitude": latitude,
     "station_id": station_id,
     "city_number": "0101",
     "api_version": "9.49.2",
     "app_version": "2.82.0",
     "applet_source": "",
     "channel": "applet",
     "app_client_id": 4,
     "sharer_uid": "",
     "s_id": s_id,
     "openid": openid,
     "h5_source": "",
     "device_token": device_token,
     "address_id": address_id,
     "user_ticket_id": "default",
     "freight_ticket_id": "default",
     "is_use_point": 0,
     "is_use_balance": 0,
     "is_buy_vip": 0,
     "coupons_id": "",
     "is_buy_coupons": 0,
     "packages": str1,
     "check_order_type": 0,
     "is_support_merge_payment": 1,
     "showData": "true",
     "showMsg": "false",
     "nars": "f925850c8a5db6203fd4d727fff923b4",
     "sesi": "TJlhL1X85bcf90def8e4956200b46b74cbc460c"
}

    print(postdata)
    postdatajs = json.dumps(postdata)
    signnarsout = contextjs.call("sign",postdatajs)
    signnarsout = json.loads(signnarsout)
    postdata['nars'] = signnarsout['nars']
    postdata['sesi'] = signnarsout['sesi']

    r_json = requests.post('https://maicai.api.ddxq.mobi/order/checkOrder', data = postdata, headers = header)
    while True:
        if json.loads(r_json.text).get('success'):
            break
        else:
            r_json = requests.post('https://maicai.api.ddxq.mobi/order/checkOrder', data = postdata, headers = header)
    #print(r_json.request.body)
    coupon = json.loads(r_json.text).get('data').get('order').get('default_coupon')
    global  user_ticket_id
    if coupon != None:
        user_ticket_id = coupon.get('_id')
    #print(r_json.text)
    return  r_json.text
#组织下单内容
cnt = 0

def justorder(payload):
    global  cnt
    while True:
        r_json = requests.post('https://maicai.api.ddxq.mobi/order/addNewOrder', data=payload, headers=header)
        cnt = cnt+1
        print(cnt,r_json.text)
        if json.loads(r_json.text).get('success'):
            notify(r_json.text)
            os._exit(0)
            break
    print(r_json.text)
    return  r_json.text

def makeorder(order):
    pjson = json.loads(order).get('data')

    payment_order={
        "reserved_time_start":reserved_time_start,
        "reserved_time_end": reserved_time_end,
        "price":pjson.get('order').get('total_money'),
        "freight_discount_money": pjson.get('order').get('freight_discount_money'),
        "freight_money": pjson.get('order').get('freight_money'),
        "order_freight": pjson.get('order').get('freight_real_money'),
        "parent_order_sign": parent_order_sign,
        "product_type": 1,
        "address_id": address_id,
        "form_id": ''.join(str(uuid.uuid4()).split('-')),
        #"receipt_without_sku": ,
        "pay_type": 6,
		"vip_money": "",
		"vip_buy_user_ticket_id": "",
		"coupons_money": "",
		"coupons_id": ""
    }
    if user_ticket_id is not  None:
        payment_order = {
            "reserved_time_start": reserved_time_start,
            "reserved_time_end": reserved_time_end,
            "price": pjson.get('order').get('total_money'),
            "freight_discount_money": pjson.get('order').get('freight_discount_money'),
            "freight_money": pjson.get('order').get('freight_money'),
            "order_freight": pjson.get('order').get('freight_real_money'),
            "parent_order_sign": parent_order_sign,
            "product_type": 1,
            "address_id": address_id,
            "form_id": ''.join(str(uuid.uuid4()).split('-')),
            # "receipt_without_sku": ,
            "pay_type": 6,
            "user_ticket_id": user_ticket_id,
            "vip_money": "",
            "vip_buy_user_ticket_id": "",
            "coupons_money": "",
            "coupons_id": ""
        }
    strcart1 = str(cart).replace("'","\"")
    del cart['reserved_time']
    cart['reserved_time_start'] = reserved_time_start
    cart['reserved_time_end'] = reserved_time_end
    str2 = json.dumps(cart,ensure_ascii=False)
    packagedict = []
    packagedict.append(cart)
    package_order = {
        "payment_order": payment_order,
        "packages":packagedict
    }
    orderpostdata = {
        "uid": uid,
        "longitude": longitude,
        "latitude": latitude,
        "station_id": station_id,
        "city_number": "0101",
        "api_version": "9.49.2",
        "app_version": "2.82.0",
        "applet_source": "",
        "channel": "applet",
        "app_client_id": 4,
        "sharer_uid": "",
        "s_id": s_id,
        "openid": openid,
        "h5_source": "",
        "device_token": device_token,
        "package_order": json.dumps(package_order,ensure_ascii=False),
        "showMsg": "false",
        "showData": "true",
        "ab_config": {
            "key_onion": "C"
        },
        "nars": "bc01e7e016ee73db45aecf4a8dfe1373",
        "sesi": "6yWZh7v4233dc6138d52b1597ae15d7bae46859"
    }
    print(orderpostdata)
    while True:

        r_json = requests.post('https://maicai.api.ddxq.mobi/order/addNewOrder', data=orderpostdata, headers=header)
        print(r_json.text)
        if json.loads(r_json.text).get('success'):
            notify(r_json.text)
        elif (60000 <= int(time.strftime("%H%M%S")) <= 60500):
            s = threading.Thread(target=justorder, args=(orderpostdata,))  # 注意传入的参数一定是一个元组!
            s.start()
            t = threading.Thread(target=justorder, args=(orderpostdata,))  # 注意传入的参数一定是一个元组!
            t.start()
            t.join()
            s.join()
        elif (83000 <= int(time.strftime("%H%M%S")) <= 83500):
            s = threading.Thread(target=justorder, args=(orderpostdata,))  # 注意传入的参数一定是一个元组!
            s.start()
            t = threading.Thread(target=justorder, args=(orderpostdata,))  # 注意传入的参数一定是一个元组!
            t.start()
            t.join()
            s.join()
        print(r_json.request.body)

    print(r_json.text)
    return  r_json.text

def notify(response):
    order_number = json.loads(response).get('data').get('order_number')
    payload = {
        "uid": uid,
        "longitude": longitude,
        "latitude": latitude,
        "station_id": station_id,
        "city_number": "0101",
        "api_version": "9.49.2",
        "app_version": "2.82.0",
        "applet_source": "",
        "channel": "applet",
        "app_client_id": 4,
        "sharer_uid": "",
        "s_id": s_id,
        "openid": openid,
        "h5_source": "",
        "device_token": device_token,
        "address_id": address_id,
        "group_config_id": "",
        "order_number": order_number,
        "isBridge": "false",
        "nars": "4a6be357220b0edec093691f6a66f430",
        "sesi": "yQJL6tP21bf5a2e5f19d3f35adfdd3595744d2d"
    }
    r_json = requests.post('https://maicai.api.ddxq.mobi/order/orderDetailForSplit', data = payload, headers = header)
    while True:
        if json.loads(r_json.text).get('success'):
            break
        else:
            r_json = requests.post('https://maicai.api.ddxq.mobi/order/orderDetailForSplit', data = payload, headers = header)
    buylist = json.loads(r_json.text).get('data').get('product')
    buystr = ""
    for buy in buylist:
        print(buy['product_name']+" 价格:" + buy['origin_price'] + " 共" + str(buy['count']) +"份\n")
        buystr += buy['product_name']+" 价格:" + buy['origin_price'] + " 共" + str(buy['count']) +"份\n"
    global  notifyurl
    notifyurl += "叮咚买到了"
    result = requests.get(url=notifyurl, headers=header)

    weixurl = "https://sc.ftqq.com/SCU4165T1d50896f446c107e3f2a2cb60e0b91ee583c409e9f835.send?text="
    weixurl+= buystr
    weixurl+=",叮咚买菜抢到了"
    result = requests.get(url=weixurl, headers=header)
    print('购买成功，正在通知中')
    os._exit(0)



# press the green button in the gutter to run the script.
if __name__ == '__main__':
    #time.sleep(50)
    productlist = getcart()
    #generatetime(productlist)

    order=checkorder(productlist)
    makeorder(order)
