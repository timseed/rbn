#RBN

Reverse Beacon Network - this is a small utiity that will allow you to connect to a Ham Radio RBN network and get the "spots" from the system.

Just what you do with them next is up to you... however you could

  -  use them when running in a contest 
  -  see how far your call sign is being received

#Useage

There are 2 classes qtrbn - for qt5, and a "straight" rbn for command line type stuff.

##qtrbn

This will return the data as a signal called RBN - so to start the process (assuming a QT Enviroment)

   myrnb = qtrnm()
   myrbn.RBN.connect(self.onRBN)
   myrbn.start()


Then to "catch" the signal

   def onRBN(self,data):



#Data Format

The data object will be a namedTuple

    import collections
    Person = collections.namedtuple('Call','Country','Freq','Band')
    Person('A45wg','Oman','18080.2','17')


#Stats
The stats functionality has been removed and placed in another module.

 
