# coding: utf-8

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
        self.file = open(file_path, 'w')
        self.index = 0
    
    def close(self):
        self.file.close()
    
    def write_caption(self, lines, begin, end):
        self.index += 1
        begin = hmsf_to_hms(begin)
        end = hmsf_to_hms(end)
        caption_string = '%d\n%s --> %s\n%s\n\n' % (self.index, begin, end, '\n'.join(lines))
        self.file.write(caption_string)
