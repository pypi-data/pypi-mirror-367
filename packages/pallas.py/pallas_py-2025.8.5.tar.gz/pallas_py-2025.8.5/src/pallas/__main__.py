import argparse
from typing import Union
import os
import logging
import json

from pallas.asset import Asset
from pallas.utils.DeviceType import DeviceType
from pallas.utils.Assets import Assets, UAFAssets, EnumUtils
from pallas.utils.Audience import Audience
from pallas.utils.OSTrainDevicePair import OSTrainDevicePair
from pallas.actions.Fetching import Fetching
from pallas.actions.Saving import Saving

#Code yoinked from - https://stackoverflow.com/questions/384076/how-can-i-color-python-logging-output/71215589
class TerminalColor:
    MAGENTA = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    GREY = '\033[0m' # normal
    WHITE = '\033[1m' # bright white
    UNDERLINE = '\033[4m'

def main_argparse() -> argparse.ArgumentParser:
    #arg parse for assets
    parser = argparse.ArgumentParser("PallasRequester", "pallasrequester --ios --asset com.apple.MobileAsset.UAF.FM.Overrides")
    # parser.add_argument("--unified-asset-framework", "-u", action="store_true", default=False, help="Fetches the active asset information for the UnifiedAssetFramework (UAF).") #Removing batched commands in favor of individual queries (re-run the command to get batched responses)
    parser.add_argument("--list-assets", "-ids", default=False, action="store_true", help="Lists all available assets (ex. com.apple.MobileAsset.MacSoftwareUpdate)")
    parser.add_argument("--asset", "-a", default="", action="store", help="Specifies a specific asset to fetch")
    #arg parse for device types
    parser.add_argument("--ios", "-i", default=False, action="store_true", help="Specifies DeviceType as iPhone")
    parser.add_argument("--mac", "-m", default=False, action="store_true", help="Specifies DeviceType as Mac")
    parser.add_argument("--apple-tv", "--tv", default=False, action="store_true", help="Specifies DeviceType as Apple TV")
    parser.add_argument("--vision-pro", "--vision-os", "--xros", "-p", default=False, action="store_true", help="Specifies DeviceType as Vision Pro (not iPod)", required=False)
    parser.add_argument("--apple-watch", "--watch", "-w", default=False, action="store_true", help="Specifies DeviceType as Apple Watch (not a specific watch model)", required=False)
    #arg parse for OSes
    parser.add_argument("--latest", "--current", "-l", default=False, action="store_true", required=False, help="Targets latest OS, which should be macOS 15.6/iOS 18.6-aligned")
    parser.add_argument("--beta", "-b", default=False, action="store_true", required=False, help="Targets major beta release, in this case that would be OS 26.0")
    parser.add_argument("--custom-os", "-custom", "-c", default=False, action="store_true", required=False, help="Allows you to specify an OS listed in --list-os")
    parser.add_argument("--list-os", "--list-oses", "-o", default=False, action="store_true", required=False, help="Displays all available OSes at this time")
    parser.add_argument("--save-file", "-f", default="", action="store", required=False)
    return parser


def get_uaf_assets() -> dict:
    DawnESeed_Assets = [
        UAFAssets.SiriDialogAssets,
        UAFAssets.SiriFindMy,
        UAFAssets.SiriPlatformAssets,
        UAFAssets.SiriUnderstanding,
        UAFAssets.SiriUnderstandingASRHammer,
        UAFAssets.SiriUnderstandingNLOverrides
    ]
    CrystalSeed_Assets = EnumUtils().list_members(UAFAssets)
    del CrystalSeed_Assets['FMVisual']
    del CrystalSeed_Assets['FMVisual']
    return {
        OSTrainDevicePair.DawnESeed: {
            "Device": DeviceType.iPhone,
            "Audience": Audience.ios_generic,
            "Assets": DawnESeed_Assets
        },
        OSTrainDevicePair.CrystalSeed: {
            "Device": DeviceType.Mac,
            "Audience": Audience.macos_generic,
            "Assets": CrystalSeed_Assets
        },
        OSTrainDevicePair.CrystalESeed: {
            "Device": DeviceType.Mac,
            "Audience": Audience.macos_generic,
            "Assets": EnumUtils().list_members(Assets)
        }
    }


