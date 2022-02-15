from os import TMP_MAX
import requests
import re
from bs4 import BeautifulSoup as bs
import FilrougeMLIOLibrary as MLOI
import zlib as zl


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

def ourGet(BaseURL,DetailURL,abortonerror=False,ListURL=[]):
    import pickle
    import os
    URL = BaseURL+DetailURL
    if URL not in ListURL:
        ListURL.append(URL)
        nomfic = DetailURL.replace('/','_')+'.tmp'
        if os.path.isfile(nomfic):
            with open(nomfic,'rb') as f:
                r=pickle.load(f)
                
        else:
            try:
                r = requests.get(URL)
                r.raise_for_status()
            except requests.exceptions.RequestException as err:
                print("ERREUR pour URL",URL,err)        
                #print(URL,f"Status code: {r.status_code}")
                if abortonerror:
                    exit()
                return('')
            #line_compress=bytes()
            #line_compress = zl.compress ( bytes(r.text))
            #nomfic = base64.b64encode(URL)+'.tmp'
            
            with open(nomfic,'wb') as f:
                pickle.dump(r,f)

        return(bs(r.text, 'html.parser'))
    else:
        return('')


def PrepSaveArticle(dictres,DetailURL,LibWeb,df):
    #df.info()
    if ('DOI' in dictres) and len(dictres['DOI'])>0:
        DOI = dictres['DOI'][0]
        DOI = DOI.replace(' ','')
    else:
        DOI = 'PMID'+dictres['PMID'][0]
    Title = dictres['Title']
    AName=dictres['Authors']
    AOrganization=dictres['OrgAuthors']
    AUrl=dictres['urlAuthors']
    Authors= {'Name':AName,'Organization':AOrganization,'URL':AUrl,'LibWeb':LibWeb}
    Abstract = dictres['Abstract']
    if ('DatePub' in dictres) and len(dictres['DatePub']) > 0:
        DatePub = dictres['DatePub'][0]
        DatePub = DatePub.replace('Epub ','')
        DatePub = DatePub.replace('.','')
    else:
        DatePub = ''
    RefBy=dictres['RefBy']

    MLOI.AddArticles(DOI,df,Title,Abstract,'','',Authors,'',DatePub,DetailURL,LibWeb)
    global nbArt
    if (nbArt % 10 == 0):
        global dirname,fname
        MLOI.SaveArticles(dirname,fname,df)

def followtree(dictres,wkey,LibWeb,BaseURL,Scrapdicts,maxdepth,depth,df):
    if (wkey in dictres):
        depth+=1
        for urlref in dictres[wkey]:         
            scrapArticle(df,LibWeb,BaseURL,urlref,Scrapdicts,maxdepth,depth)


Scrapdicts = {'PubMed':{
    'DatePub':{'tag':'span','args':{'class': "secondary-date"}},
    'DOI':{'tag':'span','args':{'class': "citation-doi"}},
    'PMID':{'tag':'span','args':{'class': "identifier pubmed"},'tag2':'strong','args2':{'title': "PubMed ID"}},
    'Title':{'tag':'h1'},
    'Abstract':{'tag':'div','args':{'class': "abstract-content selected"}},
    'Authors':{'multi':True,'tag':'span','args':{'class': "authors-list-item"},'tag2':'a','args2':{'class': "full-name"},'ctner':'data-ga-label'},
    'OrgAuthors':{'multi':True,'tag':'span','args':{'class': "authors-list-item"},'tag2':'a','args2':{'class': "affiliation-link"},'ctner':'title'},    
    'urlAuthors':{'multi':True,'tag':'span','args':{'class': "authors-list-item"},'tag2':'a','args2':{'class': "full-name"},'ctner':'href'},
    'RefBy':{'multi':True,'tag':'div','args':{'class': "docsum-content"},'tag2':'a','args2':{'data-ga-category': "cited_by"},'ctner':'href'}, 
    'Similar':{'multi':True,'tag':'div','args':{'class': "docsum-content"},'tag2':'a','args2':{'data-ga-category': "similar_article"},'ctner':'href'},  
    }}
Scrapref = {'PubMed':{
    'RefTo':{'multi':True,'tag':'ol','args':{'class': "references-list"},'tag2':'a','args2':{'data-ga-action': re.compile(r"^[1-9]{8}$")},'ctner':'href'} 
    }}

def scrap(Scrapdict,BaseURL,DetailURL,dictres):
    html_paper = ourGet(BaseURL,DetailURL,True)
    filled = len(html_paper)
    if filled :
        #print(html_paper)       
        for ktopic,vtopic in Scrapdict.items():
            res = []
            resfa = []
            args = fmtargs(vtopic,'args')
            #print(ktopic,vtopic,args)
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
    return(filled)



#DOI,df=None,Title='',Abstract='',Body='',RefTo='',Authors='',RefBy='',DatePub='',url='',LibName=''):
def scrapArticle(df,LibWeb,BaseURL,DetailURL,Scrapdicts,maxdepth=10,depth=0):
    from time import strftime
    from datetime import datetime
    if (depth<maxdepth):
        Scrapdict = Scrapdicts[LibWeb]
        dictres = dict()
        if scrap(Scrapdict,BaseURL,DetailURL,dictres):
            global nbArt
            nbArt +=1
            print(datetime.now(),'article #',nbArt,'Level',depth,dictres['Title'])
            PrepSaveArticle(dictres,DetailURL,LibWeb,df)
            followtree(dictres,'RefBy',LibWeb,BaseURL,Scrapdicts,maxdepth,depth,df)
            followtree(dictres,'Similar',LibWeb,BaseURL,Scrapdicts,maxdepth,depth,df)
            dictref={}
            scrap(Scrapref[LibWeb],BaseURL,DetailURL+'references/',dictref)
            followtree(dictref,'RefTo',LibWeb,BaseURL,Scrapdicts,maxdepth,depth,df)
            
        

#    'BaseURL':"https://pubmed.ncbi.nlm.nih.gov/",
BaseURL = "https://pubmed.ncbi.nlm.nih.gov"
DetailURL = "/32087349/"
maxdepth = 10
depth=0
global nbArt
nbArt = 0
global dirname,fname
dirname,fname = '',"art.json"

df = MLOI.LoadArticles(dirname,fname)
df.info()
scrapArticle(df,'PubMed',BaseURL,DetailURL,Scrapdicts,maxdepth,depth)   



