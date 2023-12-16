import sqlite3


class DatabaseFacade:
    def __init__(self, db_name="music_player.sqlite"):
        self.db_manager = DatabaseManager(db_name)

    def create_playlist(self, playlist_name, client_socket):
        return self.db_manager.create_playlist(playlist_name, client_socket)

    def add_track_to_playlist(self, playlist_name, track_title, track_path, client_socket, value=0):
        self.db_manager.add_track_to_playlist(playlist_name, track_title, track_path, client_socket, value)

    def remove_track_from_playlist(self, playlist_name, track_title, client_socket, value=0):
        self.db_manager.remove_track_from_playlist(playlist_name, track_title, client_socket, value)

    def shuffle_playlist(self, playlist_name, client_socket):
        self.db_manager.shuffle_playlist(playlist_name, client_socket)

    def get_playlists(self):
        return self.db_manager.get_playlists()

    def get_tracks_for_playlist(self, playlist_id):
        return self.db_manager.get_tracks_for_playlist(playlist_id)

    def show_tracks_with_order(self, playlist_name, client_socket):
        self.db_manager.show_tracks_with_order(playlist_name, client_socket)

    def show_tracks_for_playlist(self,playlist_name):
        return self.db_manager.show_tracks_for_playlist(playlist_name)

    def select_playlist(self,playlist_id):
        return self.db_manager.select_playlist(playlist_id)





