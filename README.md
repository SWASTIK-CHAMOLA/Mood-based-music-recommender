# Mood-Based Music Recommender/Player

A mood-based music recommender/player app that uses facial emotion detection to recommend music. The app captures a photo, analyzes the user's mood, and plays music from Spotify or YouTube based on the detected emotion. It features dark and light mode themes and displays album artwork for the recommended music.

## Features
- **Mood Detection**: Capture a photo using your webcam, and the app will analyze the user's mood.
- **Music Recommendation**: Based on the detected mood, the app plays music from Spotify or YouTube.
- **Theme Switching**: Switch between light and dark modes.
- **Album Artwork**: Displays album artwork for the recommended music.
  
## Technologies Used
- **PyQt5**: For creating the graphical user interface.
- **DeepFace**: For facial emotion detection.
- **OpenCV**: For capturing images using the webcam.
- **Spotipy**: For integrating with Spotify to play music.
- **Google YouTube Data API**: For searching and playing music videos from YouTube.
- **Requests**: For making HTTP requests to fetch album artwork.

## Requirements
- **Python 3.x**
- **PyQt5**
- **OpenCV**
- **DeepFace**
- **Spotipy**
- **Google API Client**
- **Requests**

### Install Dependencies
To install the required dependencies, run:

```bash
pip install -r requirements.txt
