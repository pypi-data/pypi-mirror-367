from enum import Enum
from pallas.utils.DeviceType import DeviceType

class OSTrainDevicePair(Enum):
    DawnSeed = "DawnSeed", "17.0", DeviceType.iPhone, DeviceType.iPad
    DawnBSeed = "DawnBSeed", "17.1", DeviceType.iPhone, DeviceType.iPad
    DawnCSeed = "DawnCSeed", "17.2", DeviceType.iPhone, DeviceType.iPad
    DawnDSeed = "DawnDSeed", "17.3", DeviceType.iPhone, DeviceType.iPad
    DawnESeed = "DawnESeed", "17.4", DeviceType.iPhone, DeviceType.iPad
    DawnFSeed = "DawnFSeed", "17.5", DeviceType.iPhone, DeviceType.iPad
    DawnGSeed = "DawnGSeed", "17.6", DeviceType.iPhone, DeviceType.iPad
    CrystalSeed = "CrystalSeed", "18.0", DeviceType.iPhone, DeviceType.iPad
    CrystalBSeed = "CrystalBSeed", "18.1", DeviceType.iPhone, DeviceType.iPad
    CrystalCSeed = "CrystalCSeed", "18.2", DeviceType.iPhone, DeviceType.iPad
    CrystalDSeed = "CrystalDSeed", "18.3", DeviceType.iPhone, DeviceType.iPad
    CrystalESeed = "CrystalESeed", "18.4", DeviceType.iPhone, DeviceType.iPad
    CrystalFSeed = "CrystalFSeed", "18.5", DeviceType.iPhone, DeviceType.iPad
    CrystalGSeed = "CrystalGSeed", "18.6", DeviceType.iPhone, DeviceType.iPad
    CrystalHSeed = "CrystalHSeed", "18.7", DeviceType.iPhone, DeviceType.iPad
    CheerSeed = "CheerSeed", "26.0", DeviceType.iPhone, DeviceType.iPad
    LighthouseSeed = "LighthouseSeed", "10.0", DeviceType.Watch
    LighthouseBSeed = "LighthouseBSeed", "10.1", DeviceType.Watch
    LighthouseCSeed = "LighthouseCSeed", "10.2", DeviceType.Watch
    LighthouseDSeed = "LighthouseDSeed", "10.3", DeviceType.Watch
    LighthouseESeed = "LighthouseESeed", "10.4", DeviceType.Watch
    LighthouseFSeed = "LighthouseFSeed", "10.5", DeviceType.Watch
    LighthouseGSeed = "LighthouseGSeed", "10.6", DeviceType.Watch
    LighthouseHSeed = "LighthouseHSeed", "10.7", DeviceType.Watch
    MoonstoneSeed = "MoonstoneSeed", "11.0", DeviceType.Watch
    MoonstoneBSeed = "MoonstoneBSeed", "11.1", DeviceType.Watch
    MoonstoneCSeed = "MoonstoneCSeed", "11.2", DeviceType.Watch
    MoonstoneDSeed = "MoonstoneDSeed", "11.3", DeviceType.Watch
    MoonstoneESeed = "MoonstoneESeed", "11.4", DeviceType.Watch
    MoonstoneFSeed = "MoonstoneFSeed", "11.5", DeviceType.Watch
    MoonstoneGSeed = "MoonstoneGSeed", "11.6", DeviceType.Watch
    MoonstoneHSeed = "MoonstoneHSeed", "11.7", DeviceType.Watch
    NepaliSeed = "NepaliSeed", "26.0", DeviceType.Watch
    SunburstSeed = "SunburstSeed", "14.0", DeviceType.Mac
    SunburstBSeed = "SunburstBSeed", "14.1", DeviceType.Mac
    SunburstCSeed = "SunburstCSeed", "14.2", DeviceType.Mac
    SunburstDSeed = "SunburstDSeed", "14.3", DeviceType.Mac
    SunburstESeed = "SunburstESeed", "14.4", DeviceType.Mac
    SunburstFSeed = "SunburstFSeed", "14.5", DeviceType.Mac
    SunburstGSeed = "SunburstGSeed", "14.6", DeviceType.Mac
    SunburstHSeed = "SunburstHSeed", "14.7", DeviceType.Mac
    GlowSeed = "GlowSeed", "15.0", DeviceType.Mac
    GlowBSeed = "GlowBSeed", "15.1", DeviceType.Mac
    GlowCSeed = "GlowCSeed", "15.2", DeviceType.Mac
    GlowDSeed = "GlowDSeed", "15.3", DeviceType.Mac
    GlowESeed = "GlowESeed", "15.4", DeviceType.Mac
    GlowFSeed = "GlowFSeed", "15.5", DeviceType.Mac
    GlowGSeed = "GlowGSeed", "15.6", DeviceType.Mac
    GlowHSeed = "GlowHSeed", "15.7", DeviceType.Mac
    LuckSeed = "LuckSeed", "26.0", DeviceType.Mac
    BorealisSeed = "BorealisSeed", "1.0", DeviceType.Vision_Pro
    BorealisESeed = "BorealisESeed", "1.1", DeviceType.Vision_Pro
    BorealisFSeed = "BorealisFSeed", "1.2", DeviceType.Vision_Pro
    BorealisGSeed = "BorealisGSeed", "1.3", DeviceType.Vision_Pro
    ConstellationSeed = "ConstellationSeed", "2.0", DeviceType.Vision_Pro
    ConstellationBSeed = "ConstellationBSeed", "2.1", DeviceType.Vision_Pro
    ConstellationCSeed = "ConstellationCSeed", "2.2", DeviceType.Vision_Pro
    ConstellationDSeed = "ConstellationDSeed", "2.3", DeviceType.Vision_Pro
    ConstellationESeed = "ConstellationESeed", "2.4", DeviceType.Vision_Pro
    ConstellationFSeed = "ConstellationFSeed", "2.5", DeviceType.Vision_Pro
    ConstellationGSeed = "ConstellationGSeed", "2.6", DeviceType.Vision_Pro
    ConstellationHSeed = "ConstellationHSeed", "2.7", DeviceType.Vision_Pro
    DiscoverySeed = "DiscoverySeed", "26.0", DeviceType.Vision_Pro
    Null = "Null", "26.0", DeviceType.TV

    def lookup(ostdp):
        return ostdp.value[1]
