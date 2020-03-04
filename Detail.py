class Detail(object):

    def __init__(self, compressed, hist, width, height, mode, scanning, palette=None):
        self.compressed = compressed
        self.hist = hist
        self.height = height
        self.width = width
        self.mode = mode
        self.scanning = scanning
        self.palette = palette
