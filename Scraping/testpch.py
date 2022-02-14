import requests
import re
from bs4 import BeautifulSoup as bs
import FilrougeMLIOLibrary as MLOI
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
    'DatePub':{'tag':'span','args':{'class': "secondary-date"}},
    'DOI':{'tag':'span','args':{'class': "citation-doi"}},
    'Title':{'tag':'h1'},
    'Abstract':{'tag':'div','args':{'class': "abstract-content selected"}},
    'Authors':{'multi':True,'tag':'span','args':{'class': "authors-list-item"},'tag2':'a','args2':{'class': "full-name"},'ctner':'data-ga-label'},
    'OrgAuthors':{'multi':True,'tag':'span','args':{'class': "authors-list-item"},'tag2':'a','args2':{'class': "affiliation-link"},'ctner':'title'},    
    'urlAuthors':{'multi':True,'tag':'span','args':{'class': "authors-list-item"},'tag2':'a','args2':{'class': "full-name"},'ctner':'href'},
    'RefBy':{'multi':True,'tag':'div','args':{'class': "docsum-content"},'tag2':'a','args2':{'data-ga-category': "cited_by"},'ctner':'href'},   
    }}
#DOI,df=None,Title='',Abstract='',Body='',RefTo='',Authors='',RefBy='',DatePub='',url='',LibName=''):
def scrapArticle(LibWeb,BaseURL,DetailURL,Scrapdicts):
    
    Scrapdict = Scrapdicts[LibWeb]
    html_paper = ourGet(BaseURL,DetailURL,True)
    dictres = dict()
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
        
        dictres[ktopic]=ret
        #print(html_paper.find_all(v['tag'],v['args']).[ctner])
    print(dictres)
    DOI = dictres['DOI'][0]
    DOI = DOI.replace(' ','')
    Title = dictres['Title']
    AName=dictres['Authors']
    AOrganization=dictres['OrgAuthors']
    AUrl=dictres['urlAuthors']
    Authors= {'Name':AName,'Organization':AOrganization,'URL':AUrl,'LibWeb':LibWeb}
    Abstract = dictres['Abstract']
    DatePub = dictres['DatePub'][0]
    DatePub = DatePub.replace('Epub ','')
    DatePub = DatePub.replace('.','')
    RefBy=dictres['RefBy']
    df = MLOI.AddArticles(DOI,None,Title,Abstract,'','',Authors,'',DatePub,DetailURL,LibWeb)
    MLOI.SaveArticles("","art.json",df)

#    'BaseURL':"https://pubmed.ncbi.nlm.nih.gov/",
scrapArticle('PubMed',BaseURL,DetailURL,Scrapdicts)   



