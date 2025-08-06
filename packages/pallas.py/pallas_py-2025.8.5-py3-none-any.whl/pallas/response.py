from datetime import datetime
from pallas.asset import Asset

class Response:
    def __init__(self, response:dict={}):
        self.nonce = response.get("Nonce", None)
        self.pallas_nonce = response.get("PallasNonce", None)
        self.session_id = response.get("SessionId", None)
        self.legacy_xml_url = response.get("LegacyXmlUrl", None)
        self.posting_date = response.get("PostingDate", datetime.now().strftime("%Y-%m-%d"))
        self.posting_date = datetime.strptime(self.posting_date, "%Y-%m-%d")
        self.assets = []
        for asset in response.get("Assets", []):
            self.assets.append(Asset(a_dict=asset))
        self.asset_set_id = response.get("AssetSetId", "")
        self.asset_audience = response.get("AssetAudience", "")
        self.raw_response = response
        if 'Assets' in self.raw_response:
            for i in range(len(self.raw_response['Assets'])):
                if '_AssetReceipt' in self.raw_response['Assets'][i]:
                    del self.raw_response['Assets'][i]['_AssetReceipt']
