from tkinter import N
import tweepy
import json
import requests
import os
from pprint import pprint
import Organize_Reports
# import tweepy.error as te
from ftplib import FTP
import datetime
'''

onevisbnovn
        osjvnosjvn
        ojsvneojvnvosn


'''
#! CHANGE TO JSON BECAUSE THE LOCATORS ONLY WORK WITH A DIRECT LINE, SO QUOTE TWEET HANDLINF WONT WORK
#TODO: change log from .txt to .log using general logger
with open('TwitterCreds.json', 'r') as c:
    creds = json.load(c)

l = open('convLog.txt', 'w')

# Authorized for only public, read only data (Oauth2 instead of Oauth1)
auth = tweepy.OAuthHandler(creds['Consumer']['key'], creds['Consumer']['secret'])
api = tweepy.API(auth)

# ---------------------------- Check Base Entities --------------------------- #
def check_entities(like):
    """ Checks and/or retrieves info from like.entities

    Args:
        like (tweetObj): the tweet to analyze

    Returns:
        str(): screen name of user
        dict(): book of tweet info
    """    
    book = {}
    screen_name = like.user.screen_name
    entitiesDict = like.entities
    l.write(f'\n{screen_name}-------\n')
    l.write(f'-Entities\n--------\n')
    
    #! Needs improvement
    # Removes all letters not ascii
    tweetText = ''
    for letter in like.text:
        if letter.isascii():
            tweetText += letter

    l.write(tweetText + '\n')
    book.update({'text': tweetText})
    
    # Try to update book w/ ent.urls 
    try:        
        urls = like.entities['urls'][0]
        expanded_url = urls.get('expanded_url')
        book.update({'expanded_url': expanded_url})
        l.write(f'Found {len(urls.keys())} URLs\n')
        l.write(f'Expanded_url: {expanded_url}\n')
        l.write('Book updated')

    # Try to update book w/ ent.media
    except AttributeError as urlError:
        l.write(f'No Entities.urls for {screen_name}\n')
        mediaUrl = entitiesDict['media'][0].get('media_url_https')
        l.write(f'Found {entitiesDict["media"][0].get("media_url_https")}\n')
        l.write(f'Pic Url: {mediaUrl}\n')
        book.update({'media_url_https': mediaUrl})

    except IndexError:
        l.write('Index Error on Media Url\n')
    
    book.update({'hasMedia': False})
    return screen_name, book

# -------------------------- Check External Entities ------------------------- #
def check_ext_entities(like):
    """Checks like.extendedEntities for tweet info, likely for media or quote

    Args:
        like (tweetObj): tweet to analyze

    Returns:
        str(): screen name from tweet
        dict(): info from tweet
    """    
    l.write('-Extended Entities\n------\n')
    screen_name = like.user.screen_name
    book = {}
    videos = []

    try:
        media = like.extended_entities['media'][0]
        l.write('Found Ext Media\n')
    except AttributeError as ae:
        l.write(f'No extEntMedia for: {screen_name}\n')
        return screen_name, None

    thumbnail = media.get('media_url_https')
    typ = media.get('type')
    
    if typ == 'video':
        l.write('Is Video\n')
        try:
            video_info = media.get('video_info')
            duration = video_info.get('duration_millis')/1000
            l.write(f'Found dur [{duration}] and vid info [len:{len(video_info.keys())}]\n')
        
            for v in video_info.get('variants'):
                vBook = {
                    'bitrate': v.get('bitrate'),
                    'url': v.get('url'),
                    'content_type': v.get('content_type')
                }
                if v.get('bitrate'):
                    videos.append(vBook)
                    book.update({'mediaUrl': v.get('url')})
                l.write('vBook appended to videos\n')

            book.update({
                'thumbnail': thumbnail,
                'hasMedia': True,
                'type': typ,
                'duration': duration,
                'videos': videos         
            })
        except AttributeError as ae:
            print('Attr. Error')
            l.write('Cant Find "video_info"\n')

    elif typ == 'photo':
        l.write('Is Photo\n')
        book.update({
            'hasMedia': True,
            'type': typ,
            'mediaUrl' : media.get('media_url_https')
            })
    return screen_name, book

