# coding: utf-8

import argparse
from collections import OrderedDict
import hashlib
import math
import os
import re
import xml.etree.ElementTree as ET

import textstat

COLOR_FILTER = frozenset(['magenta', 'red'])
MAX_CPL = 36
MAX_CPS = 15
MASK_CHAR = '#'
LINE_TAG = '<br>'
CAPTION_TAG = '<p>'
TTML_TEMPLATE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'template.ttml')

ET.register_namespace('', 'http://www.w3.org/ns/ttml')
ET.register_namespace('ttm', 'http://www.w3.org/ns/ttml#metadata')
ET.register_namespace('ttp', 'http://www.w3.org/ns/ttml#parameter')
ET.register_namespace('tts', 'http://www.w3.org/ns/ttml#styling')

def indent(elem, level=0):
    """
    copy and paste from http://effbot.org/zone/element-lib.htm#prettyprint
    it basically walks your tree and adds spaces and newlines so the tree is
    printed in a nice way
    """
    i = "\n" + level*"  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            indent(elem, level+1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i


def f_to_hmsf(f):
    """
    Converts a number of frames into a timecode.

    :param f: number of frames
    :return: timecode at format hh:mm:ss:ff
    """
    s = math.floor(f/25)
    f -= s*25
    m = math.floor(s/60)
    s -= m*60
    h = math.floor(m/60)
    m -= h*60
    
    return '%02d:%02d:%02d:%02d' % (h, m, s, f)


def hmsf_to_f(hmsf):
    """
    Converts a timecode into a number of frames.

    :param hmsf: timecode at format hh:mm:ss:ff
    :return: number of frames
    """
    h, m, s, f = [int(x) for x in hmsf.split(':')]
    f += 90000*h + 1500*m + 25*s
    
    return f


def hmsf_to_s(hmsf):
    """
    Converts a timecode into a number of seconds.

    :param hmsf: timecode at format hh:mm:ss:ff
    :return: number of seconds
    """
    h, m, s, f = [int(x) for x in hmsf.split(':')]
    s += 3600*h + 60*m + 0.04*f
    
    return s


def write_lines(lines, file_path, add=False):
    mode = 'a' if add else 'w'
    file = open(file_path, mode)
    
    for line in lines:
        file.write(line + '\n')
    
    file.close()


def find_eos_positions(s):
    return [m.end() for m in re.finditer(r'((?<!["( -][A-Z])\.|[!?])([")])?(?= |$)', s)]

## READER  #####################################################################

