import requests

class ProductCategorizationAPI:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://www.productcategorization.com/api/"
    
    def categorize_text(self, text, confidence=0, expand_context=0):
        params = {
            "query": text,
            "api_key": self.api_key,
            "confidence": str(confidence),
            "expand_context": str(expand_context)
        }
        response = requests.get(self.base_url + "ecommerce/ecommerce_category6_get.php", params=params)
        return response.json()

    def categorize_url(self, url):
        payload = {
            'query': url,
            'api_key': self.api_key,
            'data_type': 'url'
        }
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        response = requests.post(self.base_url + "iab/iab_web_content_filtering_url.php", data=payload, headers=headers)
        return response.json()

    def categorize_image(self, image_url, text="", ip="0", login="0"):
        # Download image to memory
        image_response = requests.get(image_url)
        if image_response.status_code != 200:
            return {'error': 'Failed to download image'}
        import io
        image_file = io.BytesIO(image_response.content)
        data = {
            'ip': ip,
            'api_key': self.api_key,
            'login': login,
            'text': text
        }
        files = {
            'image': ('image.jpg', image_file, 'image/jpeg')
        }
        response = requests.post(self.base_url + "ecommerce/ecommerce_shopify_image.php", data=data, files=files)
        return response.json()