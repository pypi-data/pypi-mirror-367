from productservice.Utils import ProductServiceUtils
import inspect
from datetime import datetime as Datetime

class ProductService:
    def __init__(self, base_url="https://product.countrydelight.in/", service_name="unknown-service"):
        self.base_url = base_url
        self.service_name = service_name

    def get_caller_method():
        frame = inspect.currentframe()
        caller_frame = frame.f_back
        return caller_frame.f_code.co_name
    
    def common_header(self):
        return {
            "Content-Type": "application/json",
            "Accept-Encoding": "gzip, deflate, br",
            "x-caller-method": self.get_caller_method(),
            "x-adaptor-version": "1.0.0",
            "x-service-name": self.service_name,
            "x-request-start-time": Datetime.now().isoformat(),
            "Accept": "application/json"
        }

    def fetchProducts(self, customerId, showOnlyCustomerVisible):
        headers = self.common_header()
        return ProductServiceUtils.getGetResponse(self.base_url + f'products/fetchProducts?customerId={customerId}&showOnlyCustomerVisible={showOnlyCustomerVisible}', headers)


    def listProducts(self, payload):
        headers = self.common_header()
        return ProductServiceUtils.getPostResponse(self.base_url + "product/list", payload, headers)
        
    