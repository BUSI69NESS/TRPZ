import threading
import time

import pygame

from MusicPlayer.server.core.commands import PlaylistMemento
from MusicPlayer.server.core.database import DatabaseManager
from MusicPlayer.server.core.itrrator import PlaylistIterator


class MusicPlayer:
    def __init__(self):
        pygame.init()
        self.playing = False
        self.current_playlist_id = None
        self.db_manager = DatabaseManager()
        self.memento_stack = []


    def create_playlist_memento(self):
        if self.current_playlist_id is not None:
            tracks = self.db_manager.get_tracks_for_playlist(self.current_playlist_id)
            return PlaylistMemento(self.current_playlist_id, tracks)
        return None

    def restore_playlist_from_memento(self, playlist_memento):
        client_socket = None
        if playlist_memento:
            self.current_playlist_id = playlist_memento.playlist_id
            self.db_manager.remove_track_from_playlist(self.current_playlist_id, "",client_socket, value = 1)
            for position, (title, path) in enumerate(playlist_memento.tracks):
                self.db_manager.add_track_to_playlist(self.current_playlist_id, title, path,client_socket, value = 1)



    def play_in_thread(self, client_socket):
        client_socket.sendall(f"Playing........".encode('utf-8'))
        if not self.current_playlist_id:
            client_socket.sendall("No playlist selected. Create or select a playlist.".encode('utf-8'))
            return
        tracks = self.db_manager.get_tracks_for_playlist(self.current_playlist_id)

        if not tracks:
            client_socket.sendall("Current playlist is empty. Add some songs.".encode('utf-8'))
            return

        playlist_iterator = PlaylistIterator(tracks)
        for track in playlist_iterator:
            pygame.mixer.music.load(track[1])
            pygame.mixer.music.play()
            self.playing = True

            while pygame.mixer.music.get_busy() and self.playing:
                time.sleep(1)

            if not self.playing:
                break

    def play(self, client_socket):
        play_thread = threading.Thread(target=self.play_in_thread, args= (client_socket,))
        play_thread.start()

    def pause(self, client_socket):
        pygame.mixer.music.pause()
        self.playing = False
        client_socket.sendall("Paused".encode('utf-8'))

    def add_playlist(self, playlist_name, client_socket):
        playlist_id = self.db_manager.create_playlist(playlist_name,client_socket)
        self.current_playlist_id = playlist_id


    def add_track_to_playlist(self, playlist_name, track_title, track_path, client_socket):
        if not self.current_playlist_id:
            return

        self.db_manager.add_track_to_playlist(playlist_name, track_title, track_path,client_socket)

    def remove_track_from_playlist(self, playlist_name, track_title, client_socket):
        if not self.current_playlist_id:
            message = "No playlist selected. Create or select a playlist."
            client_socket.sendall(message.encode('utf-8'))
            return

        self.db_manager.remove_track_from_playlist(playlist_name, track_title,client_socket)

    def shuffle_playlist(self, playlist_name, client_socket):
        if not self.current_playlist_id:
            client_socket.sendall("No playlist selected. Create or select a playlist.".encode('utf-8'))
            return

        self.db_manager.shuffle_playlist(playlist_name,client_socket)
        client_socket.sendall(f"Shuffled the playlist '{playlist_name}'.".encode('utf-8'))

    def show_playlists(self, client_socket):
        playlists = self.db_manager.get_playlists()

        if not playlists:
            client_socket.sendall("No playlists found.".encode('utf-8'))
        else:
            message = "Available playlists: \n"
            for playlist in playlists:
                message += f"{playlist[0]}. {playlist[1]} \n"
            client_socket.sendall(message.encode('utf-8'))

    def show_tracks_for_playlist(self, playlist_name, client_socket):
        result = self.db_manager.show_tracks_for_playlist(playlist_name)

        if not result:
            client_socket.sendall("Playlist not found.".encode('utf-8'))
            return

        tracks = self.db_manager.get_tracks_for_playlist(result[0])

        if not tracks:
            client_socket.sendall(f"No tracks found for the playlist '{playlist_name}'.".encode('utf-8'))
        else:
            message = f"Tracks for the playlist '{playlist_name}': \n"
            for track in tracks:
                message += f"{track[0]} - {track[1]} \n"
            client_socket.sendall(message.encode('utf-8'))

    def stop(self, client_socket):
        pygame.mixer.music.stop()
        self.playing = False
        time.sleep(1)
        client_socket.sendall("Music stopped.".encode('utf-8'))

    def show_tracks_with_order(self, playlist_name, client_socket):
        self.db_manager.show_tracks_with_order(playlist_name,client_socket)

    def select_playlist(self, playlist_id, client_socket):
        result = self.db_manager.select_playlist(playlist_id)

        if not result:
            message = "Playlist not found."
            client_socket.sendall(message.encode('utf-8'))
            return

        self.current_playlist_id = result[0]
        message = f"Playlist selected: {self.current_playlist_id}"
        client_socket.sendall(message.encode('utf-8'))

    def play_track_in_thread(self, playlist_name, track_title, client_socket):
        if not self.current_playlist_id:
            message = "No playlist selected. Create or select a playlist."
            client_socket.sendall(message.encode('utf-8'))
            return

        track_id = self.db_manager.get_track_id_by_title(playlist_name, track_title)

        if not track_id:
            message = f"Track '{track_title}' not found in the playlist '{playlist_name}'."
            client_socket.sendall(message.encode('utf-8'))
            return

        track_path = self.db_manager.get_tracks_for_playlist(self.current_playlist_id)[track_id - 1][1]
        pygame.mixer.music.load(track_path)
        pygame.mixer.music.play()
        self.playing = True
        message = f"Playing: {track_title} from the playlist '{playlist_name}'"
        client_socket.sendall(message.encode('utf-8'))

        while pygame.mixer.music.get_busy():
            time.sleep(1)


    def play_track(self, playlist_name, track_title, client_socket):
        play_track_thread = threading.Thread(target=self.play_track_in_thread, args=(playlist_name, track_title, client_socket,))
        play_track_thread.start()

    def play_playlist_loop(self, client_socket):
        if not self.current_playlist_id:
            message = "No playlist selected. Create or select a playlist."
            client_socket.sendall(message.encode('utf-8'))
            return

        while True:
            self.play(client_socket)

    def play_track_loop(self, playlist_name, track_title, client_socket):
        if not self.current_playlist_id:
            client_socket.sendall("No playlist selected. Create or select a playlist.".encode('utf-8'))
            return

        track_id = self.db_manager.get_track_id_by_title(playlist_name, track_title)

        if not track_id:
            client_socket.sendall(f"Track '{track_title}' not found in the playlist '{playlist_name}'.".encode('utf-8'))
            return

        while True:
            self.play_track(playlist_name, track_title, client_socket)

    def remove_playlist(self, playlist_name, client_socket):
        self.db_manager.remove_playlist_by_name(playlist_name,client_socket)

    def unpause(self, client_socket):
        pygame.mixer.music.unpause()
        self.playing = True
        client_socket.sendall("Music resumed.".encode('utf-8'))

    def set_equalizer(self, level, client_socket):
        pygame.mixer.music.set_volume(level)
        client_socket.sendall(f"Equalizer set to level {level}".encode('utf-8'))