import uuid

from pydub import AudioSegment
import math
import cy_kit
from cyx.common.share_storage import ShareStorageService
import os


class AudioService:
    def __init__(self, share_storage_service: ShareStorageService = cy_kit.singleton(ShareStorageService)):
        self.share_storage_service = share_storage_service
        self.processing_folder = self.share_storage_service.get_temp_dir(AudioService)
        if not os.path.isdir(self.processing_folder):
            os.makedirs(self.processing_folder, exist_ok=True)

    def split(self, audio_file: str):
        ret = []
        from pydub import AudioSegment
        from pydub.silence import split_on_silence
        # reading from audio mp3 file
        sound = AudioSegment.from_mp3(audio_file)
        output_dir = os.path.abspath(
            os.path.join(self.processing_folder, str(uuid.uuid4()))
        )
        if not os.path.isdir(output_dir):
            os.makedirs(output_dir,exist_ok=True)
        # spliting audio files
        audio_chunks = split_on_silence(sound, min_silence_len=500, silence_thresh=-40)
        # loop is used to iterate over the output list
        for i, chunk in enumerate(audio_chunks):
            output_file = os.path.join(output_dir, "chunk{0}.mp3".format(i))
            print("Exporting file", output_file)
            chunk.export(output_file, format="mp3")
            ret+=[output_file]
        return ret

