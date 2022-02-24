#!/usr/bin/env python3

# Licensed under Creative Commons Attribution-NonCommercial-ShareAlike 4.0
# International, (the "License");
# you may not use this file except in compliance with the License.

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License

import argparse
import os
import re
import sys

# We include the path of the toplevel package in the system path so we can always use absolute imports within the package.
toplevel_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if toplevel_path not in sys.path:
    sys.path.insert(1, toplevel_path)

import evalsub.util.constants as cst
import evalsub.util.util as utl


def hms_to_hmsf(hms):
    """
    Converts a timecode from hms to hmsf format.

    :param hms: timecode at format hh:mm:ss,sss
    :return: timecode at format hh:mm:ss:ff
    """
    h, m, s = hms.split(':')
    s, ms = s.split(',')
    
    f = int(ms)/40  # frame (from 0 to 24)
    
    return '%s:%s:%s:%02d' % (h, m, s, f)

def hmsf_to_hms(hmsf):
    """
    Converts a timecode from hmsf to hms format.

    :param hmsf: timecode at format hh:mm:ss:ff
    :return: timecode at format hh:mm:ss,sss
    """
    h, m, s, f = hmsf.split(':')
    
    ms = int(f)*40
    
    return '%s:%s:%s,%03d' % (h, m, s, ms)

## READER  #####################################################################

class SrtCaption:
    def __init__(self, file_lines):
        self.index = int(file_lines[0])
        begin, end = file_lines[1].split(' --> ')
        self.begin = hms_to_hmsf(begin)
        self.end = hms_to_hmsf(end)
        self.lines = file_lines[2:]

class SrtReader:
    def __init__(self, file_path):
        self.file_path = file_path
        self.file = open(file_path, 'r', encoding='utf-8-sig')
        self.caption = None
    
    def reinit(self):
        self.file.close()
        self.file = open(self.file_path, 'r', encoding='utf-8-sig')
        self.caption = None
    
    def close(self):
        self.file.close()
    
    def read_caption(self):
        file_lines = list()
        file_line = self.file.readline().rstrip()
        
        while file_line:
            if file_line[0] != '#':
                file_lines.append(file_line)
            
            file_line = self.file.readline().rstrip()
        
        if len(file_lines) < 3:
            return False
        else:
            self.caption = SrtCaption(file_lines)
            return True

    def read_all(self):
        captions = list()
        while self.read_caption():
            caption = self.current_lines()
            captions.append(caption)

        return captions
    
    def current_index(self):
        return self.caption.index
    
    def current_time_span(self):
        return self.caption.begin, self.caption.end
    
    def current_lines(self):
        return  self.caption.lines

## WRITER  #####################################################################

class SrtWriter:
    def __init__(self, file_path):
        self.file_path = file_path
        self.file = open(file_path, 'w')
        self.index = 0
    
    def reinit(self):
        self.file.close()
        self.file = open(self.file_path, 'w')
        self.index = 0
    
    def close(self):
        self.file.close()
    
    def write_caption(self, lines, begin, end):
        self.index += 1
        begin = hmsf_to_hms(begin)
        end = hmsf_to_hms(end)
        caption_string = '%d\n%s --> %s\n%s\n\n' % (self.index, begin, end, '\n'.join(lines))
        self.file.write(caption_string)


def srt_to_tagged_str(srt_file_path, line_tag=cst.LINE_TAG, caption_tag=cst.CAPTION_TAG):
    srt_reader = SrtReader(srt_file_path)

    captions = list()
    time_spans = list()
    while srt_reader.read_caption():
        caption = srt_reader.current_lines()
        captions.append(caption)
        time_span = '%s %s' % srt_reader.current_time_span()
        time_spans.append(time_span)

    tagged_str = caption_tag.join([line_tag.join(caption) for caption in captions]) + caption_tag
    tagged_str = re.sub(r"(%s|%s)" % (line_tag, caption_tag), r" \1 ", tagged_str).strip()

    srt_reader.close()

    return tagged_str, time_spans


def find_eos(tagged_str, line_tag=cst.LINE_TAG, caption_tag=cst.CAPTION_TAG):
    return [m.end() for m in re.finditer(r'((?<!["( -][A-Z])\.|[!?])([")])?( )?(%s|%s)' % (line_tag, caption_tag), tagged_str)]


def srt_to_tagged_sents(srt_file_path, line_tag=cst.LINE_TAG, caption_tag=cst.CAPTION_TAG):
    tagged_str, time_spans = srt_to_tagged_str(srt_file_path, line_tag=line_tag, caption_tag=caption_tag)
    eos_positions = find_eos(tagged_str, line_tag=line_tag, caption_tag=caption_tag)

    tagged_sents = list()
    start_pos = 0
    for end_pos in eos_positions:
        tagged_sent = tagged_str[start_pos:end_pos]
        tagged_sent = tagged_sent.strip()
        tagged_sents.append(tagged_sent)
        start_pos = end_pos

    return tagged_sents, time_spans


## MAIN FUNCTIONS  #############################################################

def srt_to_tagged_txt(srt_file_path, tagged_txt_file_path, timecode_file_path, line_tag=cst.LINE_TAG,
                      caption_tag=cst.CAPTION_TAG):
    print('Converting srt into tagged text:')
    print('Reading and segmenting file...')
    tagged_sents, time_spans = srt_to_tagged_sents(srt_file_path, line_tag=line_tag, caption_tag=caption_tag)

    print('Writing...')
    utl.write_lines(tagged_sents, tagged_txt_file_path)
    if timecode_file_path is not None:
        utl.write_lines(time_spans, timecode_file_path)


def tagged_txt_to_srt(srt_file_path, tagged_txt_file_path, timecode_file_path):
    print("to do") # TODO?

## MAIN  #######################################################################

def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument('mode', type=str, choices=['srt2tagged', 'tagged2srt'])

    parser.add_argument('--srt_file', '-srtf', type=str)
    parser.add_argument('--tagged_txt_file', '-tagf', type=str)
    parser.add_argument('--timecode_file', '-tcf', type=str)

    args = parser.parse_args()
    return args


def main(args):
    mode = args.mode

    srt_file_path = args.srt_file
    tagged_txt_file_path = args.tagged_txt_file
    timecode_file_path = args.timecode_file

    if mode == 'srt2tagged':
        srt_to_tagged_txt(srt_file_path, tagged_txt_file_path, timecode_file_path)

    elif mode == 'tagged2srt':
        tagged_txt_to_srt(srt_file_path, tagged_txt_file_path, timecode_file_path)


if __name__ == '__main__':
    main(parse_args())