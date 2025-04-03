from etna.core.api import JSONAPIClient

class CIIMClient(JSONAPIClient):
    """
    Client for interacting with the CIIM API.
    """
    def get_record_instance(self, path: str = "/get"):
        """
        Get a single record instance from the CIIM API.
        """
        response = self.get(path=path, headers={})
        return response
    
    def get_record_list(self, path: str = "/search"):
        """
        Get a list of records from the CIIM API.
        """
        response = self.get(path=path, headers={})
        return response