class TtmlReader:
    def __init__(self, file_path, filtering=False, masking=False):
        self.caption_index = -1
        self.line_index = -1
        self.caption_next_index = 0
        self.line_next_index = 0
        
        self.tree = ET.parse(file_path)
        self.root = self.tree.getroot()
        
        # For line color filtering
        self.filtering = filtering
        self.masking = masking
        self.color_filter = COLOR_FILTER
        # For statistics
        self.color_count = OrderedDict([('Cyan', 0), ('green', 0), ('magenta', 0), ('red', 0), ('yellow', 0), ('white', 0)])
        self.n_over_cpl_lines = 0
        self.n_over_cps_captions = 0
        self.cps_sum = 0
        self.n_cps = 0  # nb of captions for which cps has been computed
    
    def reinit(self):
        self.caption_index = -1
        self.line_index = -1
        self.caption_next_index = 0
        self.line_next_index = 0
        
        # For statistics
        self.color_count = OrderedDict([('Cyan', 0), ('green', 0), ('magenta', 0), ('red', 0), ('yellow', 0), ('white', 0)])
        self.n_over_cpl_lines = 0
        self.n_over_cps_captions = 0
        self.cps_sum = 0
        self.n_cps = 0
    
    def read_line(self):
        #print("\t\tRead line", self.caption_next_index, self.line_next_index)#DEBUG#
        if self.is_file_over():
            return ''
        
        self.caption_index = self.caption_next_index
        self.line_index = self.line_next_index
        
        self.line_next_index += 1
        # There might be empty captions...
        while (self.caption_next_index < len(self.root[1][0])) and (self.line_next_index == len(self.root[1][0][self.caption_next_index])):
            self.caption_next_index += 1
            self.line_next_index = 0
        
        line = self.root[1][0][self.caption_index][self.line_index]
        # If the line is actually a break mark <br/>
        if line.text is None:
            return self.read_line()
        # If it is an actual line
        else:
            # If the line length exceeds the limit
            if len(line.text) > MAX_CPL:
                self.n_over_cpl_lines += 1
            
            color = self.current_color()
            # There should not be colors other than those already in the counter...
            try:
                self.color_count[color] += 1
            # ... however...
            except KeyError:
                self.color_count[color] = 1
            # If filtering is active, and that the line color is among those filtered
            if self.filtering and color in self.color_filter:
                # next line is directly read
                return self.read_line()
            # Else, if masking is active, and that the line color is among those filtered
            elif self.masking and color in self.color_filter:
                # masked line text is returned
                #print("\t\t\t", line.text)#DEBUG#
                return len(line.text)*MASK_CHAR
            # Else
            else:
                # line text is returned
                #print("\t\t\t", line.text)#DEBUG#
                return line.text
    
    def read_caption(self, flat=True):
        #print("\tRead caption", self.caption_next_index)#DEBUG#
        if self.is_file_over():
            return '' if flat else []
        
        lines = list()
        caption_current_index = self.caption_next_index
        
        while self.caption_next_index == caption_current_index:
            line = self.read_line()
            lines.append(line)
        
        start, end = self.current_time_span()
        duration = hmsf_to_s(end) - hmsf_to_s(start)
        if duration > 0:
            n_chars = sum(map(len, lines))
            cps = n_chars/duration
            self.cps_sum += cps
            self.n_cps += 1
            if cps > MAX_CPS:
                self.n_over_cps_captions += 1
        
        if not flat:
            return lines
        
        caption = ' '.join(lines)
        if self.masking:
            caption = re.sub(r"%s %s" % (MASK_CHAR, MASK_CHAR), 3*MASK_CHAR, caption)
        
        return caption
    
    def read_all(self, flat=True):
        #print("Read all", len(self.root[1][0]) - self.caption_next_index)#DEBUG#
        captions = list()
        
        while not self.is_file_over():
            caption = self.read_caption(flat=flat)
            captions.append(caption)
        
        if not flat:
            return captions
        
        all_sub = ' '.join(captions)
        if self.masking:
            all_sub = re.sub(r"%s %s" % (MASK_CHAR, MASK_CHAR), 3*MASK_CHAR, all_sub)
        
        return all_sub
    
    def set_masking(self, masking):
        self.masking = masking
    
    def n_captions(self):
        return len(self.root[1][0])
    
    # Call after read_all()
    def n_lines(self, filtered=True):
        n_lines = sum(self.color_count.values())
        if filtered:
            n_lines -= sum([self.color_count[c] for c in self.color_filter])
        return n_lines
    
    # Call after read_all()
    def n_over_cpl(self):
        return self.n_over_cpl_lines
    
    # Call after read_all()
    def line_color_count(self):
        return self.color_count
    
    # Call after read_all()
    def n_over_cps(self):
        return self.n_over_cps_captions
    
    # Call after read_all()
    def caption_cps(self):
        return self.cps_sum/self.n_cps
    
    def time_span(self, ci):
        caption = self.root[1][0][ci]
        start = caption.attrib['begin']
        end = caption.attrib['end']
        return start, end
    
    # "current" = wrt the last read line
    def current_time_span(self):
        return self.time_span(self.caption_index)
    
    def next_time_span(self):
        return self.time_span(self.caption_next_index)
    
    def total_duration(self):
        last_caption = self.root[1][0][-1]
        end = last_caption.attrib['end']
        etime = hmsf_to_s(end)
        return etime
    
    # "current" = wrt the last read line
    def current_color(self):
        line = self.root[1][0][self.caption_index][self.line_index]
        color = line.attrib['{http://www.w3.org/ns/ttml#styling}color']  #TODO à revoir...
        return color
    
    def is_next_break(self):
        return self.caption_index == self.caption_next_index
    
    def is_file_over(self):
        return self.caption_next_index >= len(self.root[1][0])

## WRITER  #####################################################################

class TtmlWriter:
    def __init__(self, output_file_path, title='no title'):
        self.tree = ET.parse(TTML_TEMPLATE)
        self.root = self.tree.getroot()
        
        self.root[0][0][0].text = title
        self.output_file_path = output_file_path
    
    def write(self):
        indent(self.root)
        self.tree.write(self.output_file_path, encoding='unicode', xml_declaration=True)
    
    def add_caption(self, lines, begin, end, color):
        ttml_caption = ET.SubElement(self.root[1][0], 'p')
        ttml_caption.set('xml:id', 'caption%d' % len(self.root[1][0]))
        ttml_caption.set('ttm:role', 'caption')
        ttml_caption.set('begin', begin)
        ttml_caption.set('end', end)
        
        self.add_line(lines[0], color)
        for line in lines[1:]:
            self.add_break()
            self.add_line(line, color)
    
    def add_line(self, line, color):
        ttml_line = ET.SubElement(self.root[1][0][-1], 'span')
        ttml_line.text = line
        ttml_line.set('tts:textAlign', 'center')
        ttml_line.set('tts:color', color)
    
    def add_break(self):
        ET.SubElement(self.root[1][0][-1], 'br')

