from __future__ import absolute_import
from ark_agent.celery import celery
from ark_agent.load_data import LoadMongoDB
from ark_agent.ark_logger import *
from celery.result import ResultSet
import sys
import ystockquote
import pprint
import finsymbols 
from time import sleep
from sets import Set
import httplib
import urllib2


def get_symbol_set(symbols):
    symbol_set = Set()
    for symbol in symbols:
        symbol_set.add(symbol['symbol'])
    return symbol_set

#@celery.task(rate_limit='15/m')
@celery.task()
def get_eod_data(symbol, start_date,end_date):

    #TODO consider retring task for 2 times   
    
    logger = QuantLogger.get_logger(__name__)
    logger.info("Obtaining %s from %s to %s" %(symbol,start_date,end_date))
    
    try:
        price_data = ystockquote.get_historical_prices(symbol,start_date,end_date) 
        return {'symbol':symbol,'data': price_data,'status':'success'}
    except urllib2.HTTPError,exc: 
        logger.error({'status':'failed','symbol':symbol,'msg':str(exc),'exception':'HTTPError'})
        return {'status':'failed','symbol':symbol,'msg':str(exc)}
    except urllib2.URLError,exc:
        logger.error({'status':'failed','symbol':symbol,'msg':str(exc),'exception':'URLError'})
        return {'status':'failed','symbol':symbol,'msg':str(exc)}
    except Exception, exc:
        logger.error({'status':'failed','symbol':symbol,'msg':str(exc),'exception':'Last'})
        return {'status':'failed','symbol':symbol,'msg':str(exc)}


@celery.task(ignore_result=True)
def generate_eod_tasks():
    """
    Task responsible for generating work items used to obtain end of day 
    data for stocks using get_eod_data() task
    """

    symbol_sets = Set()
    symbol_sets.add('GOOG')
    symbol_sets.add('MPG')
    symbol_sets.add('LAND')
    #Gets all symbols
    sp500 = finsymbols.get_sp500_symbols()
    #amex = finsymbols.get_amex_symbols()
    #nyse = finsymbols.get_nyse_symbols()
    #nasdaq = finsymbols.get_nasdaq_symbols()
    
    #Adds all symbols to set which removes duplicates
    #symbol_sets.update(get_symbol_set(sp500))
    #symbol_sets.update(get_symbol_set(amex))
    #symbol_sets.update(get_symbol_set(nyse))
    #symbol_sets.update(get_symbol_set(nasdaq))

    load_mongo = LoadMongoDB()
    
    result_ids = []
    for symbol in symbol_sets:
        #Obtain start and end dates from database
        date_range = load_mongo.get_date_range(symbol) 
        result_id = get_eod_data.apply_async((symbol,date_range['start_date'],date_range['end_date']))
        result_ids.append(result_id)

    
    result_data = ResultSet(result_ids)
    my_results = result_data.iterate()

    #Iterate over all results
    for data in my_results:
        if(data['status'] == 'success'):
            load_mongo.insert_to_db(data)
            load_mongo.set_last_load_date(data['symbol'],data['status'])
        elif(data['status'] == 'failed'):
            load_mongo.set_last_load_date(data['symbol'],data['status'])

    load_mongo.done()
