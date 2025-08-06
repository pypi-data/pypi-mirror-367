from typing import Union

from pallas.utils.Assets import Assets
from pallas.utils.Assets import UAFAssets
from pallas.utils.Audience import Audience
from pallas.utils.DeviceType import DeviceType
from pallas.utils.OSTrainDevicePair import OSTrainDevicePair
from pallas.utils.PallasRequest import PallasRequest

from pallas.response import Response

class Fetching:
    def __init__(self, url:str="https://gdmf.apple.com/v2/assets"):
        self.url = url

    def __fetch__(self, asset:Union[Assets, UAFAssets], os_train:OSTrainDevicePair, audience:Audience, device_type:DeviceType) -> Response:
        if "pr" not in self.__dict__:
            self.pr = PallasRequest(url=self.url)
        temp = self.pr.request(asset_audience=audience, asset_type=asset, device_type=device_type, train_name=os_train)
        temp = Response(response=temp)
        return temp

    def __fetch_group__(self, assets:list[Union[Assets, UAFAssets]], os_train:OSTrainDevicePair, audience:Audience, device_type:DeviceType) -> list[Response]:
        responses = []
        for asset in assets:
            responses.append(self.__fetch__(asset=asset, os_train=os_train, audience=audience, device_type=device_type))
        return responses

    ## Group Fetching Common Name Functions ##
    def get_macos_asset_group(self, assets:list[Union[Assets, UAFAssets]]=[UAFAssets.SiriPlatformAssets], os_train:OSTrainDevicePair=OSTrainDevicePair.CrystalSeed) -> list[Response]:
        return self.__fetch_group__(assets=assets, os_train=os_train, audience=Audience.macos_generic, device_type=DeviceType.Mac)

    def get_ios_asset_group(self, assets:list[Union[Assets, UAFAssets]]=[UAFAssets.SiriPlatformAssets], os_train:OSTrainDevicePair=OSTrainDevicePair.CrystalSeed) -> list[Response]:
        return self.__fetch_group__(assets=assets, os_train=os_train, audience=Audience.ios_generic, device_type=DeviceType.iPhone)

    def get_tvos_asset_group(self, assets:list[Union[Assets, UAFAssets]]=[UAFAssets.SiriPlatformAssets], os_train:OSTrainDevicePair=OSTrainDevicePair.CrystalSeed) -> list[Response]:
        return self.__fetch_group__(assets=assets, os_train=os_train, audience=Audience.tvos_generic, device_type=DeviceType.TV)

    def get_watchos_asset_group(self, assets:list[Union[Assets, UAFAssets]]=[UAFAssets.SiriPlatformAssets], os_train:OSTrainDevicePair=OSTrainDevicePair.CrystalSeed) -> list[Response]:
        return self.__fetch_group__(assets=assets, os_train=os_train, audience=Audience.watchos_generic, device_type=DeviceType.Watch)


    ## Individual Asset Common Name Functions ##
    def get_macos_asset(self, asset:Union[Assets, UAFAssets]=UAFAssets.SiriPlatformAssets, os_train:OSTrainDevicePair=OSTrainDevicePair.CrystalSeed) -> Response:
        return self.__fetch__(asset=asset, os_train=os_train, audience=Audience.macos_generic, device_type=DeviceType.Mac)

    def get_ios_asset(self, asset:Union[Assets, UAFAssets]=UAFAssets.SiriPlatformAssets, os_train:OSTrainDevicePair=OSTrainDevicePair.CrystalSeed) -> Response:
        return self.__fetch__(asset=asset, os_train=os_train, audience=Audience.ios_generic, device_type=DeviceType.iPhone)

    def get_tvos_asset(self, asset:Union[Assets, UAFAssets]=UAFAssets.SiriPlatformAssets, os_train:OSTrainDevicePair=OSTrainDevicePair.CrystalSeed) -> Response:
        return self.__fetch__(asset=asset, os_train=os_train, audience=Audience.tvos_generic, device_type=DeviceType.TV)

    def get_watchos_asset(self, asset:Union[Assets, UAFAssets]=UAFAssets.SiriPlatformAssets, os_train:OSTrainDevicePair=OSTrainDevicePair.CrystalSeed) -> Response:
        return self.__fetch__(asset=asset, os_train=os_train, audience=Audience.watchos_generic, device_type=DeviceType.Watch)
