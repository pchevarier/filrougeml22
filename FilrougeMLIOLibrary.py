#FilrougeML IO Librairy
# Dataframe <-> Json
# Structure du DataFrame
#   TitLe: titre de l'article STRING
#   Abstract: Résumé STRING
#   Body: contenu (corps) de l'article STRING
#   RefTo: Liste des DOI auquel se réfere l'article https://doi.org/leDOI
#   Authors DICTIONNAIRE des auteurs clef: Name, Id, Organisation
#   RefBy: List des DOI  des articles se référant à cet article
#   DatePub: Date de publication datetime64
#   url: URL de l'article: STRING
#   LibName: Nom de la bibliothéque ( site web) ou est stocké l'article STRING
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
    df.to_json(dirname+fname,orient=gorient,date_format='iso')
    return()

def AddArticles(DOI,df=None,Title='',Abstract='',Body='',RefTo='',Authors='',RefBy='',DatePub='',url='',LibName=''):
    """Ajoute un article dans un dataframe typé et compatible pour sauvegarde
    Exemple d'utilisation:
    Premier appel de dataframe n'existe pas
    art = AddArticles('10.1128/MCB.22.9.2918-2927.2002',None,'Titre','abstract','body',[['10.1128/MCB.22.9.2918-2927.2002']],{'Name':'nomaut1','Id':'idaut1','Organization':'orgaut1'},[['10.1128/MCB.22.9.2918-2927.2002']],'2020 Feb 20','url','bib')
    Appel suivants, le datframe existe et est passé en parametre
    art = AddArticles('10.1rrr8/MCB.22.9.2918-2927.2002',art,'Titre2','abstract2','body2',[['22210.1128/MCB.22.9.2918-2927.2002']],{'Name':'nomaut2','Id2':'idaut2','Organization2':'orgaut21'},[['12220.1128/MCB.22.9.2918-2927.2002']],'2022 Feb 20','url2','bib2')
    """
    if isinstance(df,type(None)):
        df = pd.DataFrame([[Title,Abstract,Body,RefTo,Authors,RefBy,DatePub,url,LibName]],
                  columns = ['Title','Abstract','Body','RefTo','Authors','RefBy','DatePub','url','LibName'],
                  index=[DOI]
                  )
        df= df.astype({'Title':'string','Abstract':'string','Body':'string','DatePub':'datetime64[ns]','url':'string','LibName':'string'})
    else:
        df.loc[DOI]= [Title,Abstract,Body,RefTo,Authors,RefBy,DatePub,url,LibName]
    return(df)

#art = AddArticles('10.1128/MCB.22.9.2918-2927.2002',None,'Titre','abstract','body',[['10.1128/MCB.22.9.2918-2927.2002']],{'Name':'nomaut1','Id':'idaut1','Organization':'orgaut1'},[['10.1128/MCB.22.9.2918-2927.2002']],'2020 Feb 20','url','bib')
#art = AddArticles('10.1rrr8/MCB.22.9.2918-2927.2002',art,'Titre2','abstract2','body2',[['22210.1128/MCB.22.9.2918-2927.2002']],{'Name':'nomaut2','Id2':'idaut2','Organization2':'orgaut21'},[['12220.1128/MCB.22.9.2918-2927.2002']],'2022 Feb 20','url2','bib2')

#art = pd.DataFrame([['Titre','abstract','body',[['10.1128/MCB.22.9.2918-2927.2002']],{'Name':'nomaut1','Id':'idaut1','Organization':'orgaut1'},[['10.1128/MCB.22.9.2918-2927.2002']],'2022-12-31','url','bib'],
#                   ['Titre2','abstract2','body2',[['10.1128/MCB.22.9.2918-2927.2002']],{'Name':'nomaut2','Id':'idaut2','Organization':'orgaut2'},[['10.1128/MCB.22.9.2918-2927.2002']],'2022-11-30','url2','bib2']],
#                  columns = ['Title','Abstract','Body','RefTo','Authors','RefBy','DatePub','url','LibName'],
#                  index=['10.1128/MCB.22.9.2918-2927.2002','10.1128/MCB.22.9.2918-2927.2022']
#                  )
#art= art.astype({'Title':'string','Abstract':'string','Body':'string','DatePub':'datetime64[ns]','url':'string','LibName':'string'})
#print(art)                  
#art.info()
#dirname=''
#fname = 'test.json'
#SaveArticles(dirname,fname,art)
#art2= LoadArticles(dirname,fname)
# art2= art2.astype({'Title':'string','Abstract':'string','Body':'string','DatePub':'datetime64[ns]','url':'string','LibName':'string'})
# art2.info()
# print(art2)