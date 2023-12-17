import vlc
import pychromecast
import os
import random
import fnmatch
import time
import logging

# Loading Libraries - should be enough - Make sure VLC is installed this time
# Global variables
player = None
chromecast_device = None
media_status = {"state": "stopped", "position": 0, "duration": 0, "metadata": {}}
playlist = []
current_track_index = 0

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Function to handle exceptions during various operations
def handle_exceptions(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"An error occurred: {str(e)}")
            # Additional actions like logging, notifying the user, or handling the error could be implemented here

    return wrapper

# Function to save the playlist locally
def save_playlist():
    with open("playlist.txt", "w") as file:
        for track in playlist:
            file.write(f"{track}\n")

# Function to load the playlist from a local file
def load_playlist():
    global playlist
    try:
        with open("playlist.txt", "r") as file:
            playlist = [line.strip() for line in file.readlines()]
    except FileNotFoundError:
        logger.warning("Playlist file not found. Creating a new playlist.")

# Function to discover Chromecast devices
@handle_exceptions
def discover_chromecast(device_name):
    cast = None
    chromecasts, _ = pychromecast.get_chromecasts()
    for chromecast in chromecasts:
        if chromecast.device.friendly_name == device_name:
            cast = chromecast
            break
    return cast

# Function to set the Chromecast device
@handle_exceptions
def set_chromecast_device(device_name):
    global chromecast_device
    chromecast_device = discover_chromecast(device_name)

# Function to authenticate NAS
def authenticate_nas(username, password):
    # Implement NAS authentication here - Use a time locked us
    pass

# Function to search for a song in a media folder
def search_for_song(media_folder, song_query):
    matching_files = []
    for root, dirs, files in os.walk(media_folder):
        for file in fnmatch.filter(files, f'*{song_query}*'):
            matching_files.append(os.path.join(root, file))
    return matching_files

# Function to get media metadata
def get_media_metadata(file_path):
    media = vlc.Media(file_path)
    media.parse()
    return {
        "title": media.get_meta(vlc.Meta.Title),
        "artist": media.get_meta(vlc.Meta.Artist),
        "album": media.get_meta(vlc.Meta.Album),
        "genre": media.get_meta(vlc.Meta.Genre),
    }

# Function to update media status
def update_media_status():
    global player, media_status
    if player is not None:
        media_status["state"] = "playing" if player.get_state() == vlc.State.Playing else "paused" if player.get_state() == vlc.State.Paused else "stopped"
        media_status["position"] = player.get_time()
        media_status["duration"] = player.get_length()
        if media_status["state"] == "playing" and current_track_index < len(playlist):
            media_status["metadata"] = get_media_metadata(playlist[current_track_index])

# Function to play the current track
def play_current_track(chromecast_device):
    global player, playlist, current_track_index
    if current_track_index < len(playlist):
        track_to_play = playlist[current_track_index]
        if chromecast_device:
            media = pychromecast.controllers.media.MediaController()
            chromecast_device.register_handler(media)
            chromecast_device.media_controller = media
            media.play_media(track_to_play, "audio/mp3")
        else:
            player = vlc.MediaPlayer(track_to_play)
            player.play()
            update_media_status()
            while media_status["state"] == "playing":
                time.sleep(1)
                update_media_status()
            player.release()
            player = None
        current_track_index += 1

# Function to play random media from a folder
def play_random_media_from_folder(folder_path, chromecast_device):
    global playlist, current_track_index
    media_files = get_media_files_from_folder(folder_path)
    if not media_files:
        logger.warning(f"No media files found in the folder: {folder_path}")
        return

    playlist = random.sample(media_files, len(media_files))
    current_track_index = 0
    if chromecast_device is not None:
        play_current_track(chromecast_device)

# Function to get media files from a folder
def get_media_files_from_folder(folder_path):
    media_files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
    return media_files

# Function to pause media playback
def pause_media():
    global player
    if player is not None:
        player.pause()
        update_media_status()

