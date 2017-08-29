import MySQLdb, sys, re, pprint, csv
from dotenv import load_dotenv, find_dotenv
import os

''' Find product posts that are published but out-of-stock, and set them to draft.
Brute Force:
    - find all product posts
    - if simple product ...
        ...check stock, and change to outofstock & draft if needed
    - if variable product ...
        ...list up all children,
        ...count each stock
        ...if count is 0, change to outofstock & draft
'''


isVerbose = False #global variable, used in debugPrint()
oosProducts = list()
productsChanged = 0


def main():
    # check verbosity flag
    global isVerbose, productsChanged, oosProducts
    if len(sys.argv) == 2 and (sys.argv[1] == 'v' or sys.argv[1] == '-v'):
        isVerbose = True
    # get credentials from dotenv
    load_dotenv(find_dotenv())
    DB_USER = os.environ.get('DB_USER')
    DB_PW = os.environ.get('DB_PW')
    DB_NAME = os.environ.get('DB_NAME')
    # open mysql db connection
    db = MySQLdb.connect(user=DB_USER,passwd=DB_PW,db=DB_NAME)
    cnx = db.cursor()
    # get a list of published parent product posts
    product_ids = getAllProducts(cnx)
    # check data
    for pid in product_ids:
        assert len(pid) == 2 and type(pid) == type(()) #i.e. len:1 and tuple
        debugPrint(pid) #e.g. (76864,)
        pid = pid[0]
        cnx.execute(queryForChildProducts(pid))
        children = cnx.fetchall()
        if len(children) == 0:
            processSimpleProduct(cnx,pid)
        else:
            processVariableProduct(cnx,pid,children)
    # exit procedures
    db.close()
    # print list of out of stock products to display
    print(f'\n--\nOut Of Stock Products\n--')
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(oosProducts)
    print('\n--')
    # print general overall stats
    print(f'\n--\nTotal Products Changed: {productsChanged}\n--\n')
    # output to csv file
    with open('results.csv', 'w') as f:
        writer = csv.writer(f)
        for row in oosProducts:
            writer.writerow(row)


def processVariableProduct(cnx,pid,children):
    ''' Iterate through child variations and check for validity
    Tally _stock; check _stock_status, _manage_stock
    Depending on condition, un-publish parent post '''
    global productsChanged, oosProducts
    debugPrint("\tNeed to process a variable product")
    # check parent post condition; should be NOT managed & stock 0
    cnx.execute(queryManageStock(pid))
    parent_manage_stock = cnx.fetchall()
    parent_manage_stock = parent_manage_stock[0][0]
    if parent_manage_stock == 'yes':
        setManageStock(cnx,pid,'no')
    # make sure each child variation are set correctly
    tally = 0
    for child in children:
        debugPrint(f'\tchild post: {child}')
        # TODO: enable/disable child products
        child = child[0] # before:(77717,) after:77717
        cnx.execute(queryStockCount(child))
        stock = cnx.fetchall()
        if len(stock)==0: # some data are null/empty
            stock = 0
        else:
            stock = int(float(stock[0][0])) # before:(('3',),)
        debugPrint(f'\tchild post {child} has stock qty: {stock}')
        tally += stock
    debugPrint(f'\t\tparent post {pid} has total stock: {tally}')
    if tally == 0:
        productsChanged += 1
        sku = getSKU(cnx,pid)
        post_title = getPostTitle(cnx,pid)
        post_link = getLink(pid)
        oosProducts.append([sku,post_title,post_link])
        #set product to draft
        setStockStatus(cnx,pid,'outofstock')
        debugPrint(f'\t\t{pid}: set stock_status to outofstock')
        setPostStatus(cnx,pid,'draft')
        debugPrint(f'\t\t{pid}: set post_status to draft')


