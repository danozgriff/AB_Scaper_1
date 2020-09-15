import scraperwiki
import mechanize
import cookielib
import re
from bs4 import BeautifulSoup
from datetime import datetime, date, time
# generate random integer values
import time    
from random import seed, randint
import pytz


au_tz = pytz.timezone('Australia/Perth')
dtstart = datetime.now(tz=au_tz).strftime("%Y-%m-%d %H:%M:%S")
dtend = None
eoddate = None

scraperwiki.sqlite.execute("drop table if exists RunHistory")  
scraperwiki.sqlite.execute("create table RunHistory (`Start_DateTime` string NOT NULL, `End_DateTime` string, `Company_EOD_Date` string, UNIQUE (`Start_DateTime`, `Company_EOD_Date`))")

#if 1==1:
#
#    scraperwiki.sqlite.execute("insert or replace into RunHistory values (?, ?, ?)",  [dtstart, dtend, eoddate]) 
#    scraperwiki.sqlite.commit() 

if 1==1:

    url = 'https://www.marketindex.com.au/asx-listed-companies'
    br = mechanize.Browser()
    cj = cookielib.LWPCookieJar()
    br.set_cookiejar(cj)
    br.set_handle_equiv(True)
    br.set_handle_redirect(True)
    br.set_handle_robots(False)
    br.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)
        # sometimes the server is sensitive to this information
    br.addheaders = [('User-agent','Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1500.72 Safari/537.36')]



    scraperwiki.sqlite.execute("drop table if exists company")  
    scraperwiki.sqlite.execute("create table company (`Rank` integer, `Code` string NOT NULL, `Company` string, `Price` real, `Change` real, `Perc_Change` real, `Perc_Change_1_Year` real, `Market_Cap` integer, `EOD_Date` string NOT NULL, UNIQUE (`Code`, `EOD_Date`))")
    #scraperwiki.sqlite.execute("delete from company")  


    page = br.open(url)
    htmlcontent = page.read()
    soup = BeautifulSoup(htmlcontent, features="lxml")


    eoddate = soup.findAll("div", {"class": "header-timestamp"})[0].text[-11:].replace(" ", "-")
    date_obj = datetime.strptime(eoddate, '%d-%b-%Y')
    eoddate = date_obj.strftime('%Y-%m-%d')
    #eoddateint = int(date_obj.strftime('%Y%m%d'))

    table = soup.find( "table", {"id":"asx_sp_table"} )

    output_rows = []
    for table_row in table.findAll('tr'):
        columns = table_row.findAll('td')
        output_row = []
        for column in columns:
            output_row.append(column.text + ",")
        output_rows.append(output_row)
        

    for sublst in output_rows:
        if len(sublst) > 0:
            rank = sublst[0].replace(",", "")
            code = sublst[2].replace(",", "") 
            company = sublst[3].replace(",", "") 
            price = sublst[4].replace(",", "").replace("$", "") 
            change = sublst[5].replace(",", "").replace("+", "")
            perchg = round(float(sublst[6].replace(",", "").replace("+", "").replace("%", "").strip('"'))/100.0, 4)                                                                                                   
            yrperchg = round(float(sublst[8].replace(",", "").replace("+", "").replace("%", "").strip('"'))/100.0, 4)                                                                                                 
            marketcap = sublst[7].replace(",", "").replace("$", "").replace(".", "").replace(" B", "0000000").replace(" M", "0000").replace(" TH", "0")    
            
            scraperwiki.sqlite.execute("insert or ignore into company values (?, ?, ?, ?, ?, ?, ?, ?, ?)",  [rank, code, company, price, change, perchg, yrperchg, marketcap, eoddate]) 

    scraperwiki.sqlite.commit()  




if 1==1:

    dtend = datetime.now(tz=au_tz).strftime("%Y-%m-%d %H:%M:%S")
     
    scraperwiki.sqlite.execute("insert into RunHistory values (?, ?, ?)",  [dtstart, dtend, eoddate]) 
    #scraperwiki.sqlite.execute("insert or replace into RunHistory values (?, ?, ?)",  [dtstart, dtend, eoddate1])     
    scraperwiki.sqlite.commit() 
    
