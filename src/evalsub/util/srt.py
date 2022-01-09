# coding: utf-8

import argparse
import re

from .util import write_lines


LINE_TAG = '<eol>'
CAPTION_TAG = '<eob>'


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


def srt_to_tagged_str(srt_file_path, line_tag=LINE_TAG, caption_tag=CAPTION_TAG):
    srt_reader = SrtReader(srt_file_path)

    captions = list()
    time_spans = list()
    while srt_reader.read_caption():
        caption = srt_reader.current_lines()
        captions.append(caption)
        time_span = '%s %s' % srt_reader.current_time_span()
        time_spans.append(time_span)

    all_sub = caption_tag.join([line_tag.join(caption) for caption in captions]) + caption_tag
    all_sub = re.sub(r"(%s|%s)" % (line_tag, caption_tag), r" \1 ", all_sub).strip()

    srt_reader.close()

    return all_sub, time_spans

## MAIN FUNCTIONS  #############################################################

def srt_to_tagged_txt(srt_file_path, tagged_txt_file_path, timecode_file_path, line_tag=LINE_TAG,
                      caption_tag=CAPTION_TAG):
    print('Converting srt into tagged text:')
    print('Reading file...')
    all_sub, time_spans = srt_to_tagged_str(srt_file_path, line_tag=line_tag, caption_tag=caption_tag)

    print('Segmenting into sentences...')
    sub_eos_positions = [m.end() for m in re.finditer(r'((?<!["( -][A-Z])\.|[!?])([")])?( )?%s' % caption_tag, all_sub)]

    sub_segments = list()
    start_pos = 0
    for end_pos in sub_eos_positions:
        sub_segment = all_sub[start_pos:end_pos]
        sub_segment = sub_segment.strip()
        sub_segments.append(sub_segment)
        start_pos = end_pos

    print('Writing...')
    write_lines(sub_segments, tagged_txt_file_path)
    if timecode_file_path is not None:
        write_lines(time_spans, timecode_file_path)


def tagged_txt_to_srt(srt_file_path, tagged_txt_file_path, timecode_file_path):
    print("to do")

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