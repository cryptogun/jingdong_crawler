#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import urllib.request

import re
import time
import random

import smtplib
from email.mime.text import MIMEText

import configparser#read and save configuration.
import ast
import json

import sys
import webbrowser
import codecs

def beep():
    """play an alarm."""
    print("\a")

    """
    import winsound
    Freq = 500 # Set Frequency To 2500 Hertz
    Dur = 200 # Set Duration To 1000 ms == 1 second
    winsound.Beep(Freq,Dur)
    """

class Settings:
    """
    Read settings from jingdong_crawler_setting.ini .
    """
    def __init__(self):
        self._read_ini()

    def _read_ini(self):
        self.config=configparser.ConfigParser(delimiters=('='), allow_no_value=True)
        self.config.read_file(codecs.open('jingdong_crawler_setting.ini', "r", "utf-8"))

    def get_sleep_interval(self):
        """Get interval between every two waves of querying."""
        try:
            time_str=self.config.get("通用设置", "查询时间间隔秒")
            time_str_list=time_str.replace("x", "*").replace("X", "*").split("*")
            seconds=1
            for i in time_str_list:
                seconds=seconds*int(i)
            if seconds>0:
                return seconds
            else:
                return 60
        except Exception as e:
            print(str(e))
            return 60

    def get_monitoring_addr(self):
        try:
            MONITORING_ADDR=self.config.get("通用设置", "监控商品网址")
            return MONITORING_ADDR
        except Exception as e:
            print(str(e))
            return ""

    def is_debug(self):
        try:
            debug_str=self.config.get("通用设置", "调试")
            if debug_str in ("True", "true", "TRUE", "是"):
                return True
            else:
                return False
        except Exception as e:
            print(str(e))
            return False
    def get_province_id(self):
        try:
            iden=self.config.get("收货地址", "省编号")
            return int(iden)
        except Exception as e:
            print(str(e))
            return 1
    def get_city_id(self):
        try:
            iden=self.config.get("收货地址", "市编号")
            return int(iden)
        except Exception as e:
            print(str(e))
            return 72
    def get_county_id(self):
        try:
            iden=self.config.get("收货地址", "县编号")
            return int(iden)
        except Exception as e:
            print(str(e))
            return 2799

    def is_query_title(self):
        try:
            is_query=self.config.get("需要检测变更的内容", "标题")
            if is_query in ("True", "true", "TRUE", "是"):
                return True
            else:
                return False
        except Exception as e:
            print(str(e))
            return False        
    def is_query_detail(self):
        try:
            is_query=self.config.get("需要检测变更的内容", "描述")
            if is_query in ("True", "true", "TRUE", "是"):
                return True
            else:
                return False
        except Exception as e:
            print(str(e))
            return False        
    def is_query_stock(self):
        try:
            is_query=self.config.get("需要检测变更的内容", "存货状态")
            if is_query in ("True", "true", "TRUE", "是"):
                return True
            else:
                return False
        except Exception as e:
            print(str(e))
            return False        
    def is_query_promotion(self):
        try:
            is_query=self.config.get("需要检测变更的内容", "活动")
            if is_query in ("True", "true", "TRUE", "是"):
                return True
            else:
                return False
        except Exception as e:
            print(str(e))
            return False        
    def is_query_coupon(self):
        try:
            is_query=self.config.get("需要检测变更的内容", "优惠券")
            if is_query in ("True", "true", "TRUE", "是"):
                return True
            else:
                return False
        except Exception as e:
            print(str(e))
            return False        
    def is_query_mobi(self):
        try:
            is_query=self.config.get("需要检测变更的内容", "移动端优惠")
            if is_query in ("True", "true", "TRUE", "是"):
                return True
            else:
                return False
        except Exception as e:
            print(str(e))
            return False        
    def is_query_price(self):
        try:
            is_query=self.config.get("需要检测变更的内容", "降价")
            if is_query in ("True", "true", "TRUE", "是"):
                return True
            else:
                return False
        except Exception as e:
            print(str(e))
            return False        
    def is_play_music(self):
        try:
            is_query=self.config.get("变更播放提示音乐", "播放音乐")
            if is_query in ("True", "true", "TRUE", "是"):
                return True
            else:
                return False
        except Exception as e:
            print(str(e))
            return False        

    def get_music_path(self):
        try:
            return self.config.get("变更播放提示音乐", "音乐位置")
        except Exception as e:
            print(str(e))
            return ""

    def is_send_email(self):
        try:
            is_send=self.config.get("邮件提醒", "发送邮件提醒")
            if is_send in ("True", "true", "TRUE", "是"):
                return True
            else:
                return False
        except Exception as e:
            print(str(e))
            return False        

    def get_sender_email_server(self):
        try:
            return self.config.get("邮件提醒", "发件人邮件服务器")
        except Exception as e:
            print(str(e))
            return ""
    def get_sender_email_account(self):
        try:
            return self.config.get("邮件提醒", "发件人邮箱账号")
        except Exception as e:
            print(str(e))
            return ""
    def get_sender_email_passwd(self):
        try:
            return self.config.get("邮件提醒", "发件人邮箱密码")
        except Exception as e:
            print(str(e))
            return ""

    def get_receiver_email_account(self):
        try:
            return self.config.get("邮件提醒", "收件人邮箱账号").split("|")
        except Exception as e:
            print(str(e))
            return ""

