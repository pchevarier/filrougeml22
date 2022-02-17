import requests
from bs4 import BeautifulSoup as bs


def getBsSrcFromUrl(url: str, headers={}):
    try:
        r = requests.get(url, headers=headers)
    except Exception as e:
        print(e)
        quit()
    else:
        return bs(r.text, 'html.parser')


def getTitle(bsSrc: bs):
    return bsSrc.h1.text.strip()


def getPubDate(bsSrc: bs):
    return bsSrc.find('div', {'class': "article-source"}).find('span', {'class': "cit"}).text.split(' ', 1)[0]


def getPMCId(bsSrc: bs):
    try:
        PMCID = bsSrc.find('span', {'class': "identifier pmc"}).a.text.strip()
    except AttributeError:
        PMCID = ''
    return PMCID


def getDOI(bsSrc: bs):
    try:
        DOI = bsSrc.find('span', {'class': "identifier doi"}).a.text.strip()
    except AttributeError:
        DOI = ''
    return DOI


def getPMId(bsSrc: bs):
    try:
        DOI = bsSrc.find('strong', {'class': "current-id"}).text.strip()
    except AttributeError:
        DOI = ''
    return DOI


def getAuthor(bsSrc: bs):
    authorList = []
    authors = bsSrc.select('div.full-view span.authors-list-item')

    for author in authors:
        aut = author.find('a', {'class': "full-name"})['data-ga-label']
        try:
            autUrl = author.find('a', {'class': "full-name"})['href']
        except:
            autUrl = ''

        try:
            affs = author.find_all('a', {'class': "affiliation-link"})
            aff = []
            for x in affs:
                aff.append(x['title'])
        except Exception as e:
            aff = []

        authorList.append({'author': aut, 'affiliation': aff, 'href': autUrl})

    return authorList


def getAbstract(bsSrc: bs):
    try:
        text = bsSrc.find(
            'div', {'class': "abstract-content selected"}).text.strip().replace('\n', ' ')
    except:
        text = ''
    return text


def getReferences(srcUrl: str):
    refBaseUrl = 'https://pubmed.ncbi.nlm.nih.gov/'
    refBS = getBsSrcFromUrl(refBaseUrl + srcUrl + '/references/')

    references_incr = refBS.select('li.skip-numbering')

    refPMC = []
    refPubMed = []
    for ref in references_incr:
        refLink = ref.select('a.reference-link')
        for x in refLink:
            if x.text.strip() == 'PMC':
                refPMC.append(x['data-ga-action'])
            elif x.text.strip() == 'PubMed':
                refPubMed.append(x['data-ga-action'])
    return {'PMC': refPMC, 'PubMed': refPubMed}


def getCitedIn(srcUrl: str):
    citedInPubMed = []

    p = 1
    while True:
        citedInBaseUrl = f'https://pubmed.ncbi.nlm.nih.gov/?page={p}&format=pmid&size=200&linkname=pubmed_pubmed_citedin&from_uid={srcUrl}'
        pageBS = getBsSrcFromUrl(citedInBaseUrl)
        try:
            arts = pageBS.find(
                'pre', {'class': "search-results-chunk"}).text.split('\r\n')
            citedInPubMed = citedInPubMed + arts
            if len(arts) < 200:
                break
            else:
                p = p + 1
        except:
            break
    return citedInPubMed


def getBody(pmc: str):
    if not pmc:
        return ''

    full_text = ''
    bodyBaseUrl = f'https://www.ncbi.nlm.nih.gov/pmc/articles/{pmc}/'
    
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
    s = getBsSrcFromUrl(bodyBaseUrl, headers)

    all = s.find_all('div', {'class': "tsec sec"})
    for i in all:
        full_text = full_text + ' ' + i.text
    return full_text


def getArticle(srcUrl: str):
    baseURL = "https://pubmed.ncbi.nlm.nih.gov/"
    src = getBsSrcFromUrl(baseURL + srcUrl)
    refs = getReferences(srcUrl)
    pmc = getPMCId(src)
    article = {'title': getTitle(src), 'pubDate': getPubDate(
        src), 'PMCID': pmc, 'DOI': getDOI(src), 'PMID': getPMId(src), 'abstract': getAbstract(
        src), 'author': getAuthor(src), 'refPMID': refs['PubMed'], 'citedInPMID': getCitedIn(srcUrl), 'body': getBody(pmc)
    }
    return article
