# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------
# This is a sample controller
# this file is released under public domain and you can use without limitations
# -------------------------------------------------------------------------

# ---- example index page ----

# def index():
#     response.flash = T("Hello World")
#     return dict(message=T('Welcome to web2py!'))

# # ---- API (example) -----
# @auth.requires_login()
# def api_get_user_email():
#     if not request.env.request_method == 'GET': raise HTTP(403)
#     return response.json({'status':'success', 'email':auth.user.email})

# # ---- Smart Grid (example) -----
# @auth.requires_membership('admin') # can only be accessed by members of admin groupd
# def grid():
#     response.view = 'generic.html' # use a generic view
#     tablename = request.args(0)
#     if not tablename in db.tables: raise HTTP(403)
#     grid = SQLFORM.smartgrid(db[tablename], args=[tablename], deletable=False, editable=False)
#     return dict(grid=grid)

# # ---- Embedded wiki (example) ----
# def wiki():
#     auth.wikimenu() # add the wiki to the menu
#     return auth.wiki() 

# # ---- Action for login/register/etc (required for auth) -----
# def user():
#     """
#     exposes:
#     http://..../[app]/default/user/login
#     http://..../[app]/default/user/logout
#     http://..../[app]/default/user/register
#     http://..../[app]/default/user/profile
#     http://..../[app]/default/user/retrieve_password
#     http://..../[app]/default/user/change_password
#     http://..../[app]/default/user/bulk_register
#     use @auth.requires_login()
#         @auth.requires_membership('group name')
#         @auth.requires_permission('read','table name',record_id)
#     to decorate functions that need access control
#     also notice there is http://..../[app]/appadmin/manage/auth to allow administrator to manage users
#     """
#     return dict(form=auth())

# # ---- action to server uploaded static content (required) ---
# @cache.action()
# def download():
#     """
#     allows downloading of uploaded files
#     http://..../[app]/default/download/[filename]
#     """
#     return response.download(request, db)

from gluon.tools import Service
service = Service()

def call():   
    return service()

import pandas as pd
import requests
def load_recommendations(): 
    item_similarity_df = pd.read_csv("applications/movies/static/item_similarity_df.csv",index_col=0)
    print("item_similarity_df cached in memory")
    return item_similarity_df 

item_similarity_df = cache.ram('item_similarity_df3',load_recommendations,None) 
# print(item_similarity_df.head())

def get_similar_movies(movie_name,user_rating):
    try:
        similar_score = item_similarity_df[movie_name]*(user_rating-2.5)
        similar_movies = similar_score.sort_values(ascending=False)
    except:
        print("don't have movie in model")
        similar_movies = pd.Series([])
    
    return similar_movies

def check_seen(recommended_movie,watched_movies):
    
    for movie_id,movie in watched_movies.items():
        movie_title = movie["title"]

        if recommended_movie == movie_title:
            return True
    
    return False

global dates
dates = ('(2015)','(2016)','(2017)','(2018)','(2019)')

@service.json
def get_recommendations(watched_movies):

    similar_movies = pd.DataFrame()

    for movie_id,movie in watched_movies.items():
        similar_movies = similar_movies.append(get_similar_movies(movie["title"],movie["rating"]),ignore_index=True)

    all_recommend = similar_movies.sum().sort_values(ascending=False)[:72]

    recommended_movies = []
    posters = []
    for movie,score in all_recommend.iteritems():
        if not check_seen(movie,watched_movies):
            recommended_movies.append(movie)
            if movie[-6:] in dates: 
                posters.append(get_poster_url(movie))
            else:
                posters.append(None)
    # print(len(recommended_movies))
    if len(recommended_movies) > 70:
        recommended_movies = recommended_movies[0:70]  
        posters = posters[:70]      

    # print(recommended_movies)
    # recommended_movies.append(posters)
    return [recommended_movies,posters]


def load_masterdB():
    masterdB = pd.read_csv("applications/movies/static/masterdB.csv",index_col=0)
    print("masterdB cached in memory")
    return masterdB 

masterdB = cache.ram('masterdB2',load_masterdB,None) 

@service.json
def get_poster_url(title):
    # print(masterdB.head())
    try:
        url = list(masterdB[masterdB['title']==title]['poster'])[0]
    except:
        url = getPosterFromTitle(title)
    # print(url)
    return url


def load_im():
    im = pd.read_csv("applications/movies/static/im.csv",index_col=0)
    print("im cached in memory")
    return im 

im = cache.ram('im2',load_im,None) 

@service.json
def getMovieId(title):
    return getId(list(im[im['title']==title]['imdbId'])[0])

def getId(n):
    n = str(n)
    l = len(str(n))
    if l==7: return 'tt'+n
    elif 'tt' in n: return n
    else:
        return 'tt'+'0'*(7-l) + n

@service.json
def getPoster(movie_id):
    if len(movie_id)!=9: 
        imdbId = getId(movie_id)
    else:
        imdbId = movie_id
    url = "https://imdb-internet-movie-database-unofficial.p.rapidapi.com/film/"+imdbId
    headers = {
    'x-rapidapi-key': "53c9998270msh9c6fd907d16a488p1c908bjsnd884842ae9e4",
    'x-rapidapi-host': "imdb-internet-movie-database-unofficial.p.rapidapi.com"
    }
    return requests.request("GET", url, headers=headers).json()['poster']

@service.json
def getPosterFromTitle(title):
    return getPoster(getMovieId(title))