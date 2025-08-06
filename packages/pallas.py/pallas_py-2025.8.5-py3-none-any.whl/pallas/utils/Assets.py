from enum import Enum
from typing import Union, Optional

class Assets(Enum):
    AppleKeyServicesCRL2 = "com.apple.MobileAsset.AppleKeyServicesCRL2"
    CombinedVocalizerVoices = "com.apple.MobileAsset.VoiceServices.CombinedVocalizerVoices"
    ComfortSoundsAssets = "com.apple.MobileAsset.ComfortSoundsAssets"
    CustomVoice = "com.apple.MobileAsset.VoiceServices.CustomVoice"
    ContextKit = "com.apple.MobileAsset.ContextKit"
    CoreSuggestions = "com.apple.MobileAsset.CoreSuggestions"
    CoreSuggestionsModels = "com.apple.MobileAsset.CoreSuggestionsModels"
    DarwinAccessoryUpdate_A2525 = "com.apple.MobileAsset.DarwinAccessoryUpdate.A2525"
    DesktopPicture = "com.apple.MobileAsset.DesktopPicture"
    DictionaryOSX = "com.apple.MobileAsset.DictionaryServices.dictionaryOSX"
    Font7 = "com.apple.MobileAsset.Font7"
    GameController_DB1 = "com.apple.MobileAsset.GameController.DB1"
    GamePolicy_DB1 = "com.apple.MobileAsset.GamePolicy.DB1"
    GeoPolygonDataAssets = "com.apple.MobileAsset.GeoPolygonDataAssets"
    ImageCaptionModel = "com.apple.MobileAsset.ImageCaptionModel"
    IntelligentRouting = "com.apple.MobileAsset.IntelligentRouting"
    iPhoneSoftwareUpdate = "com.apple.MobileAsset.iPhoneSoftwareUpdate" #Unsure, referencing format for MacSoftwareUpdate
    KextDenyList = "com.apple.MobileAsset.KextDenyList"
    LinguisticData = "com.apple.MobileAsset.LinguisticData"
    LinguisticDataAuto = "com.apple.MobileAsset.LinguisticDataAuto"
    MacSoftwareUpdate = "com.apple.MobileAsset.MacSoftwareUpdate"
    MacSplatSoftwareUpdate = "com.apple.MobileAsset.MacSplatSoftwareUpdate"
    MacinTalkVoiceAssets = "com.apple.MobileAsset.MacinTalkVoiceAssets"
    MediaSupport = "com.apple.MobileAsset.MediaSupport"
    NetworkNomicon = "com.apple.MobileAsset.network.networknomicon"
    MobileAccessoryUpdate_A2096_EA = "com.apple.MobileAsset.MobileAccessoryUpdate.A2096.EA"
    MobileAssetBrain = "com.apple.MobileAsset.MobileAssetBrain"
    OSEligibility = "com.apple.MobileAsset.OSEligibility"
    PKITrustSupplementals = "com.apple.MobileAsset.PKITrustSupplementals"
    PhotosCuratedMusicLibraryAsset = "com.apple.MobileAsset.PhotosCuratedMusicLibraryAsset"
    ProactiveEventTrackerAssets = "com.apple.MobileAsset.ProactiveEventTrackerAssets"
    SecExperimentAssets = "com.apple.MobileAsset.SecExperimentAssets"
    SourceEditorAssets = "com.apple.MobileAsset.SourceEditorAssets"
    SpeechTranslationAssets6 = "com.apple.MobileAsset.SpeechTranslationAssets6"
    SpotlightResources = "com.apple.MobileAsset.SpotlightResources"
    TTSAXResourceModelAssets = "com.apple.MobileAsset.TTSAXResourceModelAssets"
    TimeZoneUpdate = "com.apple.MobileAsset.TimeZoneUpdate"
    TopLevelDomainDafsa = "com.apple.MobileAsset.TopLevelDomainDafsa"
    PhoneNumberResolver = "com.apple.MobileAsset.phoneNumberResolver"
    UARP_A2363 = "com.apple.MobileAsset.UARP.A2363"
    UARP_A2452 = "com.apple.MobileAsset.UARP.A2452"
    UARP_A2515 = "com.apple.MobileAsset.UARP.A2515"
    UARP_A2618 = "com.apple.MobileAsset.UARP.A2618"
    WatchSoftwareUpdate = "com.apple.MobileAsset.WatchSoftwareUpdate" #Unsure, referencing format for MacSoftwareUpdate
    VideoAppsMusicAssets3 = "com.apple.MobileAsset.VideoAppsMusicAssets3"
    VoiceTriggerAssetsASMac = "com.apple.MobileAsset.VoiceTriggerAssetsASMac"
    VoiceTriggerAssetsStudioDisplay = "com.apple.MobileAsset.VoiceTriggerAssetsStudioDisplay"

class UAFAssets(Enum):
    FMOverrides = "com.apple.MobileAsset.UAF.FM.Overrides"
    FMCodeLM = "com.apple.MobileAsset.UAF.FM.CodeLM"
    FMGenerativeModels = "com.apple.MobileAsset.UAF.FM.GenerativeModels"
    FMVisual = "com.apple.MobileAsset.UAF.FM.Visual"
    HandwritingSynthesis = "com.apple.MobileAsset.UAF.Handwriting.Synthesis"
    SafariBrowsingAssistant = "com.apple.MobileAsset.UAF.SafariBrowsingAssistant"
    SiriDialogAssets = "com.apple.MobileAsset.UAF.Siri.DialogAssets"
    SiriFindMy = "com.apple.MobileAsset.UAF.Siri.FindMyConfigurationFiles"
    SiriPlatformAssets = "com.apple.MobileAsset.UAF.Siri.PlatformAssets"
    SiriUnderstanding = "com.apple.MobileAsset.UAF.Siri.Understanding"
    SiriUnderstandingASRHammer = "com.apple.MobileAsset.UAF.Siri.UnderstandingASRHammer"
    SiriUnderstandingNLOverrides = "com.apple.MobileAsset.UAF.Siri.UnderstandingNLOverrides"
    SpeechASR = "com.apple.MobileAsset.UAF.Speech.AutomaticSpeechRecognition"
    SummarizationKit = "com.apple.MobileAsset.UAF.SummarizationKitConfiguration"
    IFPlanner = "com.apple.if.planner"
    IFPlannerOverrides = "com.apple.if.planner.overrides"
    IPComputeHammer = "com.apple.intelligenceplatform.IntelligencePlatformComputeService.hammer"
    IPComputeAssistant = "com.apple.intelligenceplatform.IntelligencePlatformComputeService.assistant"
    UAFPlatform = "com.apple.siri.uaf.platform" #TODO: Create generic "No locale" asset flags

class EnumUtils:
    def list_members(self, enum:Enum):
        to_return = []
        for key in enum.__dict__["_member_names_"]:
            to_return.append(enum.__dict__[key])
        return to_return

    def lookup(self, value:str) -> Optional[Union[UAFAssets, Assets]]:
        if '.' in value:
            value = value.split('.')[-1]
        #Check if requested value is in UAFAssets
        lowercased_assets = {asset.lower():asset for asset in UAFAssets.__dict__["_member_names_"]}
        if value.lower() in lowercased_assets:
            return UAFAssets.__dict__[lowercased_assets[value.lower()]]

        #Check if requested value is in Assets
        lowercased_assets = {asset.lower():asset for asset in Assets.__dict__["_member_name_"]}
        if value.lower() in lowercased_assets:
            return Assets.__dict__[lowercased_assets[value.lower()]]
        return None
