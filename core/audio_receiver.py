import numpy as np
import discord
import grpc
import google.oauth2.service_account
import google.cloud.speech_v1

class GoogleSpeechToText:
    def __init__(self, lang, recognition_model, api_credentials = None):
        endpoint = google.cloud.speech_v1.SpeechClient.SERVICE_ADDRESS
        credentials = google.oauth2.service_account.Credentials.from_service_account_file(api_credentials) if api_credentials else grpc.local_channel_credentials()
        LocalSpeechGrpcTransport = type('LocalSpeechGrpcTransport', (google.cloud.speech_v1.gapic.transports.speech_grpc_transport.SpeechGrpcTransport, ), dict(create_channel = lambda self, address, credentials, **kwargs: grpc.secure_channel(address, credentials, **kwargs)))
        client_options = dict(api_endpoint = endpoint)

        self.client = google.cloud.speech_v1.SpeechClient(credentials = credentials, client_options = client_options) if api_credentials else google.cloud.speech_v1.SpeechClient(transport = LocalSpeechGrpcTransport(address = endpoint, credentials = credentials), client_options = client_options)
        self.lang = lang
        self.recognition_model = recognition_model

    def transcribe(self, pcm_s16le, sample_rate, num_channels):
        res = self.client.recognize(dict(audio_channel_count = num_channels, encoding = 'LINEAR16', sample_rate_hertz = sample_rate, language_code = self.lang, model = self.recognition_model), dict(content = pcm_s16le))
        hyp = res.results[0].alternatives[0].transcript if len(res.results) > 0 else ''
        return hyp



class BufferAudioSink(discord.AudioSink):
    def __init__(self, flush):
        self.flush = flush
        self.NUM_CHANNELS = discord.opus.Decoder.CHANNELS
        self.NUM_SAMPLES = discord.opus.Decoder.SAMPLES_PER_FRAME
        self.SAMPLE_RATE_HZ = discord.opus.Decoder.SAMPLING_RATE
        self.BUFFER_FRAME_COUNT = 500
        self.buffer = np.zeros(shape = (self.NUM_SAMPLES * self.BUFFER_FRAME_COUNT, self.NUM_CHANNELS), dtype = 'int16')
        self.buffer_pointer = 0
        self.speaker = None

    def write(self, voice_data):
        if voice_data.user is None:
            return
        speaker = voice_data.user.id
        frame = np.ndarray(shape = (self.NUM_SAMPLES, self.NUM_CHANNELS), dtype = self.buffer.dtype, buffer = voice_data.data)
        speaking = np.abs(frame).sum() > 0
        need_flush = (self.buffer_pointer >= self.BUFFER_FRAME_COUNT - 2) or (not speaking and self.buffer_pointer > 0.5 * self.BUFFER_FRAME_COUNT) #or (self.speaker is not None and speaker != self.speaker)

        if speaking:
            self.buffer[(self.buffer_pointer * self.NUM_SAMPLES) : ((1 + self.buffer_pointer) * self.NUM_SAMPLES)] = frame
            self.buffer_pointer += 1
            self.speaker = speaker

        if need_flush:
            pcm_s16le = self.buffer.tobytes()
            self.buffer.fill(0)
            self.buffer_pointer = 0
            self.flush(self.speaker, pcm_s16le, self.SAMPLE_RATE_HZ, self.NUM_CHANNELS)