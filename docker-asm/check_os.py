import sys
if sys.version_info.major==3 and sys.version_info.minor==9 and sys.version_info.micro==5:
    print(sys.version)
else:
    raise Exception(sys.version)
def cmd(ls):
    import subprocess
    ret = subprocess.check_output(ls)
    ret_ttx = ret.decode('utf8')
    return ret_ttx
raise Exception(cmd(["which","soffice"]))