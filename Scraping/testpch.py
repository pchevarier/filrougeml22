import requests
import re
from bs4 import BeautifulSoup as bs
BaseURL = "https://pubmed.ncbi.nlm.nih.gov/"
DetailURL = "32087349/"

def fmtargs(adict,akey):
    if akey not in adict:
        args={}
    else:
        args = adict[akey]
    return(args)

def filtretext(mstr):
    mstr = re.sub(r'[\n]',r'',mstr)
    mstr = mstr.strip()
    return(mstr)

def ourGet(BaseURL,DetailURL,abortonerror=False):
    URL = BaseURL+DetailURL
    try:
        r = requests.get(URL)
        r.raise_for_status()
    except requests.exceptions.RequestException as err:
        print("ERREUR pour URL",URL,err)        
        #print(URL,f"Status code: {r.status_code}")
        if abortonerror:
            exit()
        return('')
    else:
        return(bs(r.text, 'html.parser'))

Scrapdicts = {'PubMed':{
    'BaseURL':"https://pubmed.ncbi.nlm.nih.gov/",
    'Title':{'tag':'h1'},
    'Abstract':{'tag':'div','args':{'class': "abstract-content selected"}},
    'Authors':{'multi':True,'tag':'span','args':{'class': "authors-list-item"},'tag2':'a','args2':{'class': "full-name"},'ctner':'data-ga-label'},
    'OrgAuthors':{'multi':True,'tag':'span','args':{'class': "authors-list-item"},'tag2':'a','args2':{'class': "affiliation-link"},'ctner':'title'},    
    'urlAuthors':{'multi':True,'tag':'span','args':{'class': "authors-list-item"},'tag2':'a','args2':{'class': "full-name"},'ctner':'href'}
    }}

def scrapArticle(LibWeb,DetailURL,Scrapdicts):
    
    Scrapdict = Scrapdicts[LibWeb]
    print(Scrapdict)
    html_paper = ourGet(Scrapdict['BaseURL'],DetailURL,True)

    for ktopic,vtopic in Scrapdict.items():
        res = []
        resfa = []
        args = fmtargs(vtopic,'args')
        if 'multi' in vtopic and vtopic['multi']:
            resfa=html_paper.find_all(vtopic['tag'],args)
            args2 = fmtargs(vtopic,'args2')
            for ligfa in resfa:
                res.append(ligfa.find(vtopic['tag2'],args2))
        else:   
            res.append(html_paper.find(vtopic['tag'],args))
        ret=[]
        for r in res:
            if r != None:
                rr = filtretext(r.text if 'ctner' not in vtopic else r[vtopic['ctner']])
                ret.append(rr)
        print('ktopic',ktopic,ret)

        #print(html_paper.find_all(v['tag'],v['args']).[ctner])

scrapArticle('PubMed',DetailURL,Scrapdicts)   



