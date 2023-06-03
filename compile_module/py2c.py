import pathlib
import subprocess
import sys
import os
working_dir = pathlib.Path(__file__).parent.parent.__str__()
def get_content(file_path:str):
    file_name = pathlib.Path(file_path).name
    r = f"" \
        f"import pathlib\n" \
        f"from setuptools import setup\n" \
        f"from Cython.Build import cythonize\n" \
        f"import os\n" \
        f"build_dir = pathlib.Path(__file__).parent.__str__()\n" \
        f"file_path=os.path.join(build_dir, '{file_name}')\n" \
        f"setup(\n" \
        f"name='files_services',\n" \
        f"ext_modules=cythonize(file_path),\n" \
        f"zip_safe=True,\n" \
        f"packages=['{file_name}'])\n"
    return r
if len(sys.argv)<2:
    print("miss directory to module")
compile_dir = sys.argv[1]
full_compiler_dir = os.path.join(working_dir,compile_dir)
root_dir,dirs,files = list(os.walk(full_compiler_dir))[0]
files_list = []
for file in files:
    if file=="__init__.py":
        continue
    if os.path.splitext(file)[1]!=".py": continue
    if file.startswith("compiler."): continue
    compile_file = f"compiler.{file}"
    full_path_to_compile_file = os.path.join(root_dir,compile_file)
    content = get_content(os.path.join(root_dir,file))
    if not os.path.exists(full_path_to_compile_file):
        with open(full_path_to_compile_file,"w+") as f:
            f.write(content)
    files_list +=[compile_file]
os.chdir(working_dir)

for f in files_list:
    print(f"Compile file {f}")

    cmd_compile = f"{sys.executable} {f}  build_ext --inplace"
    # subprocess.Popen(cmd_compile, cwd=root_dir)

    ret = subprocess.check_output([
         sys.executable,os.path.join(compile_dir,f),
        'build_ext','--inplace'])
    str_ret= ret.decode('utf8')
    print(str_ret)
    #python cy_es/setup.py build_ext --inplace
