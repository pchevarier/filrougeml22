#FilrougeML IO Librairy
# Dataframe <-> Json
#
import pandas as pd
import json

gorient = 'columns'
def LoadArticles(dirname,fname):
    """lit et Charge le fichier json dont le nom est fname dans le répertoire dirname
        retourne le dataframe chargé
    La varialbe globale gorient commune a LoadArticle et SaveArticle 
    assure l'homogénéité de strucure entre lecture et écriture"""
    df = pd.read_json(dirname+fname,orient=gorient)
    return(df)  

def SaveArticles(dirname,fname,df):
    """Sauvegarde le dataframe d'articles df 
    dans le fichier fname dans le répertoire dirname"""
    art.to_json("test.json",orient=gorient)
    return()


art = pd.DataFrame([['Titre','abstract','body','refto',{'Name':'nomaut1','Id':'idaut1','Organization':'orgaut1'},'refby','DatePub','url','bib'],
                   ['Titre2','abstract2','body2','refto2','auteurs2','refby2','DatePub2','url2','bib2']],
                  columns = ['TitLe','Abstract','Body','RefTo','Authors','RefBy','DatePub','url','LibName'])
print(art)                  

dirname=''
fname = 'test.json'
SaveArticles(dirname,fname,art)
art2= LoadArticles(dirname,fname)
art2.info()
print(art2)