settings = Settings()

MAX_PRICE=10000000
#SLEEP_INTERVAL seconds.
SLEEP_INTERVAL=settings.get_sleep_interval()
MONITORING_ADDR=settings.get_monitoring_addr()
DEBUG=settings.is_debug()
PROVINCEID=settings.get_province_id()
CITYID=settings.get_city_id()
COUNTYID=settings.get_county_id()

QUERY_TITLE=settings.is_query_title()
QUERY_DETAIL=settings.is_query_detail()
QUERY_STOCK=settings.is_query_stock()
QUERY_PROMOTION=settings.is_query_promotion()
QUERY_COUPON=settings.is_query_coupon()
QUERY_MOBI=settings.is_query_mobi()
QUERY_PRICE=settings.is_query_price()

PLAY_MUSIC=settings.is_play_music()
MUSIC_PATH=settings.get_music_path()
SEND_EMAIL=settings.is_send_email()
SENDER_MAIL_SERVER=settings.get_sender_email_server()
SENDER_EMAIL_ACCOUNT=settings.get_sender_email_account()
SENDER_EMAIL_PASSWD=settings.get_sender_email_passwd()
RECEIVER_EMAIL_ACCOUNTS=settings.get_receiver_email_account()







class Product:
    def __init__(self,id_i):
        self.id_i=id_i
        self.url="http://item.m.jd.com/product/"+self.id_i+".html?provinceId=%d&cityId=%d&countyId=%d"%(PROVINCEID, CITYID, COUNTYID)
        self.page=None
        self.html=None
        self._compile_regex_object()
        #self.load_html()

    def _compile_regex_object(self):
        regex_title=r'<meta name="keywords" CONTENT="(.+?)">'
        regex_price=r'<input type="hidden" id="jdPrice" name="jdPrice" value="(-?[0-9.]+?)"/>'
        regex_promotion=r'<div class="prod-act">(.+?)</div>'
        regex_detail=r'<div class="act-link">(.+?)<a href'
        regex_mobile_discount=r'height="32" width="32">(.+?)[\r\n]'
        regex_stock=r'<span class="isExist">(..)'

        regex_province=r'<span id="provinceName">(.+?)</span>'
        regex_city=r'<span id="cityName">(.+?)</span>'
        regex_county=r'<span id="countyName">(.+?)</span>'

        self.re_compile_title=re.compile(regex_title)
        self.re_compile_price=re.compile(regex_price)
        self.re_compile_promotion=re.compile(regex_promotion)
        self.re_compile_detail=re.compile(regex_detail)
        self.re_compile_mobile_discount=re.compile(regex_mobile_discount)
        self.re_compile_stock=re.compile(regex_stock)
        self.re_compile_province=re.compile(regex_province)
        self.re_compile_city=re.compile(regex_city)
        self.re_compile_county=re.compile(regex_county)


    def load_html(self):
        try:
            self.page=urllib.request.urlopen(self.url)
        except Exception as e:
            print(str(e))
            beep()
            print(time.ctime())
            print("无法下载网页。1秒后重试...")
            time.sleep(1)
            self.load_html()
            return None
        self.html=self.page.read()
        self.page.close()

    def _parse_content(self,re_compile_obj):
        """get content according to each compiled obj that passed in."""
        found=re.findall(re_compile_obj,self.html.decode("utf-8"))
        try:
            return re.sub('<.*?>', '', found[0])
        except IndexError:
            if DEBUG:
                date_time = time.strftime("%Y%m%d_%H%M%S",time.localtime())
                html_file = open("jingdong_错误_未找到信息_%s.html"%date_time,"wb")
                html_file.write(self.html)
                html_file.close()
            return None
    def get_title(self):
        title = self._parse_content(self.re_compile_title)
        if title == None:
            return "无标题"
        else:
            return title.strip()
    def get_price(self):
        try:
            return float(self._parse_content(self.re_compile_price))
        except TypeError:
            beep()
            print("无法获取价格...")
            time.sleep(4)
            return MAX_PRICE

    def get_detail(self):
        detail = self._parse_content(self.re_compile_detail)
        if detail == None:
            return "无描述"
        else:
            return detail.strip()

    def get_promotion(self):
        promotion = self._parse_content(self.re_compile_promotion)
        if promotion == None:
            return "无促销"
        else:
            return promotion.strip()

    def get_mobile_discount(self):
        mobile_discount = self._parse_content(self.re_compile_mobile_discount)
        if mobile_discount == None:
            return "无手机端优惠"
        else:
            return mobile_discount.strip()

    def get_coupon(self):
        """Use post method to query whether there is a coupon."""
        #Communication procedure seen on httptrace extension in Chrome.
        headers = {"Connection": "keep-alive", "Content-Type": "application/x-www-form-urlencoded"}
        req = urllib.request.Request(url = 'http://item.m.jd.com/coupon/coupon.json', data = bytes("wareId=%s"%self.id_i, "ascii"), headers = headers, method = "POST")
        response = urllib.request.urlopen(req)

        try:
            #Escape the " for eval use.
            content = json.loads(response.read().decode("utf-8"))["coupon"].replace("true", "\"true\"").replace("false", "\"false\"")
        except KeyError:
        	content = ""
        response.close()
        content = ast.literal_eval(content)
        coupon_text = ""
        if not content:
            return "无券"
        for coupon in content:
            coupon_text = coupon_text+str(coupon["discount"])+"满"+str(coupon["quota"])+coupon["name"]+"____"

        return coupon_text.strip()


    def get_stock_status(self):
        stock = self._parse_content(self.re_compile_stock)
        if stock == None:
            return "无货"
        elif stock == "该地":
            return "不送"
        else:
            return stock.strip()

    def get_address(self):
        #Address shown on Jingdong goods page. Can be different from the address setted in setting file if setted wrong.
        try:
            address = self._parse_content(self.re_compile_province)+\
                      self._parse_content(self.re_compile_city)+\
                      self._parse_content(self.re_compile_county)
        except TypeError:
            # unsupported operand type(s) for +: 'NoneType' and 'NoneType'
            address = ""
        return address.strip()

