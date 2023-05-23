import cy_kit
from cyx.common.share_storage import ShareStorageService

share_storage_service = cy_kit.singleton(ShareStorageService)
fx= share_storage_service.get_root()
print(fx)