import os
import platform
import re
import json

import torch
import whisper
from whisper.tokenizer import LANGUAGES, TO_LANGUAGE_CODE

from whisper_ui.handle_prefs import USER_PREFS, check_model

SUPPORTED_FILETYPES = ('flac', 'm4a', 'mp3', 'mp4', 'wav')
AVAILABLE_MODELS = whisper.available_models()
VALID_LANGUAGES = sorted(
    LANGUAGES.keys()
) + sorted(
    [k.title() for k in TO_LANGUAGE_CODE.keys()]
)
LANGUAGES_FLIPPED = {v: k for k, v in LANGUAGES.items()}
TO_LANGUAGE_CODE_FLIPPED = {v: k for k, v in TO_LANGUAGE_CODE.items()}

if torch.cuda.is_available():
    DEVICE_NAME = 'cuda'
elif torch.backends.mps.is_available():
    DEVICE_NAME = 'mps'
else:
    DEVICE_NAME = 'cpu'
DEVICE = torch.device(DEVICE_NAME)

class ModelInterface:

    def __init__(self):
        if USER_PREFS['DEBUG']:
            self.model = 'abc'
        else:
            self.model = None
        
    def map_available_language_to_valid_language(self, available_language):
        
        if available_language == 'None':
            return None
        
        al = available_language.lower()
        if al not in VALID_LANGUAGES:
            if al in LANGUAGES_FLIPPED and LANGUAGES_FLIPPED[al] in VALID_LANGUAGES:
                return LANGUAGES_FLIPPED[al]
            elif al in TO_LANGUAGE_CODE_FLIPPED and TO_LANGUAGE_CODE_FLIPPED[al] in VALID_LANGUAGES:
                return TO_LANGUAGE_CODE_FLIPPED[al]
        else:
            return al

    def get_model(self, switch_model: bool = False):
        
        model_name = USER_PREFS["model"]
        
        if not check_model(model_name):
            print(f'\tWarning: model {model_name} not found in cache. Please download it.')
            return
        
        if self.model is None or switch_model:
            print(f'\tLoading model {model_name}. This may take a while if you have never used this model.')
            print(f'\t\tChecking for GPU...')
            
            if DEVICE_NAME == 'cuda' or DEVICE_NAME == 'mps':
                print(f'\t\tGPU found ({DEVICE_NAME}).')
            else:
                print('\t\tNo GPU found. Using CPU.')
            try:
                self.model = whisper.load_model(name=USER_PREFS['model'], device=DEVICE, in_memory=True)
            except:
                print('\t\tWarning: issue loading model onto GPU. Using CPU.')
                self.model = whisper.load_model(name=USER_PREFS['model'], in_memory=True)
            print(f'\tLoaded model {model_name} successfully.')
        else:
            print(f'\tUsing currently loaded model ({model_name}).')
            
        self.model.eval()

    def format_outputs(self, outputs):
        
        text_template = USER_PREFS['text_template']
        segmentation_template = USER_PREFS['segmentation_template']
        
        text_template_filled = None
        segmentation_lines = None
        
        if USER_PREFS['do_text']:
            text_is = USER_PREFS['text_insertion_symbol']
            text_template_filled = text_template.replace(
                text_is, outputs['text']
            )
        
        if USER_PREFS['do_segmentation']:
            text_is = USER_PREFS['segment_insertion_symbol']
            start_is = USER_PREFS['start_time_insertion_symbol']
            end_is = USER_PREFS['end_time_insertion_symbol']
            
            segmentation_lines = []
            for segment in outputs['segments']:
                text = segment['text']
                start = str(segment['start'])
                end = str(segment['end'])
                seg_template_filled = segmentation_template.replace(
                    text_is, text
                ).replace(
                    start_is, start
                ).replace(
                    end_is, end
                )
                segmentation_lines.append(seg_template_filled)
                
        return {
            'text': text_template_filled,
            'segmentation_lines': segmentation_lines
        }

    def make_paths(self, output_dir, fname):
        
        txt_loc = os.path.join(output_dir, fname + '.txt')
        seg_loc = os.path.join(output_dir, fname + '.seg')
        json_loc = os.path.join(output_dir, fname + '.json')
        
        # if any of the files already exist, make new ones with incremented numbers
        while any((os.path.exists(txt_loc), os.path.exists(seg_loc), os.path.exists(json_loc))):
            
            # if already numbered, just increment
            endswith_suffix = re.search(r'_\d+$', fname)
            if endswith_suffix:
                fname = fname[:endswith_suffix.start()] +'_' + str(int(endswith_suffix.group()[1:])+1)
            
            # if not numbered, add _1
            else:
                fname += '_1'
                
            txt_loc = os.path.join(output_dir, fname + '.txt')
            seg_loc = os.path.join(output_dir, fname + '.seg')
            json_loc = os.path.join(output_dir, fname + '.json')
        
        # if none of the files exist, fname is fine
        else:
            return txt_loc, seg_loc, json_loc

    def write_outputs(self, outputs: dict, formatted_outputs: dict, fname: str):
        text = formatted_outputs['text']
        segmentation_lines = formatted_outputs['segmentation_lines']
        
        output_dir = USER_PREFS['output_dir']
        os.makedirs(output_dir, exist_ok=True)
        
        txt_loc, seg_loc, json_loc = self.make_paths(output_dir, fname)
        
        if USER_PREFS['do_text']:
            with open(txt_loc, 'w+', encoding='utf-8') as f:
                f.write(text.strip())
            print(f'\t\tWrote transcription to "{os.path.abspath(txt_loc)}".')
        if USER_PREFS['do_segmentation']:
            with open(seg_loc, 'w+', encoding='utf-8') as g:
                for line in segmentation_lines:
                    g.write(line.strip() + '\n')
            print(f'\t\tWrote segmentation to "{os.path.abspath(seg_loc)}".')
        if USER_PREFS['do_json']:
            with open(json_loc, 'w+', encoding='utf-8') as h:
                json.dump(outputs, h, indent=4)
            print(f'\t\tWrote JSON data to "{os.path.abspath(json_loc)}".')

    def transcribe(self, paths: list, switch_model: bool):
        
        if not paths:
            print('No matching files found.\n')
            return
        
        print(f'Beginning transcription of {len(paths)} audio file(s).')

        self.get_model(switch_model=switch_model)
        
        for i, path in enumerate(paths):
            
            print(f'\tTranscribing "{path}" (file {i+1}/{len(paths)})...')
            
            path = os.path.normpath(path)
            assert os.path.exists(path)
            
            basename = os.path.basename(path)
            fname, ext = os.path.splitext(basename)
            
            if ext[1:] not in SUPPORTED_FILETYPES:
                msg = f'\tWarning: file "{path}" may not be supported. '
                msg += '\tSupported filetypes are: ' + ', '.join(SUPPORTED_FILETYPES)
                print(msg)
            
            if USER_PREFS['DEBUG']:
                outputs = json.load(
                    open(os.path.join('test_outputs', 'example_output.json'), 'r', encoding='utf-8')
                )
            else:
                with torch.no_grad():
                    outputs = self.model.transcribe(
                        whisper.load_audio(path),
                        language = self.map_available_language_to_valid_language(USER_PREFS['language']),
                        task = 'translate' if USER_PREFS['do_translate'] else 'transcribe',
                        verbose=False
                    )
            formatted_outputs = self.format_outputs(outputs)
            self.write_outputs(outputs, formatted_outputs, fname)
            print('\tDone.')
        
        print(f'Transcribed {len(paths)} files.\n')

        return self