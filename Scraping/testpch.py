from os import TMP_MAX
import requests
import re
from bs4 import BeautifulSoup as bs
import FilrougeMLIOLibrary as MLOI
import zlib as zl
cacheDir='cache/'

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

def ourGet(BaseURL,DetailURL,abortonerror=False,ListURL=[],nbretry=0):
    import pickle
    import os
    URL = BaseURL+DetailURL
    #print('listurl',ListURL)
    if URL not in ListURL:
        ListURL.append(URL)
        nomfic = DetailURL.replace('/','_')+'.tmp'
        nomfic = nomfic.replace('?','!')
        nomfic= cacheDir+nomfic
        
        if os.path.isfile(nomfic):
            with open(nomfic,'rb') as f:
                r=pickle.load(f)
                
        else:
            try:
                r = requests.get(URL)
                err=r.status_code
#                r.raise_for_status()
            #except requests.exceptions.RequestException as err:
            except:
                print("ERREUR pour URL",URL)        
                #print(URL,f"Status code: {r.status_code}")
                if nbretry <5:
                    import time
                    time.sleep(5)
                    nbretry +=1
                    return(ourGet(BaseURL,DetailURL,abortonerror,ListURL,nbretry))
                if abortonerror:
                    exit()
                return('')
                        
            with open(nomfic,'wb') as f:
                pickle.dump(r,f)

        return(bs(r.text, 'html.parser'))
    else:
        return('')

def Dict2Itm(idict,key,subskey='',sreplace=''):
    item=''
    if (key in idict) and len(idict[key])>0:
        if len(idict[key])==1:
            item = idict[key][0]
            if len(sreplace) > 0:
                item = item.replace(sreplace,'')
                idict[key][0] = item
        else:
            item=idict[key]
        
    if len(item)==0 and len(subskey)>0:
        item = Dict2Itm(idict,subskey,'',sreplace)
    return(item)

def PrepSaveArticle(dictres,DetailURL,LibWeb,df):
    #df.info()
    PMID = Dict2Itm(dictres,'PMID','',' ')
    PMCID = Dict2Itm(dictres,'PMCID','',' ')
    DOI = Dict2Itm(dictres,'DOI','PMID',' ')
    
    Title = Dict2Itm(dictres,'Title')
    AName=Dict2Itm(dictres,'Authors')
    AOrganization=Dict2Itm(dictres,'OrgAuthors')
    AUrl=Dict2Itm(dictres,'urlAuthors')
    Authors= {'Name':AName,'Organization':AOrganization,'URL':AUrl,'LibWeb':LibWeb}
    Abstract = Dict2Itm(dictres,'Abstract')
    Body = "".join(Dict2Itm(dictres,'Body'))
    if ('DatePub' in dictres) and len(dictres['DatePub']) > 0:
        DatePub = dictres['DatePub'][0]
        DatePub =DatePub.split(' ', 1)[0] 
    else:
        DatePub = ''
    RefBy=dictres['RefBy'] if 'RefBy' in dictres else ''
    RefTo=dictres['RefTo'] if 'RefTo' in dictres else '' 
    MLOI.AddArticles(DOI,df,Title,Abstract,Body,RefTo,Authors,RefBy,DatePub,DetailURL,LibWeb,PMID,PMCID)
    global nbArt
    if (nbArt % 10 == 0):
        global dirname,fname
        #print('sauv ',fname)
        MLOI.SaveArticles(dirname,fname,df)

def followtree(dictres,wkey,LibWeb,BaseURL,Scrapdicts,maxdepth,depth,df):
    if (wkey in dictres):
        depth+=1
        for urlref in dictres[wkey]:         
            scrapArticle(df,LibWeb,BaseURL,urlref,Scrapdicts,maxdepth,depth)

