import cyx.common.temp_file
import cy_kit
tmp_file = cy_kit.singleton(cyx.common.temp_file.TempFiles)
print(tmp_file.path)