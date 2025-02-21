import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QVBoxLayout, QFrame
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import Qt
import cv2
from deepface import DeepFace
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import random
import requests
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
import webbrowser
from googleapiclient.discovery import build

# Spotify API configuration
SPOTIFY_CLIENT_ID = "your_spotify_client_id"
SPOTIFY_CLIENT_SECRET = "your_spotify_client_secret"
REDIRECT_URI = "http://localhost:host/callback"
SCOPE = "user-library-read playlist-modify-public"

spotify_client = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=SPOTIFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET,
    redirect_uri=REDIRECT_URI,
    scope=SCOPE
))

# YouTube API configuration
YOUTUBE_API_KEY = "your_youtube_api_key"
youtube_client = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)

# Configure retry and timeout for HTTP requests
http_session = requests.Session()
retry_strategy = Retry(total=5, backoff_factor=0.5, status_forcelist=[429, 500, 502, 503, 504])
http_adapter = HTTPAdapter(max_retries=retry_strategy)
http_session.mount('http://', http_adapter)
http_session.mount('https://', http_adapter)
DEFAULT_REQUEST_TIMEOUT = 15

# Define mood-to-genre mapping
MOOD_TO_GENRES = {
    "happy": ["happy", "uplifting"],
    "sad": ["sad", "melancholy", "nostalgic"],
    "angry": ["rock", "intense", "energetic"],
    "calm": ["calm", "relaxing", "peaceful"],
    "excited": ["exciting", "upbeat", "party"]
}

class MoodMusicApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Mood-Based Music Player")
        self.setGeometry(100, 100, 800, 600)
        self.is_dark_mode = True
        self.initialize_ui()

    def initialize_ui(self):
        # Main layout
        layout = QVBoxLayout()

        # Header
        header_label = QLabel("Mood Based Music Recommender")
        header_label.setFont(QFont("Helvetica", 28, QFont.Bold))
        header_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(header_label)

        # Mood display
        self.mood_label = QLabel("Mood: Not Detected")
        self.mood_label.setFont(QFont("Helvetica", 18))
        self.mood_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.mood_label)

        # Image capture button
        self.capture_button = QPushButton("Capture and Detect Mood")
        self.capture_button.setFont(QFont("Helvetica", 16))
        self.capture_button.clicked.connect(self.capture_and_analyze)
        layout.addWidget(self.capture_button)

        # Theme toggle button
        self.theme_button = QPushButton("Switch to Light Mode")
        self.theme_button.setFont(QFont("Helvetica", 16))
        self.theme_button.clicked.connect(self.toggle_theme)
        layout.addWidget(self.theme_button)

        # Album art display
        self.album_art_display = QLabel()
        self.album_art_display.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.album_art_display)

        # Apply layout to central widget
        container = QFrame()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Set initial theme
        self.apply_dark_theme()

    def toggle_theme(self):
        """Switch between dark and light themes."""
        if self.is_dark_mode:
            self.apply_light_theme()
            self.theme_button.setText("Switch to Dark Mode")
        else:
            self.apply_dark_theme()
            self.theme_button.setText("Switch to Light Mode")
        self.is_dark_mode = not self.is_dark_mode

    def apply_dark_theme(self):
        """Enable dark mode styling."""
        self.setStyleSheet("""
            QMainWindow { background-color: #2B2B2B; }
            QLabel { color: #E0E0E0; }
            QPushButton {
                background-color: #555555;
                color: white;
                border-radius: 8px;
            }
        """)

    def apply_light_theme(self):
        """Enable light mode styling."""
        self.setStyleSheet("""
            QMainWindow { background-color: #FFFFFF; }
            QLabel { color: #000000; }
            QPushButton {
                background-color: #007BFF;
                color: white;
                border-radius: 8px;
            }
        """)

    def capture_and_analyze(self):
        image_path = self.capture_image()
        mood = self.analyze_mood(image_path)
        self.mood_label.setText(f"Mood: {mood}")
        self.play_music_based_on_mood(mood)

    def capture_image(self):
        """Capture an image using the webcam."""
        camera = cv2.VideoCapture(0)
        while True:
            ret, frame = camera.read()
            cv2.imshow("Capture Image", frame)
            if cv2.waitKey(1) & 0xFF == ord("c"):
                file_path = "captured_image.jpg"
                cv2.imwrite(file_path, frame)
                break
        camera.release()
        cv2.destroyAllWindows()
        return file_path

    def analyze_mood(self, image_path):
        """Detect mood from an image."""
        try:
            analysis = DeepFace.analyze(img_path=image_path, actions=["emotion"], enforce_detection=False)
            if isinstance(analysis, list):
                analysis = analysis[0]
            return analysis.get("dominant_emotion", "neutral")
        except Exception as e:
            print(f"Error during mood analysis: {e}")
            return "neutral"

    def play_music_based_on_mood(self, mood):
        """Search and play music on Spotify or YouTube based on mood."""
        genres = MOOD_TO_GENRES.get(mood.lower(), ["pop"])
        selected_genre = random.choice(genres)
        print(f"Searching for {selected_genre} music...")

        try:
            # Search for tracks related to the mood using the chosen genre on Spotify
            search_results = spotify_client.search(q=f"genre:{selected_genre}", limit=10, type="track")
            tracks = search_results["tracks"]["items"]

            if tracks:
                track = random.choice(tracks)
                track_url = track['external_urls']['spotify']
                album_art_url = track['album']['images'][0]['url']
                webbrowser.open(track_url)

                # Display album artwork
                response = http_session.get(album_art_url, stream=True, timeout=DEFAULT_REQUEST_TIMEOUT)
                response.raise_for_status()
                pixmap = QPixmap()
                pixmap.loadFromData(response.content)
                self.album_art_display.setPixmap(pixmap.scaled(200, 200, Qt.KeepAspectRatio))
            else:
                print("No music found on Spotify. Trying YouTube...")
                self.play_music_on_youtube(selected_genre)
        except Exception as e:
            print(f"Error during music playback on Spotify: {e}")
            print("Trying YouTube...")
            self.play_music_on_youtube(selected_genre)

    def play_music_on_youtube(self, genre):
        """Search and play music videos on YouTube based on genre."""
        try:
            search_response = youtube_client.search().list(
                q=f"{genre} music",
                part="id,snippet",
                maxResults=1
            ).execute()

            videos = search_response.get("items", [])
            if videos:
                video = videos[0]
                video_id = video["id"]["videoId"]
                video_url = f"https://www.youtube.com/watch?v={video_id}"
                webbrowser.open(video_url)

                # Display video thumbnail
                thumbnail_url = video["snippet"]["thumbnails"]["high"]["url"]
                response = http_session.get(thumbnail_url, stream=True, timeout=DEFAULT_REQUEST_TIMEOUT)
                response.raise_for_status()
                pixmap = QPixmap()
                pixmap.loadFromData(response.content)
                self.album_art_display.setPixmap(pixmap.scaled(180, 180, Qt.KeepAspectRatio))
            else:
                print("No music found on YouTube.")
        except Exception as e:
            print(f"Error during music playback on YouTube: {e}")

# Application entry point
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MoodMusicApp()
    window.show()
    sys.exit(app.exec_())