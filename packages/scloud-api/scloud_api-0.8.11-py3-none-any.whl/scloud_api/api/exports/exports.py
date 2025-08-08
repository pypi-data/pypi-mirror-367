from scloud_api.base import Client, ApiResponse
import re
class Exports(Client):
    def create_custom_export(self, columns, product_ids, file_format=0) -> ApiResponse:
        data = {
            'Columns': columns,
            'FileFormat': file_format,
            'ProductIds': product_ids
        }
        response = self._request("/api/Catalog/Exports/Custom", "POST", data)

        url = response.payload['QueuedJobLink']
        match = re.search(r'id=(\d+)', url)

        if match:
            payload = {'QueuedJobId': match.group(1)}
            response.payload = payload

        return response