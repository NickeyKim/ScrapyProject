import scrapy
class AptTradeScrapy(scrapy.Item):

    apt_name = scrapy.Field()
    address_1 = scrapy.Field()
    address_2 = scrapy.Field()
    address_3 = scrapy.Field()
    address_4 = scrapy.Field()
    address = scrapy.Field()
    age = scrapy.Field()
    level = scrapy.Field()
    available_space = scrapy.Field()
    trade_date = scrapy.Field()
    trade_amount = scrapy.Field()

    def to_dict(self):  # convert to Dicationary structure
        return{
            '아파트': self['apt_name'],
            '시/도': self['address_1'],
            '군/구': self['address_2'],
            '동/읍면': self['address_3'],
            '번지': self['address_4'],
            '전체주소': self['address'],
            '연식': self['age'],
            '층': self['level'],
            '면적': self['available_space'],
            '거래일자': self['trade_date'],
            '매매가격': self['trade_amount'],
        }