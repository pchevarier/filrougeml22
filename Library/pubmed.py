import requests
from bs4 import BeautifulSoup as bs


def getBsSrcFromUrl(url: str):
    try:
        r = requests.get(url)
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
            'div', {'class': "abstract-content selected"}).text.strip().replace('\n', '')
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
    citedInBaseUrl = f'https://pubmed.ncbi.nlm.nih.gov/?linkname=pubmed_pubmed_citedin&from_uid={srcUrl}&page='

    citedInPubMed = []

    i = 1
    p = 1
    while (i <= p):
        pageBS = getBsSrcFromUrl(citedInBaseUrl+str(p))

        if (p == 1):
            p = int(pageBS.find(
                'label', {'class': "of-total-pages"}).text.split(' ')[1])
        i = i + 1
        arts = pageBS.select('article.full-docsum')
        for x in arts:
            citedInPubMed.append(x.find('span', {'class': 'docsum-pmid'}).text)

    return citedInPubMed


def getArticle(srcUrl: str):
    baseURL = "https://pubmed.ncbi.nlm.nih.gov/"
    src = getBsSrcFromUrl(baseURL + srcUrl)
    refs = getReferences(srcUrl)
    article = {'title': getTitle(src), 'pubDate': getPubDate(
        src), 'PMCID': getPMCId(src), 'DOI': getDOI(src), 'PMID': getPMId(src), 'abstract': getAbstract(
        src), 'author': getAuthor(src), 'refPMID': refs['PubMed'], 'citedInPMID': getCitedIn(srcUrl)
    }
    return article
