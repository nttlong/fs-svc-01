import cy_kit
from cyx.vn_predictor import VnPredictor
from cyx.rdr_segmenter.segmenter_services import VnSegmenterService
vn_predictor=cy_kit.singleton(VnPredictor)
vn_segmenter_service =cy_kit.singleton(VnSegmenterService)
import uuid
import datetime
def convert_to_vn_predict_seg(data,handler,segment_handler):
    def __is_date__(str_date):
        try:
            datetime.datetime.strptime(str_date[0:26] + 'Z', '%Y-%m-%dT%H:%M:%S.%fZ')
            return True
        except Exception as e:
            return False
        str_date_time = str_date.split('+')[0]
        try:
            t = datetime.datetime.strptime(str_date_time, '%Y-%m-%dT%H:%M:%S.%f')
            tz = datetime.datetime.strptime(str_date.split('+')[1], "%H:%M")
            ret = t + datetime.timedelta(tz.hour)
            return True
        except Exception as e:
            return False

    def __is_valid_uuid__(value):
        try:
            uuid.UUID(str(value))

            return True
        except ValueError:
            return False
    def add_more_content(data,handler,segment_handler):
        if isinstance(data,dict):
            ret = {}
            for k,v in data.items():
                x, y, z = add_more_content(v,handler,segment_handler)
                if y and y!=x:
                    ret[f"{k}_vn_predict"] = y
                if z:
                    ret[f"{k}_seg"] = z
                ret[k] = x
            return ret,None,None
        elif isinstance(data,str):
            if not " " in data:
                return data,None,None
            if __is_valid_uuid__(data):
                return data,None,None
            elif __is_date__(data):
                return data, None,None
            else:
                return data,handler(data),segment_handler(handler(data))
        elif isinstance(data,list):
            n_list = []
            for item in data:
                x, y, z = add_more_content(item, handler, segment_handler)
                if y and y != x:
                    n_list+=[y]
                if z:
                    n_list+=[z]
                n_list += [x]
            return n_list,None,None
        else:
            return data, None,None

    ret, _, _ = add_more_content(data,handler,segment_handler)
    return ret


fx= {
"data_item" : {
            "FullFileName" : "e34fbc98-b9bb-4b3e-9d03-a73f42c49079/Quản lí nhân sự.pdf",
            "FileName" : "Quản lí nhân sự.pdf",
            "RegisterOnYears" : 2023,
            "LastModifiedOn" : "2023-04-06T10:03:06.312000",
            "SizeInBytes" : 182640,
            "FullFileNameWithoutExtenstion" : "e34fbc98-b9bb-4b3e-9d03-a73f42c49079/Quản lí nhân sự",
            "MainFileId" : "642e98daa8f377eacd115ec5",
            "MimeType" : "application/pdf",
            "RegisterOnMonths" : 4,
            "RegisteredBy" : "default",
            "ChunkSizeInBytes" : 2097152,
            "NumOfChunksCompleted" : 1,
            "FileModuleController" : "cyx.common.file_storage_mongodb:MongoDbFileService",
            "IsPublic" : True,
            "ProcessHistories" : [ ],
            "SizeUploaded" : 182640,
            "RegisterOnSeconds" : 6,
            "RegisterOn" : "2023-04-06T10:03:06.312000",
            "Status" : 1,
            "FullFileNameWithoutExtenstionLower" : "e34fbc98-b9bb-4b3e-9d03-a73f42c49079/quản lí nhân sự",
            "HasThumb" : True,
            "FileExt" : "pdf",
            "RegisterOnDays" : 6,
            "RegisterOnMinutes" : 3,
            "FileNameLower" : "quản lí nhân sự.pdf",
            "AvailableThumbSize" : "60,200,450,900",
            "SizeInHumanReadable" : "182.6 kB",
            "Privileges" : { },
            "ServerFileName" : "e34fbc98-b9bb-4b3e-9d03-a73f42c49079.pdf",
            "FileNameOnly" : "Quản lí nhân sự",
            "_id" : "e34fbc98-b9bb-4b3e-9d03-a73f42c49079",
            "NumOfChunks" : 1,
            "FullFileNameLower" : "e34fbc98-b9bb-4b3e-9d03-a73f42c49079/quản lí nhân sự.pdf",
            "ChunkSizeInKB" : 2048.0,
            "RegisterOnHours" : 10,
            "ClientPrivileges" : [ ]
          }
}

vx = convert_to_bm25_seg(fx,vn_predictor.get_text,vn_segmenter_service.parse_word_segment)
print(vx)