class DatabaseManager:
    def __init__(self, db_name="music_player.db"):
        self.db_name = db_name

        with sqlite3.connect(self.db_name) as connection:
            cursor = connection.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS playlists (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tracks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    playlist_id INTEGER,
                    title TEXT NOT NULL,
                    path TEXT NOT NULL,
                    position INTEGER,
                    UNIQUE (playlist_id, title),
                    FOREIGN KEY (playlist_id) REFERENCES playlists (id)
                )
            """)

    def select_playlist(self,playlist_id):
        with sqlite3.connect(self.db_name) as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT id FROM playlists WHERE id=?", (playlist_id,))
            return cursor.fetchone()

    def show_tracks_for_playlist(self, playlist_name):
        with sqlite3.connect(self.db_name) as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT id FROM playlists WHERE name=?", (playlist_name,))
            return cursor.fetchone()

    def remove_playlist_by_name(self, playlist_name,client_socket):
        with sqlite3.connect(self.db_name) as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT id FROM playlists WHERE name=?", (playlist_name,))
            playlist_id = cursor.fetchone()

            if not playlist_id:
                client_socket.sendall(f"Playlist '{playlist_name}' not found.".encode('utf-8'))
                return

            cursor.execute("DELETE FROM tracks WHERE playlist_id=?", (playlist_id[0],))
            cursor.execute("DELETE FROM playlists WHERE id=?", (playlist_id[0],))
            client_socket.sendall(f"Playlist '{playlist_name}' and its tracks removed.".encode('utf-8'))

    def get_track_id_by_title(self, playlist_name, track_title):
        with sqlite3.connect(self.db_name) as connection:
            cursor = connection.cursor()
            cursor.execute("""
                SELECT id
                FROM tracks
                WHERE playlist_id = (SELECT id FROM playlists WHERE name=?)
                AND title = ?
            """, (playlist_name, track_title))
            track_id = cursor.fetchone()
            return track_id[0] if track_id else None

    def create_playlist(self, playlist_name,client_socket):
        with sqlite3.connect(self.db_name) as connection:
            cursor = connection.cursor()

            try:
                cursor.execute("INSERT INTO playlists (name) VALUES (?)", (playlist_name,))
                client_socket.sendall(f"Playlist '{playlist_name}' created.".encode('utf-8'))
            except sqlite3.IntegrityError:
                client_socket.sendall(f"Playlist '{playlist_name}' already exists. Ignoring.".encode('utf-8'))

            return cursor.lastrowid

    def add_track_to_playlist(self, playlist_name, track_title, track_path,client_socket,value = 0):
        with sqlite3.connect(self.db_name) as connection:
            cursor = connection.cursor()
            cursor.execute("INSERT OR IGNORE INTO playlists (name) VALUES (?)", (playlist_name,))

            try:
                cursor.execute("""
                    INSERT INTO tracks (playlist_id, title, path, position)
                    VALUES ((SELECT id FROM playlists WHERE name=?), ?, ?, (SELECT COALESCE(MAX(position), 0) + 1 FROM tracks WHERE playlist_id=(SELECT id FROM playlists WHERE name=?)))
                """, (playlist_name, track_title, track_path, playlist_name))
                if value != 1:
                    client_socket.sendall(f"Track '{track_title}' added to the playlist '{playlist_name}'.".encode('utf-8'))
            except sqlite3.IntegrityError:
                if value != 1:
                    client_socket.sendall(f"Track '{track_title}' already exists in the playlist '{playlist_name}'. Ignoring.".encode('utf-8'))
            except Exception as e:
                if value != 1:
                    client_socket.sendall(f"An error occurred while adding track '{track_title}' to the playlist '{playlist_name}': {e}".encode('utf-8'))

    def remove_track_from_playlist(self, playlist_name, track_title,client_socket, value = 0):
        with sqlite3.connect(self.db_name) as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT id FROM playlists WHERE name=?", (playlist_name,))
            playlist_id = cursor.fetchone()

            if not playlist_id:
                if value != 1:
                    client_socket.sendall(f"Playlist '{playlist_name}' not found.".encode('utf-8'))
                return
            if value != 1:
                client_socket.sendall('Track has been successfully deleted'.encode('utf-8'))
            cursor.execute("DELETE FROM tracks WHERE playlist_id=? AND title=?", (playlist_id[0], track_title))

    def shuffle_playlist(self, playlist_name,client_socket):
        with sqlite3.connect(self.db_name) as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT id FROM playlists WHERE name=?", (playlist_name,))
            playlist_id = cursor.fetchone()

            if not playlist_id:
                client_socket.sendall(f"Playlist '{playlist_name}' not found.".encode('utf-8'))
                return

            cursor.execute("""
                SELECT id FROM tracks
                WHERE playlist_id=?
                ORDER BY RANDOM()
            """, (playlist_id[0],))
            shuffled_tracks = cursor.fetchall()

            for index, track_id in enumerate(shuffled_tracks):
                cursor.execute("UPDATE tracks SET position=? WHERE id=?", (index + 1, track_id[0]))

    def get_playlists(self):
        with sqlite3.connect(self.db_name) as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT id, name FROM playlists")
            return cursor.fetchall()

    def get_tracks_for_playlist(self, playlist_id):
        with sqlite3.connect(self.db_name) as connection:
            cursor = connection.cursor()
            cursor.execute("""
                SELECT title, path
                FROM tracks
                WHERE playlist_id = ?
                ORDER BY position
            """, (playlist_id,))
            return cursor.fetchall()

    def show_tracks_with_order(self, playlist_name,client_socket):
        with sqlite3.connect(self.db_name) as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT id FROM playlists WHERE name=?", (playlist_name,))
            playlist_id = cursor.fetchone()

            if not playlist_id:
                client_socket.sendall(f"Playlist '{playlist_name}' not found.".encode('utf-8'))
                return

            cursor.execute("""
                SELECT title, position
                FROM tracks
                WHERE playlist_id = ?
                ORDER BY position
            """, (playlist_id[0],))
            tracks = cursor.fetchall()

            if not tracks:
                client_socket.sendall(f"No tracks found for the playlist '{playlist_name}'.".encode('utf-8'))
            else:
                message = f"Tracks for the playlist '{playlist_name}' with their current order:\n"
                for track in tracks:
                    message += f"{track[1]}. {track[0]}\n"
                client_socket.sendall(message.encode('utf-8'))