import tweepy
import json
import requests
import os
from pprint import pprint

class LikeSorter:
    def __init__(self, creds):
        # Authorized for only public, read only data (Oauth2 instead of Oauth1)
        auth = tweepy.OAuthHandler(creds['Consumer']['key'], creds['Consumer']['secret'])
        self.api = tweepy.API(auth)

    def get_likes(self, user):
        favs = self.api.favorites(user)
        return favs

    def save_as_json(self, user):
        likes = self.api.favorites(user)
        for like in likes:
            jsonLike = like._json

        screenName = like['user'].get('screen_name')
        with open(f'TwitterResults\\Like_{screenName}.json', 'w') as file:
            json.dump(jsonLike, file, indent=2)

    def get_video(self, fav):
       
        tweetID = fav.id_str
        print('\n' + tweetID + '-------------')
        book = {}
        book.update({'UserName': fav.user.screen_name})
        try:
            entitiesDict = fav.entities
            urls = entitiesDict['urls'][0]
            if len(entitiesDict.get('urls')) > 0:
                urls = entitiesDict.get('urls')
                print(type(urls))

                book['expanded_url'] = urls.get('expanded_url')
            elif len(entitiesDict.get('media')) > 0:
                media = entitiesDict.get('media')
                
                book['thumbnail'] = media.get('media_url_https')
        except:
            print('No Entities')
        
        try:
            extmedia = fav.extended_entities.media[0]
            print(extmedia)
            book.update({'thumbnail': extmedia.media_url_https})
            vidInfo = fav.extended_entities.media[0].video_info
            
            if isinstance(vidInfo, dict):
                
                book['Vid_Variants'] = []
                for variant in vidInfo.variants:
                    bitrate = variant.bitrate
                    url = variant.url
                    book['Vid_Variants'].append({
                        'bitrate': bitrate,
                        'url': url
                        })
                    # book['Vid_Variants'].append({'url':url})
        except:
            print('No Extended')
        print(fav.is_quote_status)
        if fav.is_quote_status:
            print(fav.user.screen_name)
            print('Quote------------------------')
            print(type(fav.quoted_status))
            self.get_video(fav.quoted_status)
            
            
        return tweetID, book

    def get_video2(self, fav):
        tweetID = fav.get('id_str')
        book = {}
        book.update({'Vid_Variants': {}})
        counter = 0
        if 'extended_entities' in fav.keys():
            vidInfo = fav['extended_entities']['media'][0].get('video_info')
            if isinstance(vidInfo, dict):
                for variant in vidInfo.get('variants'):
                    
                    book[f'Vid_Variants{counter}'].update({'url': variant.get('url')})
                    book[f'Vid_Variants{counter}'].update({'bitrate': variant.get('bitrate')})
                    counter += 1
        return tweetID, book


with open('TwitterCreds.json', 'r') as c:
    creds = json.load(c)
userName = 'hiddenyang1'
ls = LikeSorter(creds)
favs = ls.get_likes(userName)
final_book = {}
for fav in favs:
    tweetID, book = ls.get_video(fav)
    final_book.update({tweetID: book})
with open('final_book.json', 'w') as fb:
    json.dump(final_book, fb, indent=2)

print(f'Number of likes: {len(final_book.keys())}')