#year = int(html_pubmed.find('div', {'class': "article-source"}).find('span', {'class': "cit"}).text.split(' ', 1)[0])
#PMCID = html_pubmed.find('span', {'class': "identifier pmc"}).a.text.strip()
#   'DatePub':{'tag':'div','args':{'class': "article-source"},'tag2':'span','args2':{'class': "cit"}},
Scrapdicts = {'PubMed':{
    'DatePub':{'multi':True,'tag':'div','args':{'class': "article-source"},'tag2':'span','args2':{'class': "cit"}},
    'DOI':{'tag':'span','args':{'class': "citation-doi"}},
    'PMID':{'tag':'span','args':{'class': "identifier pubmed"},'tag2':'strong','args2':{'title': "PubMed ID"}},
    'PMCID':{'tag':'span','args':{'class': "identifier pmc"},'tag2':'a'},
    'Title':{'tag':'h1'},
    'Abstract':{'tag':'div','args':{'class': "abstract-content selected"}},
    'Authors':{'multi':True,'tag':'span','args':{'class': "authors-list-item"},'tag2':'a','args2':{'class': "full-name"},'ctner':'data-ga-label'},
    'OrgAuthors':{'multi':True,'tag':'span','args':{'class': "authors-list-item"},'tag2':'a','args2':{'class': "affiliation-link"},'ctner':'title'},    
    'urlAuthors':{'multi':True,'tag':'span','args':{'class': "authors-list-item"},'tag2':'a','args2':{'class': "full-name"},'ctner':'href'},
    'RefBy':{'multi':True,'tag':'div','args':{'class': "docsum-content"},'tag2':'a','args2':{'data-ga-category': "cited_by"},'ctner':'href'}, 
    'Similar':{'multi':True,'tag':'div','args':{'class': "docsum-content"},'tag2':'a','args2':{'data-ga-category': "similar_article"},'ctner':'href'},  
    }}
Scrapref = {'PubMed':{
    'RefTo':{'multi':True,'tag':'ol','args':{'class': "references-and-notes-list"},
    'tag2':'a','args2':{'data-ga-action': re.compile(r"^[1-9]{8}$")},'ctner':'href'} 
    }}
Scraprefby = {'PubMed':{
    'RefBy':{'multi':True,'tag':'div','args':{'class': "docsum-content"},'tag2':'a','args2':{'class': 'docsum-title'},'ctner':'href'} 
    }}
Scraprefbynbpages = {'PubMed':{
    'NbPages':{'tag':'label','args':{'class': "of-total-pages"}} 
    }}
 #   html_PMC.find_all('div', {'class': "tsec sec"}) 
ScrapPMC = {'PubMed':{
    'Body':{'tag':'div','args':{'class': "jig-ncbiinpagenav"}} 
    }}
#CITED BY URL = "https://pubmed.ncbi.nlm.nih.gov/?linkname=pubmed_pubmed_citedin&from_uid=" + f"{PMID}"
#Conflicts of Interest
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
                    ret.append(filtretext(r.text if 'ctner' not in vtopic else r[vtopic['ctner']]))      
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
            dictref={}
            scrap(Scrapref[LibWeb],BaseURL,DetailURL+'references/',dictref)
            if len(dictref['RefTo'])>0 :
                dictres['RefTo']=[]
                dictres['RefTo'].append(dictref['RefTo'])
            #Scraprefbynbpages
            rbdetURL = "?linkname=pubmed_pubmed_citedin&from_uid="+DetailURL.replace("/","") #+'&page='
            dictref={}
            scrap(Scraprefbynbpages[LibWeb],BaseURL,rbdetURL,dictref)
            NbPages=''
            NbPages = Dict2Itm(dictref,'NbPages','','')
            if len(NbPages)>0:
                NbPages=NbPages.split(' ')[1]
                dictref2={}
                dictres['RefBy']=[]
                for ipag in range(1,int(NbPages)+1):
                    tmpurl = rbdetURL+'&page='+str(ipag)
                    scrap(Scraprefby[LibWeb],BaseURL,tmpurl,dictref2)
                    #print(BaseURL+tmpurl,'nbpage',NbPages,Scraprefby,dictref2)
                    
                    if len(dictref2['RefBy'])>0:
                         dictres['RefBy'].append(dictref2['RefBy'])

            if 'PMCID' in dictres and len(dictres['PMCID'])>0:
                dictPMC={}
                PMCID=dictres['PMCID'][0]
                PMCID=PMCID.split(':')[1]
                scrap(ScrapPMC[LibWeb],'https://www.',
                    'ncbi.nlm.nih.gov/pmc/articles/'+PMCID.strip()+'/',dictPMC)
                dictres['Body']=dictPMC['Body'] 

            PrepSaveArticle(dictres,DetailURL,LibWeb,df)
            print(datetime.now(),'article #',nbArt,'Level',depth,dictres['Title'])
            if NbPages != '':
                followtree(dictref2,'RefBy',LibWeb,BaseURL,Scrapdicts,maxdepth,depth,df)
            followtree(dictres,'Similar',LibWeb,BaseURL,Scrapdicts,maxdepth,depth,df)            
            followtree(dictref,'RefTo',LibWeb,BaseURL,Scrapdicts,maxdepth,depth,df)
            
        

#    'BaseURL':"https://pubmed.ncbi.nlm.nih.gov/",
BaseURL = "https://pubmed.ncbi.nlm.nih.gov"
DetailURL = "/25410209/"
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