## FUNCTIONS  ##################################################################

def hash_sub(ttml_file_path):
    #print('Computing the hash fingerprint:')
    #print('Initializing...')
    ttml_reader = TtmlReader(ttml_file_path, filtering=False, masking=False)
    
    #print('Reading file...')
    all_sub = ttml_reader.read_all()
    
    #print('Applying md5 function...')
    hashKey = hashlib.md5(all_sub.encode()).hexdigest()
    
    return hashKey


def make_sub_stats(ttml_file_path):
    # Subtitles with masking
    ttml_reader = TtmlReader(ttml_file_path, filtering=False, masking=True)
    masked_all_sub = ttml_reader.read_all()

    # Subtitles with filtering
    filtered_all_sub = masked_all_sub
    filtered_all_sub = filtered_all_sub.lstrip(MASK_CHAR + ' ')
    filtered_all_sub = re.sub(r" %s+" % MASK_CHAR, r"", filtered_all_sub)

    n_filtered_sub_chars = len(filtered_all_sub)
    sub_fre_score = textstat.flesch_reading_ease(filtered_all_sub)

    # Full subtitles
    ttml_reader.reinit()
    ttml_reader.set_masking(False)
    all_sub = ttml_reader.read_all()

    n_sub_chars = len(all_sub)
    sub_eos_positions = find_eos_positions(all_sub)
    n_segments = len(sub_eos_positions)

    # On prépare la tokenisation du sous-titre :
    #   - en plaçant des espaces après les apostrophes (sauf dans le cas de "c'est" ou "s'est", 1 mot)
    #   - en supprimant les espaces avant ":","!" ou "?" (on ne compte pas la ponctuation)
    #   - en plaçant des espaces après les tirets (sauf ceux en début de phrase)
    all_sub = re.sub(r"([^cCsS])'", r"\1' ", all_sub)
    all_sub = re.sub(r" ([:!?])", r"\1", all_sub)
    all_sub = re.sub(r"([^ ])-", r"\1- ", all_sub)

    n_sub_words = len(all_sub.split(' '))

    sub_stats = dict()

    # Nb of characters in the subtitles (before filtering)
    sub_stats['n_chars'] = n_sub_chars
    # Nb of sentences in the subtitles
    sub_stats['n_sentences'] = n_segments
    # Nb of words in the subtitles (before filtering)
    sub_stats['n_words'] = n_sub_words
    # Duration of subtitles display
    subDuration = ttml_reader.total_duration()
    sub_stats['duration'] = subDuration
    # Nb of captions
    n_captions = ttml_reader.n_captions()
    sub_stats['n_captions'] = n_captions
    # Nb of lines (before filtering)
    n_lines = ttml_reader.n_lines(filtered=False)
    sub_stats['n_lines'] = n_lines
    # Nb of lines (after filtering)
    n_lines_filtered = ttml_reader.n_lines(filtered=True)
    sub_stats['n_lines_filtered'] = n_lines_filtered
    # Nb of lines exceeding the length limit
    n_over_cpl_lines = ttml_reader.n_over_cpl()
    sub_stats['n_over_cpl_lines'] = n_over_cpl_lines
    # Nb of lines for each color
    sub_stats.update(ttml_reader.line_color_count())

    # Nb of characters in the subtitles (after filtering)
    sub_stats['n_filtered_chars'] = n_filtered_sub_chars
    # Average cps in a caption
    caption_cps = ttml_reader.caption_cps()
    sub_stats['cps'] = caption_cps
    # Nb of captions exceeding the display rate limit
    n_over_cps_captions = ttml_reader.n_over_cps()
    sub_stats['n_over_cps_captions'] = n_over_cps_captions
    # FRE score for the subtitles (assumed to be french)
    sub_stats['fre'] = sub_fre_score

    return sub_stats

## MAIN FUNCTIONS  #############################################################

