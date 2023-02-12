from enum import Enum


class PROFILE(str, Enum):
    FULL = "full"
    ITERATE = "iterate"
    BUILD = "build"
    RUN = "run"
    VIEW = "view"


class GKE_RELEASE_CHANNELS(str, Enum):
    RAPID = "RAPID"
    REGULAR = "REGULAR"
    STABLE = "STABLE"
    NONE = "None"
