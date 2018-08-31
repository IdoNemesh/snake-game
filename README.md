# snake-game
A python implementation of the nostalgic snake game.

## Key features:
  * A central server that stores the leaderboard and usernames and their passwords securely (hashed!)
  * The server support multi-client playing, meaning that multiple clients can play at the same time and communicate with the       server with no interference
  * The client-server communication is encrypted
  
## Additional required modules:
  * passlib
  
  ```pip install passlib```
  
  * PyCrypto
  
  ```easy_install http://www.voidspace.org.uk/python/pycrypto-2.6.1/pycrypto-2.6.1.win32-py2.7.exe```
  
  * PIL
  
  ```pip install pillow```