# -------------------------------- Quote Tweet ------------------------------- #
def check_quote(like):
    l.write('==================================\n')
    l.write(f'-----{like.user.screen_name}--------\n')
    l.write('Check Quote\n')
    convo = []
    info = {}
    if like.is_quote_status:
        quotedTweetId = like.quoted_status.id_str
        l.write('\tIs Quoted Status\n')
        l.write(f'\tOriginal Tweet ID: {like.id_str}\n')
        l.write(f'\tQuoted Tweet ID: {quotedTweetId}\n')
        try: 
            newTweet = api.get_status(quotedTweetId)
            return 'quoted', newTweet
        except tweepy.TweepError as te:
            print(te.args)

    elif like.in_reply_to_status_id_str:
        ogTweetId = like.in_reply_to_status_id_str
        l.write('\tIs a reply Status\n')
        l.write(f'\tReply Tweet ID: {like.id_str}\n')
        l.write(f'\tOriginal Tweet ID: {ogTweetId}\n')
        try: 
            newTweet = api.get_status(ogTweetId)
            # originality, nextTweet = check_quote(newTweet)
            
            # convo.append(nextTweet)
            
            return 'replied', newTweet
        except tweepy.TweepError as te:
            print(te.args)
    else:
        tweetID = like.id_str
        l.write(f'\tReturned Original Tweet: {tweetID}\n')
        return 'original', like

# -------------------------------- Add To Book ------------------------------- #
def add_to_book(book, entBook, screen_name):
    """Adds a given book to the main book under screen name

    Args:
        book (dict): convBook to hold all other books
        entType (str): type of sub book (ent or ext)
        entBook (dict): subbook to add to convBook
        screen_name (str): screen name of tweet author
    """    
    if isinstance(entBook, dict):
        l.write(f'\n** Adding {entBook.keys()}\n________________________\n')
        # finalKey = str(screen_name + str(snCount))
        print(screen_name)
        book[screen_name].update(entBook)
        return book
    else:
        try:
            book[screen_name].update(entBook)
            return book
        except Exception as e:
            print(e)
        
        # try:
        #     t = book.get('likes').index(screen_name)
        #     print(t)
        # except ValueError:
        #     book.get('likes').append({screen_name: entBook})

# ---------------------------- Dict Of Tweet Info ---------------------------- #
def get_info(like):
    """ Compiles an info dict from import tweet values

    Args:
        like (tweetObj): tweet to analyze

    Returns:
        dict(): book of important tweet values
    """    
    info = {}
    info['id_str'] = like.id_str
    info['text'] = like.text
    info['name'] = like.user.name
    info['screen_name'] = like.user.screen_name
    info['created_at'] = str(like.created_at)
    info['favorite_count'] = like.favorite_count
    info['retweet_count'] = like.retweet_count
    info['in_reply_to_status_id_str'] = like.in_reply_to_status_id_str
    try:        
        info['quoted_status.id_str'] = like.quoted_status.id_str
    except Exception as e:
        pass
    # print(like.user.screen_name)
    try:
        mentions = like.entities.get('user_mentions')
        userMentions = {
            'screen_name': mentions[0].get('screen_name'),
            'id_str': mentions[0].get('id_str')
        }
        info.update({'user_mentions': userMentions})
    except IndexError as ie:
        # .mentions exists, but empty
        pass
    except AttributeError as ae:
        # .mentions doesnt exist
        pass
    return info

