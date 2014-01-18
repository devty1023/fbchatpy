import sleekxmpp
import logging
import socket
import Queue

class FBChat(sleekxmpp.ClientXMPP):
    def __init__( self, app_id, access_token, port=5222 ):
        # initialize ClientXMPP superclass
        # jid and password is not requried in FB XMPP server
        super(FBChat, self).__init__( jid='', password='', sasl_mech='X-FACEBOOK-PLATFORM')

        self.auto_reconnect = True

        # following facebook chat api...
        self.credentials['api_key'] = app_id
        self.credentials['access_token'] = access_token

        # add event handlers
        self.add_event_handler('session_start', self.start)
        self.add_event_handler('no_auth', self.authFailed)

        # auth_queue to check auth failure
        self.auth_queue = Queue.Queue()

        self.xmppPort = port

    def authFailed(self, event):
        # sending message has failed..
        self.auth_queue.put('authFailed')
        self.disconnect(wait=True)


    def start(self, event):
        # authentication is successful!
        print 'authentication successfull..'
        self.auth_queue.put('success')

        # NOTE: sensing presence and getting roster follows of XMPP guidline
        self.send_presence()
        self.get_roster()

        # NOTE: I'm not sure how we can check is message is succesfully sent..
        self.send_message(  mto=self.fb_id,
                            mbody=self.msg,
                            mtype='chat')

        print 'message has been sent (but was it succesfully sent?)'
        print 'disconnecting...'
        self.disconnect(wait=True)

    def sendMessage(self, fb_id, msg):
        # NOTE: Currently, FBChat needs to make new XMPP connection every time user calls sendMessage
        # That is pretty terrible...

        # clear success/failure state
        self.auth_queue.queue.clear()

        # save fb_id and msg as internal var
        self.fb_id = str(fb_id) + '@chat.facebook.com'
        self.msg = msg

        # get IP address of facebook chat
        # for some reason, internal dns doesnt seem to work
        try:
            server = socket.gethostbyname('chat.facebook.com')
        except socket.error:
            print e.strerror
            print 'sendMessage fails'
            return False

        port = self.xmppPort  

        # since sleekxmpp is multithreaded
        # we should process send_message at atConnection
        self.connected = self.connect( (server, port ) )
        if not self.connected:
            print 'connection failed'
            return False

        # initiate xmpp protocol (?)
        self.process(block=True)
        
        # we poll our queue to retrieve its content (overkill?)
        try: 
            result = fbChat.auth_queue.get(timeout=10)
        except queue.Empty:
            result = 'failed'

        if result == 'authFailed':
            raise Exception('authorization failed. perhaps access token expired?')

        # return true on success
        return result=='success'

if __name__ == '__main__':
    # enable xmpp logs by removing the comment
    #logging.basicConfig(level=logging.DEBUG,format='%(levelname)-8s %(message)s')
    fbChat = FBChat( APP_ID, ACCESS_TOKEN  )
    print fbChat.sendMessage( FBID, 'hello world' )
