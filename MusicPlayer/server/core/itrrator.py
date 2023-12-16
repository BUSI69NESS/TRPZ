class PlaylistIterator:
    def __init__(self, tracks):
        self.tracks = tracks
        self.index = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.index < len(self.tracks):
            current_track = self.tracks[self.index]
            self.index += 1
            return current_track
        else:
            raise StopIteration