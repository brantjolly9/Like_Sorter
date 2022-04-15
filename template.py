import imaplib

import email
from email.header import decode_header
from pprint import pprint
# import dateutil.parser

class sorter:
    def __init__(self, username, password):
        self.LOG = open('IMAP_LOG2.txt', 'w')
        self.imap = imaplib.IMAP4_SSL("imap.mail.yahoo.com", 993)

        # Get and write socket info
        sock = self.imap.socket()
        self.LOG.write('SOCKET: \n')
        self.LOG.write(str(sock) + '\n')

        # Login and record creds
        try: 
            self.imap.login(username, password)
            self.LOG.write(f'User: {username}\n')
            self.LOG.write(f'Pass: {password}\n')
        except imaplib.IMAP4_SSL.error as e:
            print(e.args)
            self.LOG.write('Login FAILED\n')
            self.done()
        
    def check_mailbox(self, inbox):
        self.LOG.write(f'Inbox: {inbox}\n')
        boxStatus, messages = self.imap.select(inbox)
        self.LOG.write(f'Box Status: {boxStatus}\n')

        numMsg = int(messages[0].decode('utf-8'))
        self.LOG.write(f'# of Msg: {numMsg}\n')

        emailInfo = {}
        counter = 0
        for i in range(1, numMsg + 1):
            res, msg = self.imap.fetch(str(i), "(RFC822)")
            
            for part in msg:
                if isinstance(part, tuple):
                    m = email.message_from_bytes(part[1])
            self.LOG.write('\n=================NEW EMAIL=================\n')
            emailInfo = self.Record_Info(m)
            self.logInfo(emailInfo)
            content = self.getContent(m)
        return emailInfo
    
    def getContent(self, msg):
        self.LOG.write('\nGET CONTENT------------------\n')
        if msg.is_multipart():

            # Iterate through message parts
            for part in msg.walk():
                ct = part.get_content_type()
                cont_dispo = str(part.get("Content-Disposition"))
                
                # Try Email Body
                try:
                    body = part.get_payload(decode=True).decode()
                    self.LOG.write('Has Payload\n')
                except Exception as e:
                    pass
                
                if ct == 'text/plain':
                    self.LOG.write(f"Body: {body}\n")

                if 'attachment' in cont_dispo:
                    subjectPath = f'C:/Users/User/Documents/Programming/Python_stuff/rEmail/{msg["Subject"]}.pdf'
                    with open(subjectPath, "wb") as tn:
                        tn.write(part.get_payload(decode=True))
                    self.LOG.write(f'PDF: {msg["subject"]}\n')
            
    
    def Record_Info(self, message):
        emailInfo = {}
       # Get last 10 digit of ID before g@mail.com
        full_id = message['Message-ID']
        id = full_id.split('@')[0][-10:]

        subject = message['Subject']
        contType = message.get_content_type()

        # Only read the email from the sender item
        frm = str(message.get('From'))
        beginAddr = frm.find('<')
        endAddr = frm.find('>')
        frm = frm[beginAddr + 1:endAddr]

        # Parse the date into workable str
        # dt = dateutil.parser.parse(message['Date'])
        # d = dt.strftime('%a, %b %d, %Y at %I:%M %p')
        # emailInfo[id].update({'Date': d})
        
        # Populate emailInfo
        emailInfo[id] = {}
        emailInfo[id].update({'Full_ID': full_id})
        emailInfo[id]['From'] = frm
        emailInfo[id].update({'Subject': subject})
        emailInfo[id].update({'Date': message['Date']})
        emailInfo[id].update({'Content-Type': contType})
        
        #! Test for non-multipart messages
        if 'multipart' in message.get_content_type():
            for part in message.walk():
                load = str(part.get_payload())
                if load.startswith('http'):
                    emailInfo[id].update({'Link': load})
                    self.LOG.write(load)
        
        return emailInfo

    # Iterate through a given dict to write all into LOG
    def logInfo(self, info):
        for id in info.keys():
            self.LOG.write(f'ID: {id}\n')
            for key, value in info.get(id).items():
                self.LOG.write(f'{key}: {value}\n')


    def done(self):
        self.LOG.close()
        self.imap.close()
        self.imap.logout()

un = "remarkableemail@yahoo.com"
pw = "d0N7h@(c"
apw = "nyqjrnwwrxwczcxn"


s = sorter(un, apw)
info = s.check_mailbox('INBOX')
s.done()
