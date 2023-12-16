from abc import ABC, abstractmethod


class Command(ABC):
    @abstractmethod
    def execute(self, *args):
        pass
    def accept(self, *args): pass

class SaveMementoCommand(Command):
    def execute(self, music_player, client_socket, *args):
        memento = music_player.create_playlist_memento()
        music_player.memento_stack.append(memento)
        client_socket.sendall(f'Memento saved for playlist: {music_player.current_playlist_id}'.encode('utf-8'))

    def accept(self, visitor):
        visitor.visit_save_memento(self)
class RestoreMementoCommand(Command):
    def execute(self, music_player, client_socket, *args):
        if music_player.memento_stack:
            memento = music_player.memento_stack.pop()
            music_player.restore_playlist_from_memento(memento)
            client_socket.sendall(f'Playlist restored from memento: {music_player.current_playlist_id}'.encode('utf-8'))
        else:
            client_socket.sendall('No mementos available for restoration.'.encode('utf-8'))

    def accept(self, visitor):
        visitor.visit_restore_memento(self)
class PlayCommand(Command):
    def execute(self, music_player, client_socket, *args):
        music_player.play(client_socket)

class PauseCommand(Command):
    def execute(self, music_player, client_socket, *args):
        music_player.pause(client_socket)

class AddPlaylistCommand(Command):
    def execute(self, music_player, client_socket, *args):
        if args:
            playlist_name = ' '.join(args)
            music_player.add_playlist(playlist_name, client_socket)

class AddTrackToPlaylistCommand(Command):
    def execute(self, music_player, client_socket, *args):
        if len(args) == 3:
            playlist_name, track_title, track_path = args

            music_player.add_track_to_playlist(playlist_name, track_title, track_path, client_socket)

class RemoveTrackFromPlaylistCommand(Command):
    def execute(self, music_player, client_socket, *args):
        if len(args) == 2:
            playlist_name, track_title = args
            music_player.remove_track_from_playlist(playlist_name, track_title, client_socket)

class ShufflePlaylistCommand(Command):
    def execute(self, music_player, client_socket, *args):
        if args:
            playlist_name = args[0]
            music_player.shuffle_playlist(playlist_name, client_socket)

class ShowPlaylistsCommand(Command):
    def execute(self, music_player, client_socket, *args):
        music_player.show_playlists(client_socket)

class ShowTracksForPlaylistCommand(Command):
    def execute(self, music_player, client_socket, *args):
        if args:
            playlist_name = args[0]
            music_player.show_tracks_for_playlist(playlist_name, client_socket)

class StopCommand(Command):
    def execute(self, music_player, client_socket, *args):
        music_player.stop(client_socket)

class ShowTracksWithOrderCommand(Command):
    def execute(self, music_player, client_socket, *args):
        if args:
            playlist_name = args[0]
            music_player.show_tracks_with_order(playlist_name, client_socket)

class SelectPlaylistCommand(Command):
    def execute(self, music_player, client_socket, *args):
        if args:
            playlist_id = int(args[0])
            music_player.select_playlist(playlist_id, client_socket)

class PlayTrackCommand(Command):
    def execute(self, music_player, client_socket, *args):
        if len(args) == 2:
            playlist_name, track_title = args
            music_player.play_track(playlist_name, track_title, client_socket)

class PlayPlaylistLoopCommand(Command):
    def execute(self, music_player, client_socket, *args):
        music_player.play_playlist_loop(client_socket)

class PlayTrackLoopCommand(Command):
    def execute(self, music_player, client_socket, *args):
        if len(args) == 2:
            playlist_name, track_title = args
            music_player.play_track_loop(playlist_name, track_title, client_socket)

class RemovePlaylistCommand(Command):
    def execute(self, music_player, client_socket, *args):
        if args:
            playlist_name = args[0]
            music_player.remove_playlist(playlist_name, client_socket)

class UnpauseCommand(Command):
    def execute(self, music_player, client_socket, *args):
        music_player.unpause(client_socket)

class SetEqualizerCommand(Command):
    def execute(self, music_player, client_socket, *args):
        if args:
            level = float(args[0])
            music_player.set_equalizer(level, client_socket)

class PlaylistMemento:
    def __init__(self, playlist_id, tracks):
        self.playlist_id = playlist_id
        self.tracks = tracks