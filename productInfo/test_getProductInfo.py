#milestone29新增oversea, wechat, mycard, offline
import time
import json
import pytest
import ast
from assistence import api
from assistence import dbConnect
from pprint import pprint

py_mapping = {
    'android': 'iab',
    'ios': 'iap',
    'web': 'web',
    'oversea': 'oversea',
    'wechat': 'wechat',
    'mycard': 'mycard',
    'offline': 'remittance'
} 

testData = [
    ('查詢安卓的產品資訊', 'android'),
    ('查詢安卓的產品資訊', 'ios'),
    ('查詢安卓的產品資訊', 'web'),
    ('查詢安卓的產品資訊', 'oversea'),
    ('查詢安卓的產品資訊', 'wechat'),
    ('查詢安卓的產品資訊', 'mycard'),    
    ('查詢安卓的產品資訊', 'offline')
]

@pytest.mark.parametrize("scenario, platformName", testData)
def test_getProductInfo(scenario, platformName):
    sqlStr  = "select id, platforms, points, price, product_id, product_type, remark "
    sqlStr += "from product_info where status = 1 and production = 1 and product_type = '" + py_mapping[platformName] + "' order by points"
    dbResult = dbConnect.dbQuery('35.234.17.150', sqlStr)
    pprint(dbResult)
    header = {'Connection': 'Keep-alive'}
    apiNmae = '/api/v2/productInfo/' + platformName + '/enableList'
    res = api.apiFunction('http://35.234.17.150', header, apiNmae, 'get', None)
    resText = json.loads(res.text)
    assert res.status_code == 200
    assert len(dbResult) == len(resText['productInfos'])
    for i in range(len(dbResult)):
        assert dbResult[i][0] == resText['productInfos'][i]['id']
        assert ast.literal_eval(dbResult[i][1]) == resText['productInfos'][i]['platforms']
        assert dbResult[i][2] == resText['productInfos'][i]['points']
        assert int(dbResult[i][3]) == resText['productInfos'][i]['price']
        assert dbResult[i][4] == resText['productInfos'][i]['productId']
        assert dbResult[i][5] == resText['productInfos'][i]['productType']
        assert dbResult[i][6] == resText['productInfos'][i]['remark']