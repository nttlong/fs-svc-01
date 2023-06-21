import sys
import os
if sys.version_info.major==3 and sys.version_info.minor ==9 and sys.version_info.micro==5:
    print(sys.version)
else:
    raise Exception(
        f"invalid python3 version. Desire 3.9.5 but found {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro} \n"
        f"in {sys.executable}")
if not os.path.isfile("/usr/bin/soffice"):
    raise Exception("'/usr/bin/soffice' was not found")