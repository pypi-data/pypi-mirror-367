# pallas.py

A library to support making requests to Apple's Pallas server (gdmf.apple.com and mesu.apple.com). More info on [The Apple Wiki](https://theapplewiki.com/wiki/MobileAsset).

## Installation

Using pip

```bash
cd ~/Downloads/
mkdir pallas-py && cd pallas-py
curl "https://github.com/Riigess/pallas.py/archive/refs/heads/main.zip" -o main.zip
unzip main.zip
pip3 install ./
```

## Usage

You can either use this as a Python 3.9+ module, or as a CLI tool. You can find the module docs [here](docs/).

### CLI Tool Reference

Good news! The tool supports argparse. Here's a sample of that output as it stands.

```bash
$ pallas -h

```

## Acknowledgements

I don't take any responsibility for your use of this library. This is **purely** for educational purposes only.

- [@Nicolás17](https://github.com/nicolas17) for providing insights on [pallas-archive](https://gitlab.com/nicolas17/pallas-archive) over on gitlab
- [@r00tfs](https://github.com/R00tFS) and [@dhinakg](https://github.com/dhinakg) for validating the work and making sure I'm not backtracking the entire way through the project (sanity checking is always good)
- [@Siguza](https://github.com/Siguza) Bruh called me ChatGPT, so I had to finish the project. Betting he's still labeling me as nothing more than ChatGPT..

## Notes

In order to query Pallas, you need to use JSON Web Tokens (JWTs) and Base64 for encryption/decryption. A request may look like

```json
{
    "AssetAudience": "02d8e57e-dd1c-4090-aa50-b4ed2aef0062",
    "AssetType": "com.apple.MobileAsset.UAF.Siri.UnderstandingNLOverrides",
    "ClientVersion": 2,
    "CertIssuanceDay": "2023-12-10",
    "DeviceName": "Mac",
    "TrainName": "GlowSeed"
}
```

### AssetAudience

There are likely hundreds, if not thousands, of Asset Audiences used for groups of Assets. When Pallas generates a response, it is able to provide this information without using the device's generic audience. What is attached to this library is the generic asset audience for the OS you would like to query. In this example, we're using the corresponding [Audience.macos_generic](src/utils/Audience.py#L4) audience.

### AssetType

This is typically an identifier for different assets. This can also expose information such as the daemon owner of a particular asset. As provided in this example, MobileAsset is the daemon responsible for fetching and maintaining UAF.Siri.UnderstandingNLOverrides on-device.

### DeviceName

I am personally a little surprised this is even a field in here since the TrainName and AssetAudience should be enough of an identifier for Pallas to establish what device is making a query and how it should respond. This is as generic as it gets. Examples of this are "Mac", "iPhone", "Apple Watch", etc.. (see [DeviceType.py](src/utils/DeviceType.py) for more known references)

### TrainName

Each OS release will have a few variations on the train names. For instance, DawnESeed, DawnFSeed, GlowSeed, GlowBSeed, etc. These OS names can be found in the device's IPSW BuildManifest.plist. Sometimes leaks for these names ([iOS 27](https://www.macworld.com/article/2836234/forget-ios-26-take-a-stroll-through-apples-garden-of-os-code-names-for-2027.html), [iOS 26](https://www.macrumors.com/2024/06/30/apple-starts-work-on-ios-19-and-macos-16/), [iOS 18](https://www.macrumors.com/2023/12/20/ios-18-code-four-new-iphone-models/), [iOS 17](https://www.macrumors.com/2023/03/26/ios-17-to-provide-several-most-requested-features/), ...) show up. I'm not able to validate any of this information (I simply don't know), but if a rumor shows up I will add the original source if it's added to this library for any references of pre-release information.

## Requests

Please note that if you make a request given the above format only will result in larger than normal dumps of information. Devices don't download the generic assets as this results in 1 -> 10MB in some cases for a JWT response from Pallas. Example response may look like something like this;

```json
{
    "Nonce": "",
    "PallasNonce": "........-....-....-....-........",
    "SessionId": "",
    "LegacyXmlUrl": "",
    "PostingDate": "YYYY-MM-DD",
    "Transformations":{
        "_Measurement":"data",
        "SEPDigest":"data",
        "RSEPDigest":"data"
    },
    "Assets":[
        {
            "ArchiveDecryptionKey":"",
            "ArchiveDecryptionKeyFile":"",
            "ArchiveID":"",
            "AssetFormat":"AppleArchive",
            "AssetSpecifier":"com.apple.siri.understanding.nl.overrides.en_GB",
            "AssetType":"com.apple.MobileAsset.UAF.Siri.Understanding",
            "AssetVersion":"3304.2400.1720760365.100.134,0",
            "AssetVersionInfo":{
                "AssetVersionGroup":0,
                "AssetVersionLong":"3304.2400.1720760365.100.134,0",
                "AssetVersionTuple":"3304.2400.1720760365.100.134",
                "BuildVersionTuple":"",
                "BundleVersionTuple":"3304.2400.1720760365"
            },
            "Build":"100G134",
            "Factor":"com.apple.siri.understanding.nl.overrides.en_GB",
            "_CompressionAlgorithm":"AppleArchive",
            "_DownloadSize":65536,
            "_ISMAAutoAsset":true,
            "_Measurement":"",
            "_MeasurementAlgorithm":"SHA-1",
            "_PreSoftwareUpdateAssetStaging":false,
            "_UnarchivedSize":1,
            "__BaseURL":"",
            "__CanUseLocalCacheServer":true,
            "__RelativePath":"",
            "version":"3304.2400.1720760365",
            "_OSVersionCompatibilities":{}
            "Ramp":false
        },
        ...
    ]
}
```

This is (almost) a real partial from a response for an `NLOverrides` 'asset' with locale `en_GB`. A few of the keys will be modified but should still be present in the final response as well.

- `PallasNonce` has been replaced with periods (`.`) to represent an alphanumeric character equal to the length of the original string in place.
- `_OSVersionCompatibilities` has been truncated to remove all capable devices
- `_UnarchivedSize` has been truncated to represent a positive integer response
- `_Measurement` is typically a String equal to the (\_MeasurementAlgorithm) hash of the asset after downloading
- `__BaseURL` and `__RelativePath` have both been removed to not point to a specific URL to download this version
- `_DecryptionKey` and `_DecryptionKeyFile` have both been removed to display the keys with no specific significance being brought to accessing the asset in this example
- `AssetFormat` can be either "AppleArchive" or "AppleEncryptedArchive", usually expect "AppleArchive" here

Everything else usually matches formatting at least.
