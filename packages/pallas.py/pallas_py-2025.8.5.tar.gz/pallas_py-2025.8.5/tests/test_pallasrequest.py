import json

import pytest
from requests.models import Response

from pallas.utils.PallasRequest import PallasRequest
from posix import remove

def __get_file_data__(filepath:str) -> str:
    with open(filepath, 'r') as f:
        ret = f.read()
    return ret

def test_modify_response_pass():
    sample_content = __get_file_data__('assets/pallas_base64.txt')

    sample = Response()
    sample.status_code = 200
    sample.headers["Content-Type"] = "application/json"
    sample._content = sample_content.encode("utf-8")
    sample.encoding = "utf-8"

    expected_resp = __get_file_data__('assets/pallas_base64_decoded.json')
    expected_resp = json.dumps(json.loads(expected_resp))

    pr = PallasRequest()
    (resp,resp_len) = pr._modify_response(sample)
    if len(json.dumps(json.loads(resp))) < resp_len:
        resp = json.dumps(json.loads(resp))
    assert resp == expected_resp
    assert len(resp) == len(expected_resp)
    assert len(resp) == resp_len

def test_modify_response_fail():
    sample_content = __get_file_data__('assets/pallas_base64_decoded.json')

    sample = Response()
    sample.status_code = 200
    sample.headers['Content-Type'] = 'application/json'
    sample._content = sample_content.encode('utf-8')
    sample.encoding = 'utf-8'

    expected_resp = sample_content
    expected_resp = json.dumps(json.loads(expected_resp))

    pr = PallasRequest()
    (resp, resp_len) = pr._modify_response(sample)
    try:
        if len(json.dumps(json.loads(resp))) < resp_len:
            resp = json.dumps(json.loads(resp))
    except Exception as ex:
        #Knowingly, this probably won't work, but testing using mostly* the same logic as above
        pass
    assert resp != expected_resp
    assert len(resp) != expected_resp
    assert len(resp) == resp_len

def test_unit_remove_asset_receipts():
    sample = {
        "Assets": [
            {
                "_AssetReceipt": "",
                "AssetName": ""
            },
            {
                "AssetName": ""
            }
        ]
    }
    expected_resp = dict(sample) #Duplicate dict so we can properly run out test
    del expected_resp["Assets"][0]["_AssetReceipt"]

    pr = PallasRequest()
    resp = pr.remove_asset_receipts(sample)

    assert resp == expected_resp

def test_unit_remove_asset_receipts_no_change():
    sample = {"Assets":[{"F":"", "E": ""}]}

    pr = PallasRequest()
    resp = pr.remove_asset_receipts(sample)

    assert resp == sample