def fill_book(result, tweetList):
    originiality, newTweet = check_quote(result)
    print('begin' + str(len(tweetList)))
    firstScreenName = result.user.screen_name
    # tweetList.append(result)
    # print(firstScreenName)
    
    #!
    tweetBook = {firstScreenName: {}}
    
    if originiality == 'original':
        # screen_name, entBook = check_entities(result)
        # screen_name, extBook = check_ext_entities(result)
        # info = get_info(result)
        # info['convo'] = len(tweetList)
        # info.update(entBook)
        # info.update(extBook)
        # tweetBook[firstScreenName].append(info)
        
        screen_name, entBook = check_entities(result)
        screen_name, extBook = check_ext_entities(result)
        tweetInfo = get_info(result)
        

        convoBook = add_to_book(tweetBook, entBook, screen_name)
        convoBook = add_to_book(tweetBook, extBook, screen_name)
        convoBook = add_to_book(tweetBook, tweetInfo, screen_name)
        print(type(tweetBook))
        tweetList.append(convoBook)
        
        '''
        for pane in panes:
            if isinstance(pane, dict):
                
                pass
        tweetBook[firstScreenName].update(entBook)
        tweetBook[firstScreenName].update(extBook)
        tweetBook[firstScreenName].update(info)
        print(len(tweetList))
        '''
        
        return tweetBook, tweetList

    elif originiality == 'quoted':
        originiality, newTweet = check_quote(newTweet)
        l.write('is quoted\n')
        print('qtd', end='')
        nextTweet = fill_book(newTweet, tweetList)
        print(type(nextTweet))
        tweetList.append(nextTweet)
        
        
    elif originiality == 'replied':
        l.write('is a reply\n')
        originiality, newTweet = check_quote(newTweet)
        print('reply', end='')
        nextTweet = fill_book(newTweet, tweetList)
        tweetList.append(nextTweet)
    tweetList.append(newTweet)


book = {'likes':[]}
results = api.get_favorites(screen_name='hiddenyang1', count=40)
finalList = []
for result in results:
    convoList = []
    fullBook = fill_book(result, convoList)
    # convoList = fullBook
    print(type(fullBook))
    # if not fullBook:
    #     # convoList.append()
    #     l.write(f'List len {len(convoList)}\n')
    
    # finalList.append(convoList)
    # print(len(convoList))
    book['likes'].append(convoList)
    '''
    originiality, r = check_quote(result) # Get the list of likes in tweet form
    # if originiality == 'replied':    
        
    # print(f'Origin: {originiality}\tScreen_name: {r.user.screen_name}')
    # Add returned entities book to a book['screen_name'] = {}
    
    tweetBook = {screen_name: {}}
        
    screen_name, entBook = check_entities(r)
    add_to_book(tweetBook, entBook, screen_name, 'ent')

    screen_name, extBook = check_ext_entities(r)
    add_to_book(tweetBook, extBook, screen_name, 'ext')

    tweetInfo = get_info(r)
    add_to_book(tweetBook, tweetInfo, tweetInfo.get('screen_name'), 'info')
    
    book['likes'].append(tweetBook)
    '''
# pprint(book)
print(len(finalList))
print(type(book))
print(len(book))
with open('convBook.json', 'w') as cb:
    json.dump(book, cb, indent=3)          
print(f'# Likes: {len(results)}')
print(f'# keys in book: {len(book["likes"])}')
l.close()

basePath = r'C:\Users\User\Documents\Programming\Python_stuff\twitLikeStorage\TwitterFiles'

ro = Organize_Reports.organize_results(basePath, 'convBook.json', api)
tweetAuthors = []
for index, tweetDict in enumerate(book.get('likes')):
    print('f'+str(index))
    fileName = ro.sort_results(tweetDict)
    screen_name = list(tweetDict.keys())[0]
    tweetAuthors.append(screen_name)
    
print(tweetAuthors)
ro.l.close()

""" Code to save JSON files
with open(f'TwitterResults\\Like_{screen_name}.json', 'w') as file:
    json.dump(like._json, file, indent=2)
    
#! Possible Solution to stacking tweets by author
# Python3 code to demonstrate working of
# Get values of particular key in list of dictionaries
# Using map() + itemgetter()
from operator import itemgetter
  
# initializing list
test_list = [{'gfg' : 1, 'is' : 2, 'good' : 3},
             {'gfg' : 2}, {'best' : 3, 'gfg' : 4}]
  
# printing original list
print("The original list is : " + str(test_list))
  
# Using map() + itemgetter()
# Get values of particular key in list of dictionaries
res = list(map(itemgetter('gfg'), test_list))
  
# printing result 
print("The values corresponding to key : " + str(res))

"""