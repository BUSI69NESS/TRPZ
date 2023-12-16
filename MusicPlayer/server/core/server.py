import socket
import threading
from MusicPlayer.server.core.loggingvisitor import LoggingVisitor
from MusicPlayer.server.core.player import MusicPlayer
from MusicPlayer.server.core.commands import PlayCommand, PauseCommand, AddPlaylistCommand, AddTrackToPlaylistCommand, \
    RemoveTrackFromPlaylistCommand, ShufflePlaylistCommand, ShowPlaylistsCommand, ShowTracksForPlaylistCommand, \
    StopCommand, ShowTracksWithOrderCommand, SelectPlaylistCommand, PlayTrackCommand, PlayPlaylistLoopCommand, \
    PlayTrackLoopCommand, RemovePlaylistCommand, UnpauseCommand, SetEqualizerCommand, SaveMementoCommand, \
    RestoreMementoCommand



class MusicServer:
    def __init__(self, host='127.0.0.1', port=12345):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        self.memento_stack = []
        self.music_player = MusicPlayer()



    def handle_client(self, client_socket):
        while True:
            try:
                data = client_socket.recv(1024).decode('utf-8')
                if not data:
                    break
                self.handle_command(data, client_socket)

            except Exception as e:
                print(f"Error handling client: {e}")
                break

        client_socket.close()

    def send_help(self, client_socket):
        help_message = """
        Available commands:
        - play: Play the current playlist.
        - pause: Pause the playback.
        - add_playlist [name]: Create a new playlist.
        - add_track_to_playlist [playlist_name] [track_title] [track_path]: Add a track to a playlist.
        - remove_track_from_playlist [playlist_name] [track_title]: Remove a track from a playlist.
        - shuffle_playlist [playlist_name]: Shuffle the tracks in a playlist.
        - show_playlists: Show all playlists.
        - show_tracks_for_playlist [playlist_name]: Show tracks for a specific playlist.
        - stop: Stop the music playback.
        - show_tracks_with_order [playlist_name]: Show tracks for a playlist with their current order.
        - select_playlist [playlist_id]: Select a playlist by ID.
        - play_track [playlist_name] [track_title]: Play a specific track from a playlist.
        - play_track_loop [playlist_name] [track_title]: Loop a specific track from a playlist.
        - remove_playlist [playlist_name]: Remove a playlist.
        - unpause: Resume the playback.
        - set_equalizer [level]: Set the equalizer level.
        - save_memento: save memento
        - restore_memento: restore memento
        """
        client_socket.sendall(help_message.encode('utf-8'))

    def handle_command(self, command, client_socket):
        command_parts = command.split(' ')
        command_name = command_parts[0].lower()

        if command_name == 'help':
            self.send_help(client_socket)
        elif command_name in self.commands:
            args = command_parts[1:]
            command_instance = self.commands[command_name]
            command_instance.execute(self.music_player, client_socket, *args)
            logging_visitor = LoggingVisitor()
            command_instance.accept(logging_visitor)
        else:
            client_socket.sendall(f'unsupported command {command}'.encode('utf-8'))



    def start(self):
        print(f"Server listening on {self.host}:{self.port}")
        while True:
            client_socket, addr = self.server_socket.accept()
            client_handler = threading.Thread(target=self.handle_client, args=(client_socket,))
            client_handler.start()

    def register_commands(self):
        self.commands = {
            'play': PlayCommand(),
            'pause': PauseCommand(),
            'add_playlist': AddPlaylistCommand(),
            'add_track_to_playlist': AddTrackToPlaylistCommand(),
            'remove_track_from_playlist': RemoveTrackFromPlaylistCommand(),
            'shuffle_playlist': ShufflePlaylistCommand(),
            'show_playlists': ShowPlaylistsCommand(),
            'show_tracks_for_playlist': ShowTracksForPlaylistCommand(),
            'stop': StopCommand(),
            'show_tracks_with_order': ShowTracksWithOrderCommand(),
            'select_playlist': SelectPlaylistCommand(),
            'play_track': PlayTrackCommand(),
            'play_playlist_loop': PlayPlaylistLoopCommand(),
            'play_track_loop': PlayTrackLoopCommand(),
            'remove_playlist': RemovePlaylistCommand(),
            'unpause': UnpauseCommand(),
            'set_equalizer': SetEqualizerCommand(),
            'save_memento': SaveMementoCommand(),
            'restore_memento': RestoreMementoCommand(),
        }



def main():
    music_server = MusicServer()
    music_server.register_commands()
    music_server.start()