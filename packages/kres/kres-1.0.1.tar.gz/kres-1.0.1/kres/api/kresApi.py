import sys
import uvicorn
from getpass import getpass
from fastapi import FastAPI

from kres.encryption.tokenEncryption import TokenEncryption

def setupRoutes():
    kresApi = FastAPI()

    @kresApi.get("/health")
    def health():
        return {"health": "kres-agent is running"}
        
    @kresApi.get("/decrypt")
    def decrypt():
        return {"token": tokenEncryption.decryptToken(encryptedToken)}
    
    return kresApi

if __name__ == "__main__":
    paraphrase = sys.stdin.readline().strip()
    token      = sys.stdin.readline().strip()
    port       = int(sys.argv[1])

    tokenEncryption = TokenEncryption()
    encryptedToken  = tokenEncryption.login(paraphrase, token)

    kresApi = setupRoutes()
    uvicorn.run(app=kresApi, host="127.0.0.1", port=5454)