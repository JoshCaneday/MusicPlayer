import customtkinter
import os
import pygame
import threading
from mutagen.wave import WAVE
from scrape import Scraper

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.title("Music Scraper & Player")
        self.geometry("1100x700")
        
        self.scrape = Scraper()
        pygame.mixer.init()
        self.music_dir = "./music"
        
        self.current_folder = ""
        self.song_list = []
        self.song_buttons = {}
        self.is_playing = False
        self.current_song_path = ""
        self.current_offset = 0.0
        self.duration = 0.0
        self.current_idx = 0
        self.repeat_state = 0 
        self.current_volume = 0.7 # Default volume

        self.show_home_page()

    def clear_screen(self):
        for child in self.winfo_children():
            child.destroy()

    # --- HOME PAGE ---
    def show_home_page(self):
        self.clear_screen()
        label = customtkinter.CTkLabel(self, text="Music Collections", font=("Arial", 24, "bold"))
        label.pack(pady=20)
        container = customtkinter.CTkScrollableFrame(self, width=500, height=300)
        container.pack(pady=10, padx=20)
        
        if os.path.exists(self.music_dir):
            folders = sorted([f for f in os.listdir(self.music_dir) if os.path.isdir(os.path.join(self.music_dir, f))])
            for folder in folders:
                btn = customtkinter.CTkButton(container, text=folder, command=lambda f=folder: self.load_player(f))
                btn.pack(pady=5, fill="x")
        
        new_btn = customtkinter.CTkButton(self, text="+ New Collection", fg_color="#2ecc71", command=self.show_new_folder_entry)
        new_btn.pack(pady=20)

    def show_new_folder_entry(self):
        self.clear_screen()
        customtkinter.CTkLabel(self, text="Folder Name:", font=("Arial", 18)).pack(pady=20)
        entry = customtkinter.CTkEntry(self, width=300)
        entry.pack(pady=10)
        
        def proceed():
            name = entry.get().strip()
            if name:
                self.current_folder = name
                self.show_download_page()
                
        customtkinter.CTkButton(self, text="Create & Add Links", command=proceed).pack(pady=10)
        customtkinter.CTkButton(self, text="Back", fg_color="transparent", command=self.show_home_page).pack()

    # --- DOWNLOAD PAGE ---
    def show_download_page(self):
        self.clear_screen()
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=4)
        self.grid_rowconfigure(0, weight=1)

        self.dl_sidebar = customtkinter.CTkScrollableFrame(self)
        self.dl_sidebar.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        customtkinter.CTkLabel(self.dl_sidebar, text="Current Songs", font=("Arial", 12, "bold")).pack(pady=5)

        input_area = customtkinter.CTkScrollableFrame(self)
        input_area.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        customtkinter.CTkLabel(input_area, text=f"Adding to: {self.current_folder}", font=("Arial", 20, "bold")).pack(pady=10)
        
        customtkinter.CTkLabel(input_area, text="Add Single Song", font=("Arial", 14, "bold")).pack(pady=(20, 0))
        single_url_entry = customtkinter.CTkEntry(input_area, placeholder_text="YouTube Video URL", width=450)
        single_url_entry.pack(pady=10)

        customtkinter.CTkLabel(input_area, text="Add Playlist Range", font=("Arial", 14, "bold")).pack(pady=(20, 0))
        playlist_url_entry = customtkinter.CTkEntry(input_area, placeholder_text="YouTube Playlist URL", width=450)
        playlist_url_entry.pack(pady=10)
        
        range_frame = customtkinter.CTkFrame(input_area, fg_color="transparent")
        range_frame.pack()
        start_idx = customtkinter.CTkEntry(range_frame, placeholder_text="Start Index (1)", width=100)
        start_idx.pack(side="left", padx=5)
        stop_idx = customtkinter.CTkEntry(range_frame, placeholder_text="Stop Index (N)", width=100)
        stop_idx.pack(side="left", padx=5)

        status_label = customtkinter.CTkLabel(input_area, text="")
        status_label.pack(pady=10)

        def update_dl_sidebar_local():
            for widget in self.dl_sidebar.winfo_children():
                if isinstance(widget, customtkinter.CTkLabel) and widget.cget("text") != "Current Songs":
                    widget.destroy()
            folder_path = os.path.join(self.music_dir, self.current_folder)
            if os.path.exists(folder_path):
                files = sorted([f for f in os.listdir(folder_path) if f.endswith(".wav")])
                for f in files:
                    customtkinter.CTkLabel(self.dl_sidebar, text=f, font=("Arial", 10), wraplength=180).pack(anchor="w", padx=5)

        def trigger_download(mode):
            url = single_url_entry.get().strip() if mode == "single" else playlist_url_entry.get().strip()
            items = None
            if mode == "playlist":
                s, e = start_idx.get().strip(), stop_idx.get().strip()
                if not s: s = "1"
                items = f"{s}-{e}" if e else f"{s}-"

            if not url: return
            status_label.configure(text="Downloading...", text_color="white")
            
            def run():
                success = self.scrape.get(url, self.current_folder, playlist_items=items)
                if success:
                    self.after(0, lambda: status_label.configure(text="Success!", text_color="green"))
                    self.after(0, update_dl_sidebar_local)
                else:
                    self.after(0, lambda: status_label.configure(text="Failed!", text_color="red"))

            threading.Thread(target=run, daemon=True).start()

        customtkinter.CTkButton(input_area, text="Download Single Video", command=lambda: trigger_download("single")).pack(pady=5)
        customtkinter.CTkButton(input_area, text="Download Playlist Range", fg_color="#3498db", command=lambda: trigger_download("playlist")).pack(pady=5)
        customtkinter.CTkButton(input_area, text="Finish & Open Player", fg_color="green", command=lambda: self.load_player(self.current_folder)).pack(pady=30)
        
        update_dl_sidebar_local()

    # --- PLAYER PAGE ---
    def load_player(self, folder):
        self.current_folder = folder
        path = os.path.join(self.music_dir, folder)
        if not os.path.exists(path): os.makedirs(path)
        self.song_list = sorted([f for f in os.listdir(path) if f.endswith(".wav")])
        self.show_player_page()

    def show_player_page(self):
        self.clear_screen()
        self.grid_columnconfigure(0, weight=2)
        self.grid_columnconfigure(1, weight=8)
        self.grid_rowconfigure(0, weight=1)

        sidebar = customtkinter.CTkScrollableFrame(self)
        sidebar.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        player_frame = customtkinter.CTkFrame(self)
        player_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)

        self.current_song_label = customtkinter.CTkLabel(player_frame, text="Select a Song", font=("Arial", 18))
        self.current_song_label.pack(pady=40)

        # Progress Slider
        self.audio_slider = customtkinter.CTkSlider(player_frame, from_=0, to=100, command=self.seek_audio)
        self.audio_slider.set(0)
        self.audio_slider.pack(fill="x", padx=50, pady=10)

        # Control Row
        ctrl_frame = customtkinter.CTkFrame(player_frame, fg_color="transparent")
        ctrl_frame.pack(pady=10)
        
        self.play_btn = customtkinter.CTkButton(ctrl_frame, text="Play", width=100, command=self.toggle_play, fg_color="green")
        self.play_btn.pack(side="left", padx=10)
        
        self.repeat_btn = customtkinter.CTkButton(ctrl_frame, text="No Repeat", width=120, command=self.cycle_repeat, fg_color="#3b3b3b")
        self.repeat_btn.pack(side="left", padx=10)

        # Volume Section
        vol_frame = customtkinter.CTkFrame(player_frame, fg_color="transparent")
        vol_frame.pack(pady=10)
        customtkinter.CTkLabel(vol_frame, text="Volume:").pack(side="left", padx=5)
        self.vol_slider = customtkinter.CTkSlider(vol_frame, from_=0, to=1, width=150, command=self.set_volume)
        self.vol_slider.set(self.current_volume)
        self.vol_slider.pack(side="left", padx=5)

        customtkinter.CTkButton(player_frame, text="Home", command=self.show_home_page).pack(side="bottom", pady=20)

        self.song_buttons = {}
        for i, song in enumerate(self.song_list):
            btn = customtkinter.CTkButton(sidebar, text=song, fg_color="#2ecc71", command=lambda idx=i: self.play_song(idx))
            btn.pack(pady=2, fill="x")
            self.song_buttons[song] = btn

        if self.song_list:
            self.play_song(0)
            self.check_music_end_loop()

    # --- CORE PLAYER LOGIC ---
    def set_volume(self, value):
        self.current_volume = float(value)
        pygame.mixer.music.set_volume(self.current_volume)

    def update_slider_loop(self):
        if hasattr(self, 'audio_slider') and self.audio_slider.winfo_exists():
            if pygame.mixer.music.get_busy() and self.is_playing:
                actual_pos = self.current_offset + (pygame.mixer.music.get_pos() / 1000.0)
                self.audio_slider.set(actual_pos)
                self.after(100, self.update_slider_loop)

    def play_song(self, idx):
        if not self.song_list: return
        self.current_idx = idx
        song_name = self.song_list[idx]
        self.current_song_path = os.path.join(self.music_dir, self.current_folder, song_name)
        
        try:
            audio = WAVE(self.current_song_path)
            self.duration = audio.info.length
            self.audio_slider.configure(to=self.duration)
            self.audio_slider.set(0)
            self.current_offset = 0.0
            
            pygame.mixer.music.load(self.current_song_path)
            pygame.mixer.music.set_volume(self.current_volume) # Apply current volume to new song
            pygame.mixer.music.play()
            self.is_playing = True
            
            self.current_song_label.configure(text=f"Playing: {song_name}")
            self.play_btn.configure(text="Pause", fg_color="orange")
            
            for i, (name, btn) in enumerate(self.song_buttons.items()):
                btn.configure(fg_color="grey" if i == idx else "#2ecc71")
            
            self.update_slider_loop()
        except Exception as e:
            print(f"Playback Error: {e}")

    def toggle_play(self):
        if not self.current_song_path: return
        if self.is_playing:
            pygame.mixer.music.pause()
            self.is_playing = False
            self.play_btn.configure(text="Play", fg_color="green")
        else:
            pygame.mixer.music.unpause()
            self.is_playing = True
            self.play_btn.configure(text="Pause", fg_color="orange")
            self.update_slider_loop()

    def seek_audio(self, value):
        if not self.current_song_path: return
        self.current_offset = float(value)
        pygame.mixer.music.play(start=self.current_offset)
        pygame.mixer.music.set_volume(self.current_volume) # Re-apply volume after play()
        self.is_playing = True
        self.play_btn.configure(text="Pause", fg_color="orange")
        self.update_slider_loop()

    def check_music_end_loop(self):
        if not pygame.mixer.music.get_busy() and self.is_playing:
            if self.repeat_state == 2:
                self.play_song(self.current_idx)
            elif self.repeat_state == 1:
                self.update_repeat_ui(0)
                self.play_song(self.current_idx)
            else:
                self.play_song((self.current_idx + 1) % len(self.song_list))
        
        if hasattr(self, 'audio_slider') and self.audio_slider.winfo_exists():
            self.after(1000, self.check_music_end_loop)

    def update_repeat_ui(self, state):
        self.repeat_state = state
        states = ["No Repeat", "Repeat Once", "Repeat Endlessly"]
        colors = ["#3b3b3b", "#3498db", "#9b59b6"]
        self.repeat_btn.configure(text=states[self.repeat_state], fg_color=colors[self.repeat_state])

    def cycle_repeat(self):
        self.update_repeat_ui((self.repeat_state + 1) % 3)

if __name__ == "__main__":
    app = App()
    app.mainloop()