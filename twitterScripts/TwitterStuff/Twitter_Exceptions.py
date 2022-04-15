from pprint import pprint
# class notReply(Exception):
#     def __init__(self, message):
#         self.message = message
#         # super(notReply, self).__init__(message)
#     def __str__(self):
#         return str(self.massage)
    
# class notQuote(Exception):
#     def __init__(self, message):
#         self.message = message
#         # super(notQuote, self).__init__(message)
#     def __str__(self):
#         return str(self.message)

import requests
import json
import os
basePath = 'C:\\Twitter\\'
# def get_web_content(url):
#     headers = requests.head(url, allow_redirects=True).headers
#     cont_type = headers.get('content-type')
#     pprint(headers, indent=2)
#     print(cont_type)
#     print('--------------------')
    
#     re = requests.get(url, allow_redirects=True)
#     content = re.content
#     return content


# with open('convBook.json', 'r') as cb:
#     convBook = json.load(cb)
# for screen_name, value in convBook.items():
#     print('----------------')
#     print(screen_name)
#     try:
#         # Confirm like.ext
#         extBook = value.get('ext')
#         if extBook.get('type') == 'video':
#             detList = extBook.get('videos')
#             bitrate = 0
#             for det in detList:
#                 if det.get('bitrate') != None and det.get('bitrate') > bitrate:                 # Choose highest bitrate
#                     mediaUrl = det.get('url')
#                     bitrate = det.get('bitrate')
                    
#         elif extBook.get('type') == 'photo':
#             mediaUrl = extBook.get('url')
#         media = get_web_content(mediaUrl)
#         print(type(media))
    
#     except AttributeError:
#         print('No Ext Book')

#     try:
#         namedPath = os.path.join(basePath, screen_name)
#         os.chdir(namedPath)
#     except Exception:
#         newPath = os.path.join(basePath, screen_name)
#         os.mkdir(newPath)
#         os.chdir(newPath)
#     os.mkdir(value['info'].get('id_str'))
#     tweetFolder = os.path.join(basePath, screen_name,value['info'].get('id_str'))
#     #! DUMP JSON TWEET INTO FOLDER
    # with open(os.path.join(tweetFolder, 'JSONRepresentation.json')) as j:
    #     api.get_status(id_str)

    # elif extBook.get('type') == 'photo':
    #     mediaUrl = value['ext'].get('url')
    #     media = get_web_content(mediaUrl)

    
    # if extBook.get('type') == 'video':
    #     detList = extBook.get('videos')
        
    #     bitrate = 0
    #     for det in detList:
    #         if det.get('bitrate') != None and det.get('bitrate') > bitrate:                 # Choose highest bitrate
    #             mediaUrl = det.get('url')
    #             bitrate = det.get('bitrate')
    #             print(bitrate)
    #     media = get_web_content(mediaUrl)

class organize_results:

    def __init__(self, basePath, resultBookPath):
        self.l = open('Org_Log.txt', 'w')

        with open(resultBookPath, 'r') as rb:
            self.rBook = json.load(rb)
        self.basePath = basePath

        self.l.write(f'Num of Tweets: {len(self.rBook)}\n')
        self.l.write(f'Base Path: {self.basePath}\n')
    
    def get_web_content(self, url):
        headers = requests.head(url, allow_redirects=True).headers
        cont_type = headers.get('content-type')
        # pprint(headers, indent=2)
        # print(cont_type)
        # print('--------------------')
        
        re = requests.get(url, allow_redirects=True)
        return re.content          # IN BYTES

    def sort_results(self):
        for screen_name, value in self.rBook.items():
            id_str = value['info'].get('id_str')
            self.l.write(f'Screen Name: {screen_name}\n')
            self.l.write(f'ID: {id_str}')
            
            try:
                # Confirm like.ext
                extBook = value.get('ext')
                self.l.write('Has Extbook')
                if extBook.get('type') == 'video':
                    self.l.write('Is Video')
                    detList = extBook.get('videos')
                    bitrate = 0
                    for det in detList:
                        if det.get('bitrate') != None and det.get('bitrate') > bitrate:                 # Choose highest bitrate
                            mediaUrl = det.get('url')
                            bitrate = det.get('bitrate')
                            
                elif extBook.get('type') == 'photo':
                    self.l.write('Is Photo')
                    mediaUrl = extBook.get('url')
                self.l.write(f'Media URL: {mediaUrl}')
                media = self.get_web_content(mediaUrl)
                print(type(media))
            
            except AttributeError:
                print('No Ext Book')

            try:
                namedPath = os.path.join(basePath, screen_name)
                os.chdir(namedPath)
            except Exception:
                newPath = os.path.join(basePath, screen_name)
                os.mkdir(newPath)
                os.chdir(newPath)
            os.mkdir(id_str)
            tweetFolder = os.path.join(basePath, screen_name,value['info'].get('id_str'))
            with open(os.path.join(tweetFolder, 'JSON_Representation.json'), 'x') as j:
                js = api.get_status(id_str)._json


bookPath = 'convBook.json'
ro = organize_results(basePath,bookPath )
ro.sort_results()
ro.l.close()