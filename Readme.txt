

Dependences:
- Librairie pymongo
- Un serveur mongodb accessible

Etapes pour démarrer le store sur un serveur mongo situé sur "<ADDRESS IP>:<PORT>" :


from storeEvent import StoreEvent

store = StoreEvent(clientPath="<ADDRESS IP>:<PORT>")

Pour le démarrer sur le serveur par defaut, pas besoin de préciser le clientPath
