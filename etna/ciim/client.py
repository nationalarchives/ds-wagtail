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

        try:
            result = response.get("data", [])[0].get("@template", {}).get("details", {})
            return result
        except Exception as e:
            return {"error": str(e)}

    def get_record_list(self, path: str = "/search"):
        """
        Get a list of records from the CIIM API.
        """
        response = self.get(path=path, headers={})
        
        try:
            results = response.get("data", [])
            total = response.get("stats", {}).get("total", 0)
            return results, total
        except Exception as e:
            return {"error": str(e)}
