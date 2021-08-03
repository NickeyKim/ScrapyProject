import datetime as dt
from urllib.parse import urlencode

import scrapy
from dateutil.relativedelta import relativedelta
from openpyxl import Workbook, load_workbook
from scrapy import Selector
from sqlalchemy import create_engine
import invest_crawler.consts as CONST
from invest_crawler.items.apt_trade import AptTradeScrapy

import pandas as pd

class TradeSpider(scrapy.spiders.XMLFeedSpider):
    name = 'trade' #Spider Name

    def start_requests(self):
        self.engine = create_engine('sqlite:///CRAWLER.DB', echo=False) # database connect
        date = dt.datetime(2017,7,1)
        Workbook().save('APT_TRADE.xlsx')
        yield from self.get_realestate_trade_data(date)
        #return the value of method and re-return
        
    def get_realestate_trade_data(self, date):  #the first logic when crawling starts
        page_num = 1
        urls = [
            CONST.APT_DETAIL_ENDPOINT   #Endpoint
        ]
        params = {
            "pageNo": str(page_num),
            "numOfRows": "999",
            "LAWD_CD": "11740",  #gang-dong gu
            "DEAL_YMD": date.strftime("%Y%m"),
        }
        for url in urls:
            url += urlencode(params)
            print(url)
            yield scrapy.Request(url=url, callback=self.parse_node, cb_kwargs=dict(page_num=page_num, date=date))
            #callback : Request response -> callback method, that argument is cb_kwargs

    def parse_node(self, response, page_num, date):  #Parse
#        print(response.body)
        selector = Selector(response, type='xml')
        items = selector.xpath('//%s' % self.itertag)
        if not items:
            return
        # # to Save Excel Sheet
        # apt_trades = [self.parse_item(item) for item in items]  # python LC(List Comprehension)
        # apt_dataframe = pd.DataFrame.from_records([apt_trade.to_dict() for apt_trade in apt_trades])
        # # using to_dict method, convert python object List -> DataFrame of Pandas

        # writer = pd.ExcelWriter('APT_TRADE.xlsx', engine = 'openpyxl', mode='a')  #ExcelWriter is Panda's method
        # apt_dataframe.to_excel(writer, sheet_name='서울-' + date.strftime("%Y%m"), index=False)
        # writer.save()
        # # saving dataframe as Excel

        apt_trades = [self.parse_item(item) for item in items]  # python LC(List Comprehension)
        apt_dataframe = pd.DataFrame.from_records([apt_trade.to_dict() for apt_trade in apt_trades])  
        # using to_dict method, convert python object List -> DataFrame of Pandas
        apt_dataframe.to_sql('APT_TRADE', con=self.engine, if_exists='append')
        # using to_sql method, save datafram to DB table

        date += relativedelta(months = 1)  # add month 1
        yield from self.get_realestate_trade_data(date)

#        for item in items:
#            apt_trade = self.parse_item(item)
#            print(apt_trade)

    def parse_item(self, item):  # parsing data in 'item'
        state = '서울시'
        district = '강동구'

        try:
            apt_trade_data = AptTradeScrapy(
                apt_name = item.xpath("./아파트/text()").get(),
                address_1=state,
                address_2=district,
                address_3= item.xpath("./법정동/text()").get(),
                address_4= item.xpath("./지번/text()").get(),
                address = state + " " + district + " " + item.xpath("./법정동/text()").get().strip() + " " + 
                    item.xpath("./지번/text()").get(),
                age = item.xpath("./건축년도/text()").get(),
                level = item.xpath("./층/text()").get(),
                available_space = item.xpath("./년/text()").get(),
                trade_date = item.xpath("./년/text()").get() + "/" +
                    item.xpath("./월/text()").get() + "/"+ 
                    item.xpath("./일/text()").get(),
                trade_amount = item.xpath("./거래금액/text()").get().strip().replace(',', ''),
            )
        except Exception as e:
            print(e)
            self.logger.error(item)
            self.logger.error(item.xpath("./아파트/text()").get())

        return apt_trade_data

      
