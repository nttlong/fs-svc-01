import sys
if sys.version_info.major!=3 and sys.version_info.minor !=9 and sys.version_info.micro !=5:
    raise Exception(f"invalid python3 version. Desire 3.9.5 but found {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
else:
    print(sys.version)