class Result:
    """
    Read/save goods info from/to jingdong_crawler_result.txt.
    """
    def __init__(self):
        self._read_ini()

    def _read_ini(self):
        self.config = configparser.RawConfigParser()
        self.config.read('jingdong_crawler_result.txt')

    def get_url(self, good_id):
        try:
            return self.config.get(good_id, 'url')
        except Exception as e:
            print(str(e))
            return ''

    def set_url(self, good_id, _str):
        string = str(_str)
        with open('jingdong_crawler_result.txt', 'w') as configfile:
            if not self.config.has_section(good_id): self.config.add_section(good_id)
            self.config.set(good_id, 'url', string)
            self.config.write(configfile)


    def get_prev_title(self, good_id):
        try:
            return self.config.get(good_id, 'name')
        except Exception as e:
            print(str(e))
            return '无法读取标题'

    def set_prev_title(self, good_id, _str):
        string = str(_str)
        with open('jingdong_crawler_result.txt', 'w') as configfile:
            if not self.config.has_section(good_id): self.config.add_section(good_id)
            self.config.set(good_id, 'name', string)
            self.config.write(configfile)

    def get_prev_price(self, good_id):
        try:
            return float(self.config.get(good_id, 'price'))
        except Exception as e:
            print(str(e))
            return MAX_PRICE

    def set_prev_price(self, good_id, num):
        string = str(num)
        with open('jingdong_crawler_result.txt', 'w') as configfile:
            if not self.config.has_section(good_id):
                self.config.add_section(good_id)
            self.config.set(good_id, 'price', string)
            self.config.write(configfile)
    def get_prev_stock(self, good_id):
        try:
            return self.config.get(good_id, 'stock')
        except Exception as e:
            print(str(e))
            return '无法读取库存'

    def set_prev_stock(self, good_id, string):
        with open('jingdong_crawler_result.txt', 'w') as configfile:
            if not self.config.has_section(good_id):
                self.config.add_section(good_id)
            self.config.set(good_id, 'stock', string)
            self.config.write(configfile)
    def get_prev_promo(self, good_id):
        try:
            return self.config.get(good_id, 'promotion')
        except Exception as e:
            print(str(e))
            return '无法读取促销信息'

    def set_prev_promo(self, good_id, string):
        with open('jingdong_crawler_result.txt', 'w') as configfile:
            if not self.config.has_section(good_id):
                self.config.add_section(good_id)
            self.config.set(good_id, 'promotion', string)
            self.config.write(configfile)
            
    def get_prev_detail(self, good_id):
        try:
            return self.config.get(good_id, 'detail')
        except Exception as e:
            print(str(e))
            return '无法读取描述'

    def set_prev_detail(self, good_id, string):
        with open('jingdong_crawler_result.txt', 'w') as configfile:
            if not self.config.has_section(good_id):
                self.config.add_section(good_id)
            self.config.set(good_id, 'detail', string)
            self.config.write(configfile)


    def get_min_price(self, good_id):
        try:
            return float(self.config.get(good_id, 'min_price'))
        except Exception as e:
            print(str(e))
            return MAX_PRICE

    def set_min_price(self, good_id, num):
        string = str(num)
        with open('jingdong_crawler_result.txt', 'w') as configfile:
            if not self.config.has_section(good_id):
                self.config.add_section(good_id)
            self.config.set(good_id, 'min_price', string)
            self.config.write(configfile)

    def get_prev_mobi(self, good_id):
        try:
            return self.config.get(good_id, 'mobi')
        except Exception as e:
            print(str(e))
            return '无法读取手机促销信息'

    def set_prev_mobi(self, good_id, string):
        with open('jingdong_crawler_result.txt', 'w') as configfile:
            if not self.config.has_section(good_id):
                self.config.add_section(good_id)
            self.config.set(good_id, 'mobi', string)
            self.config.write(configfile)

    def get_prev_coupon(self, good_id):
        try:
            return self.config.get(good_id, 'coupon')
        except Exception as e:
            print(str(e))
            return '无法读取本地优惠券信息'

    def set_prev_coupon(self, good_id, string):
        with open('jingdong_crawler_result.txt', 'w') as configfile:
            if not self.config.has_section(good_id):
                self.config.add_section(good_id)
            self.config.set(good_id, 'coupon', string)
            self.config.write(configfile)