# Function to stop media playback
def stop_media():
    global player, chromecast_device, media_status
    if chromecast_device:
        chromecast_device.media_controller.stop()
    elif player is not None:
        player.stop()
        update_media_status()

# Function to set volume
def set_volume(volume_level):
    global player, chromecast_device
    if chromecast_device:
        chromecast_device.media_controller.set_volume(float(volume_level) / 100.0)
    elif player is not None:
        player.audio_set_volume(volume_level)

# Function to add a track to the playlist
def add_to_playlist(file_path):
    global playlist
    playlist.append(file_path)

# Function to handle playback events
def playback_events_listener(event, data):
    global player, current_track_index, chromecast_device
    if player is not None:
        if event == "MediaEndReached":
            current_track_index += 1
            play_current_track(chromecast_device)
        elif event == "MediaStateChanged":
            update_media_status()

# Function for Home Assistant integration
def home_assistant_integration():
    # Implement Home Assistant integration here
    pass

# Function to handle commands from Home Assistant
def handle_commands_from_home_assistant(data):
    global player, chromecast_device

    if "command" in data:
        command = data["command"]
        if command == "pause_media":
            pause_media()
        elif command == "stop_media":
            stop_media()
        elif command == "set_volume" and "volume_level" in data:
            volume_level = data["volume_level"]
            set_volume(volume_level)
        elif command == "add_to_playlist" and "file_path" in data:
            file_path = data["file_path"]
            add_to_playlist(file_path)

# Function to update metadata based on received commands
def update_metadata_on_command(data):
    if "file_path" in data:
        file_path = data["file_path"]
        media_status["metadata"] = get_media_metadata(file_path)

# Function to update metadata based on Home Assistant commands
def update_metadata_on_home_assistant_command(data):
    if "file_path" in data:
        file_path = data["file_path"]
        media_status["metadata"] = get_media_metadata(file_path)

# Function to periodically
# publish state updates
def publish_state_updates():
    # Implement state updates logic here
    pass

# Function to periodically publish state updates to Home Assistant
def publish_state_updates_to_home_assistant():
    # Implement state updates to Home Assistant logic here
    pass

# Function to retrieve media metadata
def retrieve_media_metadata(file_path):
    return get_media_metadata(file_path)

# Function to manage a playback queue and add a new track
def manage_playback_queue(new_track):
    add_to_playlist(new_track)

# Additional features - Updated

# Function to capture playback events
def capture_playback_events(event, data):
    playback_events_listener(event, data)

# Function to notify users about playback events
def notify_playback_status():
    # Implement notification logic here
    pass

# Function to enhance the visual elements of the player
def visualize_player_elements():
    # Implement visualization improvements here
    pass

# Function to make the player cross-platform compatible
def make_player_cross_platform_compatible():
    # Implement cross-platform compatibility here
    pass

# Function to optimize the code for performance
def optimize_player_performance():
    # Implement performance optimization here
    pass

# Function to search for media files based on a search query
def search_for_media(media_folder, search_query):
    matching_files = search_for_song(media_folder, search_query)
    return matching_files

# Function to play media files based on a search query
def play_searched_media(media_folder, search_query, chromecast_device):
    global current_track_index
    matching_files = search_for_media(media_folder, search_query)
    if not matching_files:
        logger.warning(f"No matching media found for search query: {search_query}")
        return
    playlist.extend(matching_files)
    current_track_index = 0
    play_current_track(chromecast_device)

# Infinite loop to simulate continuous operation
while True:
    # Update Media Status
    update_media_status()

    # Notify Playback Status
    notify_playback_status()

    # Visualize Player Elements
    visualize_player_elements()

    # Make Player Cross-Platform Compatible
    make_player_cross_platform_compatible()

    # Optimize Player Performance
    optimize_player_performance()

    # Sleep for a short duration before the next iteration
    time.sleep(1)
