from ftplib import FTP
import ftplib
from pprint import pprint
import requests
import json
import os
import shutil
import tweepy


class organize_results:

    def __init__(self, basePath, resultBookPath):
        # Login & Get info from rasPi
        #! Add FTP() & login() to ftpInfo() ?
        self.rasPi = FTP('raspberrypi')
        self.rasPi.login(user='pi', passwd='Fib!1123581321')
        ftpInfo = self.FTPinit()
        pprint(ftpInfo)

        # Load Log, API, Book, BasePath
        self.l = open('Org_Log.txt', 'w')
        # self.api = api
        with open(resultBookPath, 'r') as rb:
            self.rBook = json.load(rb)


        self.l.write(f'Num of Tweets: {len(self.rBook)}\n')
        self.l.write(f'Base Path: {self.basePath}\n')

        #! change to rasPi basepath
        self.basePath = basePath
        # self.rasPi.cwd(self.basePath)
        
        # Delete & remake '\storage\Tweets
        if input(f'Delete {self.basePath}? (y/n)') == 'y':
            
            self.l.write(f'Deleted basepath:\n')
            self.l.write(f'{self.rasPi.nlst()}')

            self.rasPi.rmd(self.basePath)
            
            print('Deleted')
            print(self.rasPi.pwd())
            self.basePath = 'storage/Tweets'
            self.rasPi.mkd(self.basePath)
            self.rasPi.cwd(self.basePath)
            self.l.write(f'{self.basePath} Deleted & Remade\n')

        else:
            self.rasPi.cwd(self.basePath)
            self.l.write('Kept basepath:\n')
            self.l.write(f'{self.rasPi.nlst()}')
            print('Not Deleted')
            # self.l.write(f'Num of Items in {self.basePath}: {len(os.scandir(self.basePath))}\n')
            # print(f'Num of Items in {self.basePath}: {len(os.scandir(self.basePath))}')

    def FTPinit(self):
        HOSTNAME = 'raspberrypi'
        USERNAME = 'pi'
        PASSWORD = 'Fib!1123581321'
        storagePath = 'storage/'

        info = {
            'getwelcome': self.rasPi.getwelcome(),
            'source_address': self.rasPi.source_address,
            'port': self.rasPi.port,
            'host': self.rasPi.host,
            'af': self.rasPi.af,
            'pwd': self.rasPi.pwd(),
            'nlst': self.rasPi.nlst('/storage')
        }
        self.l.write('Server Info:\n')
        json.dump(info, self.l)
        return info

    def put_cont_in_folder(self, url, folderPath):
        self.l.write(f'URL: {url}')
        if url == None:
            self.l.write('URL = None\n')
            print('URL = NONE')
            return None

        # Check for valid URL
        try:
            headers = requests.head(url, allow_redirects=True).headers
            cont_type = headers.get('content-type')
        except Exception:
            self.l.write(f'URL invalid: {url}\n')
            print(f'URL Invalid: {url}\n')
            return None

        # Split URL to get file extension
        try:
            fs = url.split('?')[0]
            suffix = fs.rsplit('.')[-1]
            print(suffix)
        except:
            suffix = fs.rsplit('.')[-1]
        # fileSuffix = url.rsplit('.')[-1]
        fileSuffix = suffix
        self.l.write(f'File Suffix: {fileSuffix}\n')

        # Create File and Print its Name
        content = requests.get(url, allow_redirects=True).content
        tempPath = f'tempFile.{fileSuffix}'
        with open(tempPath, 'wb') as tf:
            tf.write(content)
            self.l.write('Wrote temp File\n')

        with open(tempPath, 'rb') as tf:
            self.rasPi.storbinary(f'STOR {os.path.join(folderPath, tf.name)}', tf)
            self.l.write('Got Temp File\n')

        # with open(os.path.join(folderPath, f'file.{fileSuffix}'), 'xb') as t:
        #     content = requests.get(url, allow_redirects=True).content
        #     self.rasPi.storbinary(f'STOR {os.path.join(folderPath,t.name)}', content)
        #     self.l.write(f'File Name {t.name}\n')
        #     tName = t.name
        
        # content = requests.get(url, allow_redirects=True).content
        # self.rasPi.storbinary(f'STOR {os.path.join(folderPath, "content", fileSuffix)}', content)
        # # self.l.write(f'File Name {t.name}\n')
        
        # pprint(headers, indent=2)
        # print(cont_type)
        # print('--------------------')
        return 'hello'          # IN BYTES

    def get_media_url(self, screen_name, book):
        
        # Check if extBook Exists
        if isinstance(book.get('ext'), dict):
            extBook = book.get('ext')
        else:
            return None

        # Get the vid link if exists
        # TODO Try to get highest bitrate
        if extBook.get('type') == 'video':
            self.l.write('Is Video\n')
            detList = extBook.get('videos')
            bitrate = 0
            for det in detList:
                if det.get('bitrate') != None and det.get('bitrate') > bitrate:                 # Choose highest bitrate
                    mediaUrl = det.get('url')
                    bitrate = det.get('bitrate')
                         
        # Get photo link
        elif extBook.get('type') == 'photo':
            self.l.write('Is Photo\n')
            mediaUrl = extBook.get('url')
        self.l.write(f'Media URL: {mediaUrl}\n')
        
        return mediaUrl


    def sort_results(self, screen_name, book):
        id_str = book['info'].get('id_str')
        self.l.write(f'\nScreen Name: {screen_name}----------------------\n')
        self.l.write(f'Tweet ID: {id_str}\n')
        self.l.write(f'{self.rasPi.pwd()}\n')

        # Create storage\Tweets\Screen_Name if doesnt exist
        
        try:
            namedPath = os.path.join(self.basePath, screen_name)
            self.rasPi.cwd(namedPath)
            self.l.write(f'{namedPath} Already Exists, chdir\n')
        except Exception:
            newPath = os.path.join(self.basePath, screen_name)
            
            self.rasPi.mkd(newPath)
            self.rasPi.cwd(newPath)
            self.l.write(f'{newPath} Created\n')

        # Create C:\Twitter\Screen_Name\ID_STR if doesnt exist
        try:
            self.rasPi.mkd(id_str)
            self.rasPi.cwd(id_str)
            self.l.write('Made Dir from id_str\n')
        except Exception:
            self.rasPi.cwd(id_str)
            self.l.write(f'File Exists, changed dir to {id_str}\n')
        tweetFolder = os.path.join(self.basePath, screen_name, id_str)

        # Get the json repr. of tweet from ID
        # with open(os.path.join(tweetFolder, 'JSON_Representation.json'), 'x') as j:
        #     jStat = self.api.get_status(id_str)._json
        #     json.dump(jStat, j, indent=2)
        
        # Dump the tweet's book 
        # with open(os.path.join(tweetFolder, 'book.json'), 'x') as j:
        #     json.dump(book, j, indent=2)
        mediaUrl = self.get_media_url(screen_name, book)
        bookPath = os.path.join(tweetFolder, '_book.json')

        # Dump user's book into temp file
        with open('jsonStorage.json', 'w') as jt:
            json.dump(book, jt)

        # GET user's book from temp file
        with open('jsonStorage.json', 'rb') as jt:
            self.rasPi.storlines(f'STOR {bookPath}',jt)

        fileName = self.put_cont_in_folder(mediaUrl, tweetFolder)
        self.rasPi.cwd(self.basePath)
        self.l.write('Changed back to base\n\n')
        return fileName


bookPath = 'convBook.json'
with open(bookPath, 'r') as bp:
    topBook = json.load(bp)
basePath = '/storage/Tweets'
ro = organize_results(basePath,bookPath )
for screen_name, book in topBook.items():
    ro.sort_results(screen_name, book)
ro.l.close()