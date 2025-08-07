import requests

class ProductServiceUtils:
    @staticmethod
    def getPostResponse(url, payload, headers):    
        response = requests.post(url=url, data=payload, headers=headers)

        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()

    @staticmethod
    def getGetResponse(url, headers):    
        response = requests.post(url=url, headers=headers)

        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()
    