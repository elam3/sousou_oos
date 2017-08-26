import MySQLdb, csv, json, pprint, datetime, sys

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

def main():
    db = MySQLdb.connect(user='sousouus',passwd='sousouus',db='sousouus')
    cnx = db.cursor()

    products = list()
    products = GetAllProducts(cnx)

    for product in products:
        print(product)

    # exit procedures
    db.close()


def GetAllProducts(cnx):
    ''' Fetch a list of all parent product posts '''
    products = list()
    query = GetAllProductsQuery()
    return products


def GetAllProductsQuery():
    query = '''
SELECT id
FROM wp_posts
WHERE post_status = 'publish'
    AND post_type = 'product';'''
    return query


if __name__=="__main__": main()