def internet_on():
    """Check if computer is online. Return type: boolean."""
    try:
        response=urllib.request.urlopen("http://www.baidu.com",timeout=100)
        return True
    except Exception as e:
        print(str(e))
        return False

def send_mail(sub,content,to_list=RECEIVER_EMAIL_ACCOUNTS):
    mail_host=SENDER_MAIL_SERVER
    mail_user=SENDER_EMAIL_ACCOUNT #用户名
    mail_pass=SENDER_EMAIL_PASSWD #口令

    me=mail_user
    msg = MIMEText(content,_subtype='plain',_charset='UTF-8')
    msg['Subject'] = sub
    msg['From'] = me
    msg['To'] = ";".join(to_list)
    try:
        server = smtplib.SMTP()
        server.connect(mail_host)
        server.login(mail_user,mail_pass)
        server.sendmail(me, to_list, msg.as_string())
        server.close()
        print("邮件发送成功！")
        return True
    except Exception as e:
        print(str(e))
        print("正在检查网络连接...")
        if True==internet_on():
            print("网络畅通，或许账号或密码有误。程序终止以避免频繁尝试登陆邮箱。")
            raise NameError("账号密码有误，请检查。")
        else:
            print("网络故障，稍后重试...")
            return False

def Run():
    #Counting querying times.
    count=0
    #JD goods id.
    ID=re.findall(r"/([\d]+).ht", MONITORING_ADDR)
    ID=list(tuple(ID))
    while(True):
        #Endless querying with sleep interval, until user quit the program.
        count+=1
        #Sum up all changes in a single query and print at the end of the prompt.
        change_print=""
        #Introduce randomness to simulate human clicking. Avoiding IP ban from jingdong.
        random.shuffle(ID)
        #For each link setted in file.
        for id_i in ID:
            time.sleep(random.randint(100,200)/1000)
            url_i = "http://item.m.jd.com/product/"+id_i+".html?provinceId=%d&cityId=%d&countyId=%d"%(PROVINCEID, CITYID, COUNTYID)
            print("++++++++++++++++++++++++++++++++++++++++++++++++++++")

            product=Product(id_i)

            result=Result()
            prev_url=result.get_url(id_i)
            prev_price=result.get_prev_price(id_i)
            prev_title=result.get_prev_title(id_i)
            prev_promo=result.get_prev_promo(id_i)
            prev_detail=result.get_prev_detail(id_i)
            prev_mobi=result.get_prev_mobi(id_i)
            prev_stock=result.get_prev_stock(id_i)
            prev_coupon=result.get_prev_coupon(id_i)
            minium_price=result.get_min_price(id_i)
            news_type=""
            product.load_html()

            curr_price=product.get_price()
            curr_title=product.get_title()
            curr_promo=product.get_promotion()
            curr_detail=product.get_detail()
            curr_mobi=product.get_mobile_discount()
            curr_stock=product.get_stock_status()
            curr_coupon=product.get_coupon()
            address = product.get_address()


            #save url to file if url not saved:
            if prev_url!=url_i:
                result.set_url(id_i, url_i)
            #record minium price：
            if curr_price<minium_price:
                #update minium price to file.
                minium_price=curr_price
                result.set_min_price(id_i, minium_price)



            ########################################################
            #title changed：
            if curr_title!=prev_title:
                news_type=""       #"题"
                print("标题！")
                change_print+=url_i+"\n"+curr_title[0:10]+": "+curr_title+"\n\n"
                result.set_prev_title(id_i, curr_title)

            ########################################################
            #discription changed：
            if curr_detail!=prev_detail:
                if QUERY_DETAIL:
                    news_type="描"
                print("描述！")
                change_print+=url_i+"\n"+curr_title[0:10]+": "+curr_detail+"\n\n"
                result.set_prev_detail(id_i, curr_detail)

            ########################################################
            #stock status：
            if curr_stock!=prev_stock and curr_stock == "有货":
                if QUERY_STOCK:
                    news_type="货"
                print("库存变化！")
                change_print+=url_i+"\n"+curr_title[0:10]+": "+curr_stock+"\n\n"
            if curr_stock!=prev_stock:
                result.set_prev_stock(id_i, curr_stock)

            ########################################################
            #promotion：
            if curr_promo!=prev_promo:
                if QUERY_PROMOTION:
                    news_type="活"
                print("活动！")
                #print(curr_promo.encode("utf-8"))
                #print(prev_promo.encode("utf-8"))
                change_print+=url_i+"\n"+curr_title[0:10]+": "+curr_promo+"\n\n"
                result.set_prev_promo(id_i, curr_promo)
            ########################################################
            #coupon censor：
            if curr_coupon!=prev_coupon and curr_coupon != "无券":
                if QUERY_COUPON:
                    news_type="券"
                print("优惠券！")
                change_print+=url_i+"\n"+curr_title[0:10]+": "+curr_coupon+"\n\n"
            if curr_coupon!=prev_coupon:
                result.set_prev_coupon(id_i, curr_coupon)
            ########################################################
            #mobile or jd_app price：
            if curr_mobi!=prev_mobi:
                #print(bytes(curr_mobi, "utf-8"))
                #print(bytes(prev_mobi, "utf-8"))
                if QUERY_MOBI:
                    news_type="移"
                print("移动端！")
                change_print+=url_i+"\n"+curr_title[0:10]+": "+curr_mobi+"\n\n"
                result.set_prev_mobi(id_i, curr_mobi)

            ########################################################
            #price drop：
            if curr_price<prev_price:
                print(prev_price)
                print(curr_price)
                if QUERY_PRICE:
                    news_type="降"
                print("降！ %.1f"%(prev_price-curr_price))
                change_print+=url_i+"\n"+curr_title[0:10]+": "+str(curr_price)+"降！ %.1f"%(prev_price-curr_price)+"\n\n"
            if curr_price!=prev_price:
                result.set_prev_price(id_i, curr_price)

            #detection finished.
            ########################################################

            message = u"地址      ："+address+"\n"+          \
                      u"物品      ："+curr_title+"\n"+       \
                      u"描述      ："+curr_detail+"\n"+      \
                      u"现价      ："+str(curr_price)+"\n"+  \
                      u"移动端价格："+str(curr_mobi)+"\n"+   \
                      u"有货否    ："+curr_stock+"\n"+       \
                      u"活动      ："+curr_promo+"\n"+       \
                      u"优惠券    ："+curr_coupon+"\n"       \
                      u"曾经最低价："+str(minium_price)+"\n" \
                      u"网址      ："+url_i+"\n"

            if news_type:
                print("检测到变更！！！")
                if SEND_EMAIL:
                    #Try 10 times if unabled to send email.
                    for i in range(10):
                        if send_mail("%s%d%s"%(news_type,curr_price,curr_title), message):
                            news_type=""
                            break;
                        else:
                            beep()
                            print("无法发送。30秒后重试...")
                            time.sleep(30)

                if PLAY_MUSIC:
                    webbrowser.open(MUSIC_PATH)

            else:
                print("无变更。")
            print(message)

        print("##############################################################")
        #print out current time.
        print(time.ctime())
        print("第"+str(count)+"次 汇总结果：")
        if ""==change_print:
            print("无变更。")
        else:
            print(change_print)
        #Randomness added to sleep interval, simulating human clicking and refreshing.
        RAND_INT = random.randint(-5,5)
        SLEEP_INTERVAL_RANDOM=int(SLEEP_INTERVAL+RAND_INT)
        if SLEEP_INTERVAL_RANDOM < 1:
            SLEEP_INTERVAL_RANDOM=1

        print("等待 %d+%d=%d秒 更新..."%(SLEEP_INTERVAL, RAND_INT, SLEEP_INTERVAL_RANDOM))
        print("如数字不跳动，请按ESC来退出选择模式。")
        #Countdown shown on the same position on prompt.
        count_length = len(str(SLEEP_INTERVAL_RANDOM))
        for i in range(SLEEP_INTERVAL_RANDOM,0,-1):
            sys.stdout.write(str(i)+" "+"\r")
            time.sleep(1)
            sys.stdout.flush()
            
        print("正在获取网页...\n\n")






if __name__ == '__main__':
    while True:
        try:
            Run()
        except Exception as e:
            print(e)
            beep()
            time.sleep(5)


'''
#Price: another way to obtain
import requests
pids=1217524
url="http://p.3.cn/prices/mgets?skuIds=J_1217524"# + str(pids)

ret=requests.get(url)
print(ret)
print(ret.content)
'''


r'''
HACK:
ConfigParser, SafeConfigParser and RawConfigParser react with the no escaped "%" differently:
invalid interpolation syntax in '【北京市家电节能补贴 最高补贴13%！】' at position 17
Traceback (most recent call last):
ValueError: invalid interpolation syntax in '【北京市家电节能补贴 最高补贴13%！】' at position 17

'''