def processSimpleProduct(cnx,pid):
    ''' Check product integrity: _stock, _stock_status, _manage_stock, post_status
        - how much _stock do i have of this item?
        - is _stock_status in proper state?
        - is manage_stock in proper state?
        - is post_status correct?
    '''
    global productsChanged
    debugPrint("\tNeed to process a simple product")
    # check _stock flag
    cnx.execute(queryStockCount(pid))
    stock_qty = cnx.fetchall() #dirty data, tuple in tuple; e.g. (('5',),)
    stock_qty = stoi(stock_qty[0][0])
    # check _stock_status flag
    cnx.execute(queryStockStatus(pid))
    stock_status = cnx.fetchall() #dirty data, nested tuple; e.g. (('outofstock',),)
    stock_status = stock_status[0][0]
    # check _manage_stock flag
    cnx.execute(queryManageStock(pid)) # ""; e.g. (('yes',),)
    manage_stock = cnx.fetchall()
    manage_stock = manage_stock[0][0]
    # check post_status flag
    cnx.execute(queryPostStatus(pid))
    post_status = cnx.fetchall() #dirty data, nested tuple; e.g. (('publish',),)
    post_status = post_status[0][0]
    debugPrint(f'\tpost_id: {pid} \n\tstock_status: {stock_status} \n\tmanage_stock: {manage_stock} \n\tpost_satus: {post_status}')
    if manage_stock != 'yes':
        setManageStock(cnx,pid,'yes')
        debugPrint(f'\t\t{pid}: set manage_stock from {manage_stock} to yes')
    if stock_qty <= 0:
        productsChanged += 1
        sku = getSKU(cnx,pid)
        post_title = getPostTitle(cnx,pid)
        post_link = getLink(pid)
        oosProducts.append([sku,post_title,post_link])
        if stock_status != 'outofstock':
            setStockStatus(cnx,pid,'outofstock')
            debugPrint(f'\t\t{pid}: set stock_status from {stock_status} to outofstock')
        if post_status == 'publish':
            setPostStatus(cnx,pid,'draft')
            debugPrint(f'\t\t{pid}: set post_status from {post_status} to draft')


def getSKU(cnx,pid):
    ''' Retrieve post's SKU number '''
    query = f'''
SELECT meta_value
FROM wp_postmeta
WHERE post_id = '{pid}'
    AND meta_key = '_sku'
;'''
    cnx.execute(query)
    sku = cnx.fetchall()
    sku = sku[0][0]
    return sku


def getPostTitle(cnx,pid):
    ''' Retrive post's product title '''
    query = f'''
SELECT post_title
FROM wp_posts
WHERE id = {pid}
;'''
    cnx.execute(query)
    title = cnx.fetchall()
    title = title[0][0]
    return title


def getLink(pid):
    return f'http://www.sousouus.com/wp-admin/post.php?post={pid}&action=edit'

def setPostStatus(cnx,pid,status):
    ''' TODO: set post_status to 'draft' '''


def setManageStock(cnx,pid,meta_value):
    ''' TODO: set _manage_stock to 'yes' '''


def setStockStatus(cnx,pid,stock_status):
    ''' TODO: set _stock_status to 'outofstock' '''


def queryPostStatus(pid):
    query = f'''
SELECT post_status
FROM wp_posts
WHERE id = {pid}
;'''
    return query


def queryManageStock(pid):
    query = f'''
SELECT meta_value
FROM wp_postmeta
WHERE meta_key = '_manage_stock'
    AND post_id = {pid}
;'''
    return query


def queryStockStatus(pid):
    query = f'''
SELECT meta_value
FROM wp_postmeta
WHERE meta_key = '_stock_status'
    AND post_id = {pid}
;'''
    return query


def stoi(string):
    ''' Clean dirty data, from string to integer '''
    string = re.sub(r'\s+', '', string, flags=re.UNICODE)
    string = 0 if len(string)==0 else string
    return int(float(string))

def queryStockCount(pid):
    query = f'''
SELECT meta_value
FROM wp_postmeta
WHERE meta_key = '_stock'
    AND post_id = {pid}
;'''
    return query


def queryForChildProducts(pid):
    query = f'''
SELECT id
FROM wp_posts
WHERE post_parent = {pid}
    AND post_type = 'product_variation'
;'''
    return query


def getAllProducts(cnx):
    ''' Fetch a list of all parent product posts '''
    products = list()
    cnx.execute(queryForAllProducts())
    products = cnx.fetchall() # returns a list of len:1 tules
    return products


def queryForAllProducts():
    query = '''
SELECT id, post_title
FROM wp_posts
WHERE post_status = 'publish'
    AND post_type = 'product'
;'''
    return query


def debugPrint(s):
    if isVerbose:
        print(s)


'''
------------------------
        Resources:
------------------------

Dealing with whitespaces:
    --
    https://stackoverflow.com/a/28607213
    --
    If you also want to remove all the other strange whitespace
    characters that exist in unicode you can use re.sub with the
    re.UNICODE arguement:

        sentence = re.sub(r"\s+", "", sentence, flags=re.UNICODE)

    ... because do you really want to keep these strange unicode characters?


    --
    https://stackoverflow.com/a/8270124
    --
    or a regular expression:

    import re
    pattern = re.compile(r'\s+')
    sentence = re.sub(pattern, '', sentence)

'''
if __name__=="__main__": main()
