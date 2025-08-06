from funasr import AutoModel
from funasr.utils.postprocess_utils import rich_transcription_postprocess
import time

def sensorvoice_funasr(audio_path):
    start_time = time.perf_counter()
    model_dir = "iic/SenseVoiceSmall"

    model = AutoModel(
        model=model_dir,
        trust_remote_code=True,
        remote_code="./model.py",  
        vad_model="fsmn-vad",
        vad_kwargs={"max_single_segment_time": 30000},
        device="cpu",
    )

    res = model.generate(
        input=audio_path,
        cache={},
        language="zn",  # "zn", "en", "yue", "ja", "ko", "nospeech"
        use_itn=True,
        batch_size_s=60,
        merge_vad=True,  #
        merge_length_s=15,
    )
    text = rich_transcription_postprocess(res[0]["text"])
    end_time = time.perf_counter()
    print(text)
    print(f"Time taken: {end_time - start_time} seconds")
    return text

def paraformer_funasr(audio_path):
    start_time = time.perf_counter()
    model = AutoModel(model="paraformer-zh", model_revision="v2.0.4",
                    vad_model="fsmn-vad", vad_model_revision="v2.0.4",
                    punc_model="ct-punc-c", punc_model_revision="v2.0.4",
                    spk_model="cam++", spk_model_revision="v2.0.2",
                    )
    text = model.generate(input="test-short.wav", 
                batch_size_s=300, 
                hotword='')
    end_time = time.perf_counter()
    print(text)
    print(f"Time taken: {end_time - start_time} seconds")
    return text