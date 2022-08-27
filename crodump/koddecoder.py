"""
Decode CroStru KOD encoding.
"""
INITIAL_KOD = [
    0x08, 0x63, 0x81, 0x38, 0xA3, 0x6B, 0x82, 0xA6, 0x18, 0x0D, 0xAC, 0xD5, 0xFE, 0xBE, 0x15, 0xF6,
    0xA5, 0x36, 0x76, 0xE2, 0x2D, 0x41, 0xB5, 0x12, 0x4B, 0xD8, 0x3C, 0x56, 0x34, 0x46, 0x4F, 0xA4,
    0xD0, 0x01, 0x8B, 0x60, 0x0F, 0x70, 0x57, 0x3E, 0x06, 0x67, 0x02, 0x7A, 0xF8, 0x8C, 0x80, 0xE8,
    0xC3, 0xFD, 0x0A, 0x3A, 0xA7, 0x73, 0xB0, 0x4D, 0x99, 0xA2, 0xF1, 0xFB, 0x5A, 0xC7, 0xC2, 0x17,
    0x96, 0x71, 0xBA, 0x2A, 0xA9, 0x9A, 0xF3, 0x87, 0xEA, 0x8E, 0x09, 0x9E, 0xB9, 0x47, 0xD4, 0x97,
    0xE4, 0xB3, 0xBC, 0x58, 0x53, 0x5F, 0x2E, 0x21, 0xD1, 0x1A, 0xEE, 0x2C, 0x64, 0x95, 0xF2, 0xB8,
    0xC6, 0x33, 0x8D, 0x2B, 0x1F, 0xF7, 0x25, 0xAD, 0xFF, 0x7F, 0x39, 0xA8, 0xBF, 0x6A, 0x91, 0x79,
    0xED, 0x20, 0x7B, 0xA1, 0xBB, 0x45, 0x69, 0xCD, 0xDC, 0xE7, 0x31, 0xAA, 0xF0, 0x65, 0xD7, 0xA0,
    0x32, 0x93, 0xB1, 0x24, 0xD6, 0x5B, 0x9F, 0x27, 0x42, 0x85, 0x07, 0x44, 0x3F, 0xB4, 0x11, 0x68,
    0x5E, 0x49, 0x29, 0x13, 0x94, 0xE6, 0x1B, 0xE1, 0x7D, 0xC8, 0x2F, 0xFA, 0x78, 0x1D, 0xE3, 0xDE,
    0x50, 0x4E, 0x89, 0xB6, 0x30, 0x48, 0x0C, 0x10, 0x05, 0x43, 0xCE, 0xD3, 0x61, 0x51, 0x83, 0xDA,
    0x77, 0x6F, 0x92, 0x9D, 0x74, 0x7C, 0x04, 0x88, 0x86, 0x55, 0xCA, 0xF4, 0xC1, 0x62, 0x0E, 0x28,
    0xB7, 0x0B, 0xC0, 0xF5, 0xCF, 0x35, 0xC5, 0x4C, 0x16, 0xE0, 0x98, 0x00, 0x9B, 0xD9, 0xAE, 0x03,
    0xAF, 0xEC, 0xC9, 0xDB, 0x6D, 0x3B, 0x26, 0x75, 0x3D, 0xBD, 0xB2, 0x4A, 0x5D, 0x6C, 0x72, 0x40,
    0x7E, 0xAB, 0x59, 0x52, 0x54, 0x9C, 0xD2, 0xE9, 0xEF, 0xDD, 0x37, 0x1E, 0x8F, 0xCB, 0x8A, 0x90,
    0xFC, 0x84, 0xE5, 0xF9, 0x14, 0x19, 0xDF, 0x6E, 0x23, 0xC4, 0x66, 0xEB, 0xCC, 0x22, 0x1C, 0x5C,
]


class KODcoding:
    """
    class handing KOD encoding and decoding, optionally
    with a user specified KOD table.
    """
    def __init__(self, initial=INITIAL_KOD, confidence=[255] * 256):
        self.kod = [_ for _ in initial]
        self.confidence = confidence

        # calculate the inverse table.
        self.inv = [0 for _ in initial]
        for i, x in enumerate(self.kod):
            if confidence[i]:
                self.inv[x] = i

    def decode(self, o, data):
        """
        decode : shift, a[0]..a[n-1] -> b[0]..b[n-1]
            b[i] = KOD[a[i]]- (i+shift)
        """
        return bytes((self.kod[b] - i - o) % 256 for i, b in enumerate(data))

    def try_decode(self, o, data):
        """
        decode : shift, a[0]..a[n-1] -> b[0]..b[n-1]
            b[i] = KOD[a[i]]- (i+shift)
        """
        return (
            [(self.kod[b] - i - o) % 256 if self.confidence[b] > 0 else 0 for i, b in enumerate(data)],
            [self.confidence[b] for b in data]
        )

    def encode(self, o, data):
        """
        encode : shift, b[0]..b[n-1] -> a[0]..a[n-1]
            a[i] = INV[b[i]+ (i+shift)]
        """
        return bytes(self.inv[(b + i + o) % 256] for i, b in enumerate(data))


def new(*args):
    """
    create a KODcoding object with the specified arguments.
    """
    return KODcoding(*args)

def match_with_mismatches(data, confidence, string, maxsubs=None):
    """
    find all occurences of string in data with at least one and allowing a
    maximum of maxsubs substitutions
    """

    # default for maximum of substitutions is to have at least two matching chars
    maxsubs = maxsubs if maxsubs is not None else max( 2, len(string) - 2)

    # if string cant fit into data, return no matches
    if len(string) > len(data):
        return []

    matches = []
    for offs in range(0, len(data) - len(string)):
        matching = 0
        for o, c in enumerate(string):
            if data[offs + o] == c and confidence[offs + o] > 0:
                matching += 1

        if matching != len(string) and matching >= maxsubs:
            matches.append((offs, matching))

    return sorted(matches, key=lambda x: x[1])