def get_assets(assets: dict, key: OSTrainDevicePair):
    otdp = assets[key]
    device = otdp["Device"]
    if device == DeviceType.iPhone or DeviceType.iPad:
        return fetch.get_ios_asset_group(assets=otdp["Assets"], os_train=key)
    elif device == DeviceType.Mac:
        return fetch.get_macos_asset_group(assets=otdp["Assets"], os_train=key)
    elif device == DeviceType.TV:
        return fetch.get_tvos_asset_group(assets=otdp["Assets"], os_train=key)
    elif device == DeviceType.Watch:
        return fetch.get_watchos_asset_group(assets=otdp["Assets"], os_train=key)
    else:
        raise RuntimeError(
            "Error, unknown device provided please review __main__.py:get_assets(list[Assets],OSTrainDevicePair)")


def append_assets(assets: list[Asset], file_name: str) -> bool:
    store = Saving(file_name)
    if not store.sqlite_exists():
        store.configure_sqlite()
    for asset in assets:
        store.append_asset_to_sqlite(asset=asset)
    return store.sqlite_exists()


if __name__ == "__main__":
    arg_parser = main_argparse()
    args = arg_parser.parse_known_args()[0]
    #In case it's not already part of argparser (for some odd reason)
    if "help" in args or "h" in args:
        arg_parser.print_help()
        exit()

    fetch = Fetching()
    # This is caching logic, I need to add better invalidation logic to handle what happens before noon PT vs after here
    sqlite_file = f"{os.getcwd()}/database.sqlite"
    eus = EnumUtils()
    if args.list_assets:
        for e in eus.list_members(Assets):
            print(f"- {str(e).split('.')[-1]}")
        print("\n----- UAF -----")
        for e in eus.list_members(UAFAssets):
            print(f"- {str(e).split('.')[-1]}")
        exit()
    elif args.list_os:
        for e in eus.list_members(OSTrainDevicePair):
            if "Null" in e.value[0]:
                continue
            if type(e.value[1]) is str and ".0" not in e.value[1]:
                print("\t", end='')
            print(f"- {e.value[0]} ({e.value[1]})")
        exit()

    if not args.ios and not args.mac and not args.vision_pro and not args.apple_tv and not args.apple_watch:
        raise Exception("At least one device must be selected")

    if not args.asset:
        raise Exception("Asset must be specified")

    asset_identifier = eus.lookup(args.asset)
    if type(asset_identifier) not in [Assets, UAFAssets]:
        raise Exception(f"Cannot find asset for string \"{asset_identifier}\"")

    device = DeviceType.Mac
    if args.ios:
        device = DeviceType.iPhone
    if args.apple_tv:
        device = DeviceType.TV
    if args.vision_pro:
        device = DeviceType.Vision_Pro
    if args.apple_watch:
        device = DeviceType.Watch

    os = OSTrainDevicePair.CheerSeed
    if args.__getattribute__("beta") and args.beta:
        if device == DeviceType.Mac:
            os = OSTrainDevicePair.LuckSeed
        elif device == DeviceType.Vision_Pro:
            os = OSTrainDevicePair.DiscoverySeed
        elif device == DeviceType.Watch:
            os = OSTrainDevicePair.NepaliSeed
        #else, this should be CheerSeed
    elif args.__getattribute__("latest") and args.latest:
        if device == DeviceType.Mac:
            os = OSTrainDevicePair.GlowGSeed
        elif device == DeviceType.iPhone:
            os = OSTrainDevicePair.CrystalGSeed
        elif device == DeviceType.Vision_Pro:
            os = OSTrainDevicePair.ConstellationGSeed
        elif device == DeviceType.Watch:
            os = OSTrainDevicePair.MoontstoneGSeed
    elif args.__getattribute__("custom_os") and args.custom_os:
        for seed in EnumUtils().list_members(OSTrainDevicePair):
            if seed.value[-1] == device and seed.value[0]:
                os = seed
                break
    else:
        raise Exception("Error: You must specify an OS")

    resp = get_assets({os: {"Assets":[asset_identifier], "Device": device}}, os) #I think this might work.. if not, I'll find out
    if args.save_file != "":
        with open(args.save_file, 'w') as f:
            f.write(json.dumps(resp[0].raw_response, indent=4, separators=(',',':')))
    else:
        print("Response:", json.dumps(resp[0].raw_response))
