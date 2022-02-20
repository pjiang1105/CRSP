class Record:
    """Holds information from a FASTA record.

    Members:
    title       Title line ('>' character not included).
    sequence    The sequence.
    
    """
    def __init__(self, title="", sequence=""):
        self.title = title
        self.sequence = sequence

    def __repr__(self):
        return 'Record("%s","%s")' % (self.title, self.sequence)

class Reader:
    r'''
    >>> import StringIO
    >>> test_string = ">rec1\nCATCGATCGTACG\n>rec2\nCACTAGCTAGTG"
    >>> test_file = StringIO.StringIO(test_string)
    >>> list(iter(Reader(test_file)))
    [Record("rec1","CATCGATCGTACG"), Record("rec2","CACTAGCTAGTG")]
    '''

    def __init__(self, stream, bufsize=(100 * pow(2, 20))):
        self.stream = stream
        self.bufsize = bufsize
        self.pos = -1
        while self.pos == -1:
            self.buffer = self.stream.read(self.bufsize)
            if not self.buffer: break
            self.pos = self.buffer.find('>')

    def read(self):
        try:
            return next(self)
        except StopIteration:
            return None

    def read_recs(self):
        return [rec for rec in self]

    def _parse_rec(self, text):
        titlesplit = text.find('\n')
        return Record(text[:titlesplit].rstrip(),
                      text[titlesplit:].replace('\n', '').replace(' ', ''))
    
    def __iter__(self):
        return self

    def __next__(self):
        if self.pos == -1:
            raise StopIteration
        
        text = ""
        startpos = self.pos + 1

        while 1:
            self.pos = self.buffer.find('>', startpos)

            if self.pos != -1:
                text += self.buffer[startpos: self.pos]
                break

            text += self.buffer[startpos:]
            self.buffer = self.stream.read(self.bufsize)

            if not self.buffer:
                break

            startpos = 0

        return self._parse_rec(text)

class Writer:
    def __init__(self, stream, colwidth=60):
        self.stream = stream
        self.colwidth = colwidth

    def write(self, rec):
        print(">%s" % rec.title, file=self.stream)
        for i in range(0, len(rec.sequence), self.colwidth):
            print(rec.sequence[i: i + self.colwidth], file=self.stream)
    
    def write_recs(self, recs):
        for rec in recs:
            self.write(rec)

def _test():
    import doctest
    doctest.testmod()

if __name__ == "__main__":
    _test()