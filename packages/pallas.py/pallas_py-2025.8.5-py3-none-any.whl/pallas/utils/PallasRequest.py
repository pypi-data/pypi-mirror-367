import urllib
import json
import ssl
from io import BytesIO
import base64
import http.client
import urllib.parse
from typing import Union

import requests

from pallas.utils.Assets import Assets
from pallas.utils.Assets import UAFAssets
from pallas.utils.Audience import Audience
from pallas.utils.DeviceType import DeviceType
from pallas.utils.OSTrainDevicePair import OSTrainDevicePair

class PallasRequest:
    def __init__(self, url:str = "https://gdmf.apple.com/v2/assets"):
        self.url = url
        self.headers = {
            "Content-Type": "application/json"
        }

    def _modify_response(self, resp) -> tuple[str,int]:
        content_type = None
        if 'Content-Type' in resp.headers:
            content_type = resp.headers['Content-Type']
        if content_type and 'application/json' in content_type:
            body_str = resp.text
            decoded_jwt_body = ""
            if body_str.startswith('e'):
                jwt_body = body_str.split('.')[1]
                decoded_jwt_body = str(base64.urlsafe_b64decode(jwt_body + '=='))[2:-1]
            return decoded_jwt_body, len(decoded_jwt_body)
        return "", 0

    def make_post_request(self, body:str):
        headers = {
            "Host": "gdmf.apple.com",
            "Content-Length": str(len(body))
        }
        headers.update(self.headers) #Update with existing headers
        resp = requests.post(self.url, data=body, headers=headers, verify=False)
        if resp.status_code == 200:
            resp_body, length = self._modify_response(resp)
            if len(resp_body) == length:
                return resp_body
        return f"[ERR] [HTTP {resp.status_code}] {resp.text}"

    def request(self, asset_audience:Audience, asset_type:Union[Assets, UAFAssets], device_type:DeviceType, train_name:OSTrainDevicePair) -> dict:
        body = {
            "AssetAudience": asset_audience.value, #This can be changed to fit other deviceTypes
            "ClientVersion": 2,
            "AssetType": asset_type.value, #This can be changed to other Assets
            "CertIssuanceDay": "2023-12-10",
            "DeviceName": device_type.value, #Can be changed to other DeviceTypes
            "TrainName": train_name.value[0] #Can be changed to other OSTrainDevicePair names (Useful at a quick glance)
        }
        body_dump = json.dumps(body)

        resp = self.make_post_request(body_dump)
        if '{' in resp[0]:
            if type(resp) is str:
                resp = json.loads(resp)
            if type(resp) is dict:
                return resp
            else:
                raise Exception(f"Error: unformatted type for resp {type(resp)}")
        else:
            print(resp)
            raise Exception("Unhandled data format")

    def save_json_to_file(self, data:dict, filename:str):
        with open(filename, 'w') as f:
            f.write(json.dumps(data, indent=4, separators=(',',':')))

    def remove_asset_receipts(self, data:dict) -> dict:
        if 'Assets' in data:
            for asset in data['Assets']:
                if '_AssetReceipt' in asset:
                    del asset['_AssetReceipt']
        return data
