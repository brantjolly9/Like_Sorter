from email.mime import base
from pprint import pprint
import requests
import json
import os
import shutil

class organize_results:

    def __init__(self, basePath, resultBookPath, api):
        # Load Log, API, Book, BasePath
        self.l = open('Org_Log.txt', 'w')
        self.api = api
        with open(resultBookPath, 'r') as jFile:
            self.rBook = json.load(jFile)
        self.basePath = basePath

        self.l.write(f'Num of Tweets: {len(self.rBook)}\n')
        self.l.write(f'Base Path: {self.basePath}\n')

        #? Replace with RasPi
        # os.chdir('C:\\') #!
        if input(f'Delete {self.basePath}? (y/n)') == 'y':
            print(os.getcwd())
            shutil.rmtree(self.basePath, ignore_errors=True)
            os.mkdir(self.basePath)
            print(f'Deleted and remade base\n{self.basePath}')
            self.l.write(f'{self.basePath} Deleted & Remade\n')

        else:
            print('Not Deleted')
            # self.l.write(f'Num of Items in {self.basePath}: {len(os.scandir(self.basePath))}\n')
            # print(f'Num of Items in {self.basePath}: {len(os.scandir(self.basePath))}')

    def put_cont_in_folder(self, url, folderPath):
        """ Checks if the given url is valid then checks the file type from the extension of the url
            If all checks passed: write the url's content into folderPath/test.suffix

        Args:
            url (str): a url to search
            folderPath (str or path()): the folder to create the media file under

        Returns:
            str(): the name of the created media file if any; else None
        """  

        # Check for valid URL
        try:
            mediaRes = requests.get(url, allow_redirects=True)
        except Exception:
            self.l.write(f'URL invalid: {url}\n')
            print(f'URL Invalid: {url}\n')
            return None

        # Split URL to get file extension
        try:
            fs = url.split('?')[0]
            fileSuffix = fs.rsplit('.')[-1]
            print(fileSuffix)
        except:
            fileSuffix = fs.rsplit('.')[-1]
        # fileSuffix = url.rsplit('.')[-1]
        self.l.write(f'File Suffix: {fileSuffix}\n')
        
        contentFilePath = os.path.join(folderPath, f'file_{folderPath[-4:]}.{fileSuffix}')
        
        # Create File and Print its Name
        try:
            with open(contentFilePath, 'xb') as mediaFile:
                mediaFile.write(mediaRes.content)
                self.l.write(f'!File Name {mediaFile.name}\n')
                    
        except FileExistsError as fee:
            self.l.write(f'File Exists: {folderPath.split("/")} \n{contentFilePath}')
            return folderPath
            
            return fee
        
        except FileNotFoundError as fnf:
            with open(contentFilePath + '1', 'wb') as mediaFile:
                mediaFile.write(mediaRes.content)
                self.l.write(f'!File Name {mediaFile.name}\n')
            print('file not found')

    # Dont Need
    def get_media_url(self, book):
        """ Gets the media URL out of book object if one exists
            Can either be an image or video

        Args:
            screen_name (str): screen name of acct associated with the book
            book (dict): like object

        Returns:
            url: found media url
        """
        # Check if extBook Exists
        screen_name = list(book.keys())[0]
        if not book[screen_name].get('hasMedia'):
            return None
        else:
            tweetBook = book[screen_name]

        # Get the vid link if exists
        # TODO Try to get highest bitrate
        if tweetBook.get('type') == 'video':
            self.l.write('Is Video\n')
            detList = tweetBook.get('videos')
            bitrate = 0
            for det in detList:
                if det.get('bitrate') != None and det.get('bitrate') > bitrate:                 # Choose highest bitrate
                    mediaUrl = det.get('url')
                    bitrate = det.get('bitrate')

        # Get photo link
        elif tweetBook.get('type') == 'photo':
            self.l.write('Is Photo\n')
            mediaUrl = tweetBook.get('url')
        self.l.write(f'Media URL: {mediaUrl}\n')
        return mediaUrl

    def sort_results(self, book):
        screen_name = list(book.keys())[0]
        
        id_str = book[screen_name].get('id_str')
        # id_str = book[screen_name].get('id_str')
        self.l.write(f'\nScreen Name: {screen_name}----------------------\n')
        self.l.write(f'Tweet ID: {id_str}\n')

        # Create C:\Twitter\Screen_Name if doesnt exist
        try:
            namedPath = os.path.join(self.basePath, screen_name)
            os.chdir(namedPath)
            self.l.write(f'{namedPath} Already Exists, chdir\n')
        except Exception:
            newPath = os.path.join(self.basePath, screen_name)
            os.mkdir(newPath)
            os.chdir(newPath)
            self.l.write(f'{newPath} Created\n')

        
        # Create C:\Twitter\Screen_Name\ID_STR if doesnt exist
        try:
            os.mkdir(id_str)
            os.chdir(id_str)
            self.l.write('Made Dir from id_str\n')
        except FileExistsError:
            os.chdir(id_str)
            self.l.write(f'File Exists, changed dir to {id_str}\n')
        tweetFolder = os.path.join(self.basePath, screen_name, id_str)

        # Get the json repr. of tweet from ID
        #! Only reference of API, find way to remove
        #! Causes problems when same tweet folder already exists
        with open(os.path.join(tweetFolder, 'JSON_Representation.json'), 'w') as j:
            jStat = self.api.get_status(id_str)._json
            json.dump(jStat, j, indent=2)
        
        # Dump the tweet's book 
        with open(os.path.join(tweetFolder, 'book.json'), 'w') as bookFilePath:
            json.dump(book, bookFilePath, indent=2)
            
        # mediaUrl = self.get_media_url(book)
        if book[screen_name].get('hasMedia'):
            mediaUrl = book[screen_name].get('mediaUrl')
        else:
            mediaUrl = None
        fileName = self.put_cont_in_folder(mediaUrl, tweetFolder)
        os.chdir(self.basePath)
        self.l.write('Changed back to base\n\n')
        return fileName

# bookPath = 'convBook.json'
# ro = organize_results(basePath,bookPath )
# ro.sort_results()
# ro.l.close()