def read_sub(ttml_file_path, text_file_path, filtering=True, masking=False):
    print('Extracting subtitles:')
    print('Initializing...')
    ttml_reader = TtmlReader(ttml_file_path, filtering=filtering, masking=masking)
    
    print('Reading file...')
    all_sub = ttml_reader.read_all()
    
    print('Segmenting into sentences...')
    sub_eos_positions = [m.end() for m in re.finditer(r'((?<!["( -][A-Z])\.|[!?%s])([")])?(?= |$)' % MASK_CHAR, all_sub)]  # "'MASK_CHAR' " compte comme fin de phrase à cause du masquage
    sub_segments = list()
    
    start_pos = 0
    for end_pos in sub_eos_positions:
        sub_segment = all_sub[start_pos:end_pos]
        sub_segments.append(sub_segment)
        start_pos = end_pos + 1  # + 1 accounts for the space
    
    print('Writing...')
    write_lines(sub_segments, text_file_path)


def ttml_to_tagged_txt(ttml_file_path, tagged_txt_file_path, timecode_file_path, filtering=True, masking=False,
                       line_tag=LINE_TAG, caption_tag=CAPTION_TAG):
    print('Converting ttml into tagged text:')
    print('Initializing...')
    ttml_reader = TtmlReader(ttml_file_path, filtering=filtering, masking=masking)
    
    print('Reading file...')
    captions = list()
    time_spans = list()
    while not ttml_reader.is_file_over():
        caption = ttml_reader.read_caption(flat=False)
        captions.append(caption)
        time_span = '%s %s' % ttml_reader.current_time_span()
        time_spans.append(time_span)
    
    all_sub = caption_tag.join([line_tag.join(caption) for caption in captions]) + caption_tag
    
    print('Segmenting into sentences...')
    sub_eos_positions = [m.end() for m in re.finditer(r'((?<!["( -][A-Z])\.|[!?%s])([")])?%s' % (MASK_CHAR, caption_tag), all_sub)]  # "'MASK_CHAR''caption_tag'" compte comme fin de phrase à cause du masquage

    sub_segments = list()
    start_pos = 0
    for end_pos in sub_eos_positions:
        sub_segment = all_sub[start_pos:end_pos]
        sub_segments.append(sub_segment)
        start_pos = end_pos
    
    print('Writing...')
    write_lines(sub_segments, tagged_txt_file_path)
    write_lines(time_spans, timecode_file_path)


def tagged_txt_to_ttml(ttml_file_path, tagged_txt_file_path, timecode_file_path, line_tag=LINE_TAG, caption_tag=CAPTION_TAG):
    print('Converting tagged text into ttml:')
    print('Initializing...')
    ttml_writer = TtmlWriter(ttml_file_path)
    
    print('Reading files...')
    tagged_txt = open(tagged_txt_file_path, 'r').read()
    captions = [caption.strip().split(line_tag) for caption in tagged_txt.split(caption_tag)[:-1]]
    
    timecode_lines = open(timecode_file_path, 'r').readlines()
    time_spans = [timecode_line.split() for timecode_line in  timecode_lines]
    
    print('Writing...')
    assert(len(captions) == len(time_spans))
    for caption, time_span in zip(captions, time_spans):
        begin, end = time_span
        ttml_writer.add_caption(caption, begin, end, 'white')
    
    ttml_writer.write()

## MAIN  #######################################################################

def parse_args():
    parser = argparse.ArgumentParser()
    
    parser.add_argument('mode', type=str, choices=['read', 'ttml2tagged', 'tagged2ttml', 'hash'])
    
    parser.add_argument('--ttml_file', '-ttmlf', type=str)
    parser.add_argument('--text_file', '-txtf', type=str)
    parser.add_argument('--tagged_txt_file', '-tagf', type=str)
    parser.add_argument('--timecode_file', '-tcf', type=str)
    
    parser.add_argument('--filtering', '-f', action='store_true')
    parser.add_argument('--masking', '-m', action='store_true')
    
    args = parser.parse_args()
    return args


def main(args):
    mode = args.mode
    
    ttml_file_path = args.ttml_file
    text_file_path = args.text_file
    tagged_txt_file_path = args.tagged_txt_marked_file
    timecode_file_path = args.timecode_file
    
    filtering = args.filtering
    masking = args.masking
    
    if mode == 'read':
        read_sub(ttml_file_path, text_file_path, filtering=filtering, masking=masking)
    
    elif mode == 'ttml2tagged':
        ttml_to_tagged_txt(ttml_file_path, tagged_txt_file_path, timecode_file_path, filtering=filtering, masking=masking)
    
    elif mode == 'tagged2ttml':
        tagged_txt_to_ttml(ttml_file_path, tagged_txt_file_path, timecode_file_path)
    
    elif mode == 'hash':
        print(hash_sub(ttml_file_path))


if __name__ == '__main__':
    main(parse_args())