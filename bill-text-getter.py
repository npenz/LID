from urllib.request import urlopen
import json
import base64
from bs4 import BeautifulSoup

def writeBills():
    r = urlopen("https://api.legiscan.com/?key=e2408f4fb05eb81f6018aa3599a63847&op=getMasterList&state=CO).read().decode('utf-8')
    json_obj = json.loads(r)
    js = json_obj.get('masterlist')
    bill_id_list= []

    for item in js.values():
        try:
            bill_id_list.append(item.get('bill_id'))
        except KeyError:
            pass

    bills = getBills(bill_id_list)

    num = 1
    for bill in bills:

        #iterate to the bill key
        #get the doc_id to append to the API call
        try:
            bill_num = bill.get("bill").get("bill_number")
        except AttributeError:
            bill_num = "bill" + str(num)
        try:
            doc_id = bill.get("bill").get("texts")[0].get("doc_id")
        except AttributeError:
            pass

        #append the doc_id to the API call and convert results to unicode string
        searchId = urlopen('https://api.legiscan.com/?key=e2408f4fb05eb81f6018aa3599a63847&op=getBillText&id='+str(doc_id)).read().decode()

        #create json object with API data
        resultsId = json.loads(searchId)

        #iterate to the document object
        resultsId = resultsId.get('text').get('doc')

        #decode the MIME 64 encoded text
        decodedResults = base64.b64decode(resultsId)

        #once decoded, the text is in an HTML string, use bs4 to parse it
        bsObj2 = BeautifulSoup(decodedResults)
        for p in bsObj2.find_all('p'):
            if p.string:
                p.string.replace_with(p.string.strip())
        bsObj2.style.decompose()

        #strip white space, encode in ascii and remove non-printing characters
        htmlText = str(bsObj2.getText())

        #write each instance of htmlText to a unique file
        f = open("data/" + str(bill_num) + "_" + str(doc_id) + ".txt", "wb")
        f.write(htmlText.encode("ascii", errors="ignore"))
        f.close()
        num += 1

def getBills(bill_list):
    """use the list of ids to increment api billText"""
    complete_bill_list = []
    for i in bill_list:
        billUrl = urlopen("https://api.legiscan.com/?key=e2408f4fb05eb81f6018aa3599a63847&op=getBill&id="+str(i)).read().decode()
        json_obj = json.loads(billUrl)
        complete_bill_list.append(json_obj)

    return complete_bill_list

getBillId()
