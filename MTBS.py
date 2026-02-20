import tkinter as tk
from tkinter import ttk, messagebox
import random
import time
from datetime import datetime

# ======================== UI THEME ========================
DARK_BG = "#0a0612"
PANEL_BG = "#1a1426"
ACCENT = "#ff0055"
ACCENT_ALT = "#9900ff"
TEXT_COLOR = "#e0d6ff"
HIGHLIGHT = "#ff5555"
SUCCESS = "#00cc88"
NEUTRAL = "#6a5acd"
BORDER_COLOR = "#3a2a5a"
PREMIUM_COLOR = "#ffd700"
HOVER_COLOR = "#ff3377"
BOOKED_COLOR = "#555555"

USD_TO_INR = 83

# ======================== CORE LOGIC ========================
class MovieTicketBookingSystem:
    def __init__(self):
        self.movies = {
            1: {
                "name": "Inception", 
                "genre": "Sci-Fi", 
                "rating": 9.0,
                "duration": "148 min",
                "price": 4.00 * USD_TO_INR,
                "showtimes": ["2:00 PM", "5:30 PM", "8:00 PM", "10:30 PM"],
                "description": "A thief who steals corporate secrets through dream-sharing technology"
            },
            2: {
                "name": "The Dark Knight", 
                "genre": "Action", 
                "rating": 9.5,
                "duration": "152 min",
                "price": 3.00 * USD_TO_INR,
                "showtimes": ["1:30 PM", "4:45 PM", "7:15 PM", "9:45 PM"],
                "description": "Batman faces the Joker in this epic superhero thriller"
            },
            3: {
                "name": "Interstellar", 
                "genre": "Sci-Fi", 
                "rating": 8.6,
                "duration": "169 min",
                "price": 5 * USD_TO_INR,
                "showtimes": ["3:00 PM", "6:30 PM", "9:00 PM"],
                "description": "A team of explorers travel through a wormhole in space"
            }
        }
        
        self.theaters = {
            1: {
                "seats": {},  # Will store seat data per movie/showtime
                "seat_types": self.generate_seat_types(),
                "total_seats": 48
            }
        }
        
        self.selected_movie = None
        self.selected_showtime = None

    def generate_seat_types(self):
        seat_types = {}
        for row in range(6):
            for col in range(8):
                if row == 0:
                    seat_types[(row, col)] = {"type": "economy", "price_modifier": 0.8}
                elif row >= 4:
                    seat_types[(row, col)] = {"type": "premium", "price_modifier": 1.3}
                else:
                    seat_types[(row, col)] = {"type": "regular", "price_modifier": 1.0}
        return seat_types

    def get_seat_price(self, movie_id, row, col):
        if movie_id not in self.movies:
            return 0.0
        base_price = self.movies[movie_id]["price"]
        seat_type = self.theaters[1]["seat_types"][(row, col)]
        return base_price * seat_type["price_modifier"]

    def toggle_seat(self, theater_id, movie_id, showtime, row, col):
        key = f"{movie_id}_{showtime}"
        
      
        if key not in self.theaters[theater_id]["seats"]:
            self.theaters[theater_id]["seats"][key] = {
                "matrix": [[0 for _ in range(8)] for _ in range(6)],
                "booked_seats": set()
            }
        
        # Don't toggle booked seats
        if (row, col) in self.theaters[theater_id]["seats"][key]["booked_seats"]:
            return self.theaters[theater_id]["seats"][key]["matrix"][row][col]
        
        # Toggle seat selection
        current_state = self.theaters[theater_id]["seats"][key]["matrix"][row][col]
        self.theaters[theater_id]["seats"][key]["matrix"][row][col] = 1 - current_state
        return self.theaters[theater_id]["seats"][key]["matrix"][row][col]

    def get_selected_seats(self, theater_id, movie_id, showtime):
        key = f"{movie_id}_{showtime}"
        if key not in self.theaters[theater_id]["seats"]:
            return []
        
        selected = []
        for row in range(6):
            for col in range(8):
                if self.theaters[theater_id]["seats"][key]["matrix"][row][col] == 1:
                    selected.append((row, col))
        return selected

    def calculate_total_price(self):
        if not self.selected_movie or not self.selected_showtime:
            return 0.0
        
        total = 0.0
        selected_seats = self.get_selected_seats(1, self.selected_movie, self.selected_showtime)
        for row, col in selected_seats:
            total += self.get_seat_price(self.selected_movie, row, col)
        return total

    def book_seats(self, theater_id, movie_id, showtime, seats):
        key = f"{movie_id}_{showtime}"
        
        # Initialize if this is the first booking for this movie/showtime
        if key not in self.theaters[theater_id]["seats"]:
            self.theaters[theater_id]["seats"][key] = {
                "matrix": [[0 for _ in range(8)] for _ in range(6)],
                "booked_seats": set()
            }
        
        # Mark seats as booked
        for row, col in seats:
            self.theaters[theater_id]["seats"][key]["booked_seats"].add((row, col))
            self.theaters[theater_id]["seats"][key]["matrix"][row][col] = 0

#UI 
class MovieBookingApp:
    def __init__(self, root):
        self.root = root
        self.system = MovieTicketBookingSystem()
        self.seat_buttons = []
        self.setup_ui()
        
    def setup_ui(self):
        self.root.title("🎬 CineMatrix Pro - Interactive Booking")
        self.root.geometry("1400x900")
        self.root.configure(bg=DARK_BG)
        
        # Navigation Bar
        self.nav_frame = tk.Frame(self.root, bg=PANEL_BG, height=80)
        self.nav_frame.pack(fill="x", side="top")
        
        self.nav_logo = tk.Label(
            self.nav_frame, 
            text="⚡ CINEMATRIX PRO", 
            font=("Segoe UI", 16, "bold"), 
            bg=PANEL_BG, 
            fg=ACCENT
        )
        self.nav_logo.pack(side="left", padx=20, pady=15)
        
        # Live clock
        self.clock_label = tk.Label(
            self.nav_frame,
            text="",
            font=("Segoe UI", 10),
            bg=PANEL_BG,
            fg=TEXT_COLOR
        )
        self.clock_label.pack(side="right", padx=20, pady=15)
        self.update_clock()
        
        # Main Content Frame
        self.main_frame = tk.Frame(self.root, bg=DARK_BG)
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Left Panel - Movie Selection
        self.movie_panel = tk.Frame(self.main_frame, bg=PANEL_BG, padx=15, pady=15)
        self.movie_panel.pack(side="left", fill="y", padx=(0, 10))
        
        tk.Label(
            self.movie_panel, 
            text="🎬 Now Showing", 
            font=("Segoe UI", 14, "bold"), 
            bg=PANEL_BG, 
            fg=ACCENT
        ).pack(pady=(0, 15))
        
        # Movie selection
        self.movie_frame = tk.Frame(self.movie_panel, bg=PANEL_BG)
        self.movie_frame.pack(fill="both", expand=True)
        
        self.movie_buttons = {}
        for movie_id, details in self.system.movies.items():
            movie_btn = tk.Button(
                self.movie_frame,
                text=f"{details['name']}\n{details['genre']} • {details['rating']}⭐\n₹{details['price']:.2f}",
                font=("Segoe UI", 10),
                bg=NEUTRAL,
                fg=TEXT_COLOR,
                width=20,
                height=4,
                relief="flat",
                command=lambda mid=movie_id: self.select_movie(mid)
            )
            movie_btn.pack(pady=5, fill="x")
            self.movie_buttons[movie_id] = movie_btn
        
        # Showtime selection
        tk.Label(
            self.movie_panel, 
            text="🕐 Showtimes", 
            font=("Segoe UI", 12, "bold"), 
            bg=PANEL_BG, 
            fg=ACCENT
        ).pack(pady=(20, 10))
        
        self.showtime_frame = tk.Frame(self.movie_panel, bg=PANEL_BG)
        self.showtime_frame.pack(fill="x")
        
        self.showtime_buttons = []
        
        # Center Panel - Seat Selection
        self.seat_panel = tk.Frame(self.main_frame, bg=PANEL_BG, padx=15, pady=15)
        self.seat_panel.pack(side="right", fill="both", expand=True)
        
        self.seat_header = tk.Frame(self.seat_panel, bg=PANEL_BG)
        self.seat_header.pack(fill="x", pady=(0, 15))
        
        tk.Label(
            self.seat_header, 
            text="🎭 Select Your Seats", 
            font=("Segoe UI", 14, "bold"), 
            bg=PANEL_BG, 
            fg=ACCENT
        ).pack(side="left")
        
        self.stats_label = tk.Label(
            self.seat_header,
            text="",
            font=("Segoe UI", 10),
            bg=PANEL_BG,
            fg=TEXT_COLOR
        )
        self.stats_label.pack(side="right")
        
        # Seat legend
        self.legend_frame = tk.Frame(self.seat_panel, bg=PANEL_BG)
        self.legend_frame.pack(fill="x", pady=(0, 10))
        
        legends = [
            ("□", "Available", TEXT_COLOR),
            ("■", "Selected", HIGHLIGHT),
            ("▣", "Premium", PREMIUM_COLOR),
            ("▤", "Economy", NEUTRAL),
            ("▦", "Booked", BOOKED_COLOR)
        ]
        
        for symbol, text, color in legends:
            legend_item = tk.Frame(self.legend_frame, bg=PANEL_BG)
            legend_item.pack(side="left", padx=10)
            tk.Label(legend_item, text=symbol, font=("Segoe UI", 12), bg=PANEL_BG, fg=color).pack(side="left")
            tk.Label(legend_item, text=text, font=("Segoe UI", 9), bg=PANEL_BG, fg=TEXT_COLOR).pack(side="left", padx=(5, 0))
        
        # Seat Grid
        self.seat_grid = tk.Frame(self.seat_panel, bg=PANEL_BG)
        self.seat_grid.pack(pady=10)
        
        # Row labels
        for row in range(6):
            tk.Label(
                self.seat_grid,
                text=chr(65 + row),
                font=("Segoe UI", 10, "bold"),
                bg=PANEL_BG,
                fg=TEXT_COLOR,
                width=2
            ).grid(row=row, column=0, padx=(0, 5))
        
        self.seat_buttons = []
        for row in range(6):
            row_buttons = []
            for col in range(8):
                btn = tk.Button(
                    self.seat_grid,
                    text=self.get_seat_symbol(row, col),
                    font=("Segoe UI", 10),
                    width=3,
                    height=2,
                    bg=DARK_BG,
                    fg=self.get_seat_color(row, col),
                    relief="flat",
                    command=lambda r=row, c=col: self.select_seat(r, c)
                )
                btn.grid(row=row, column=col+1, padx=2, pady=2)
                btn.bind("<Enter>", lambda e, r=row, c=col: self.on_seat_hover(r, c, True))
                btn.bind("<Leave>", lambda e, r=row, c=col: self.on_seat_hover(r, c, False))
                row_buttons.append(btn)
            self.seat_buttons.append(row_buttons)
        
        # Screen representation
        screen_frame = tk.Frame(self.seat_panel, bg=PANEL_BG)
        screen_frame.pack(pady=20)
        
        tk.Label(
            screen_frame,
            text="◢" + "="*30 + " SCREEN " + "="*30 + "◣",
            font=("Consolas", 8),
            bg=PANEL_BG,
            fg=ACCENT_ALT
        ).pack()
        
        # Right Panel - Booking Summary
        self.summary_panel = tk.Frame(self.main_frame, bg=PANEL_BG, padx=15, pady=15)
        self.summary_panel.pack(fill="both", expand=True, padx=(10, 0))
        
        tk.Label(
            self.summary_panel, 
            text="📋 Booking Summary", 
            font=("Segoe UI", 14, "bold"), 
            bg=PANEL_BG, 
            fg=ACCENT
        ).pack(pady=(0, 15))
        
        # Price display
        self.price_frame = tk.Frame(self.summary_panel, bg=PANEL_BG)
        self.price_frame.pack(fill="x", pady=(0, 10))
        
        self.price_label = tk.Label(
            self.price_frame,
            text="Total: ₹0.00",
            font=("Segoe UI", 16, "bold"),
            bg=PANEL_BG,
            fg=SUCCESS
        )
        self.price_label.pack()
        
        # Booking details
        self.details_text = tk.Text(
            self.summary_panel,
            height=12,
            bg=DARK_BG,
            fg=TEXT_COLOR,
            font=("Consolas", 9),
            wrap="word",
            relief="flat"
        )
        self.details_text.pack(fill="both", expand=True)
        
        # Action Buttons
        self.action_frame = tk.Frame(self.summary_panel, bg=PANEL_BG)
        self.action_frame.pack(fill="x", pady=(15, 0))
        
        self.book_button = tk.Button(
            self.action_frame,
            text="💳 Confirm Booking",
            font=("Segoe UI", 11, "bold"),
            bg=SUCCESS,
            fg=DARK_BG,
            padx=15,
            pady=8,
            relief="flat",
            command=self.confirm_booking
        )
        self.book_button.pack(fill="x", pady=2)
        
        self.clear_button = tk.Button(
            self.action_frame,
            text="🔄 Clear Selection",
            font=("Segoe UI", 11),
            bg=NEUTRAL,
            fg=DARK_BG,
            padx=15,
            pady=8,
            relief="flat",
            command=self.clear_selection
        )
        self.clear_button.pack(fill="x", pady=2)
        
        self.random_button = tk.Button(
            self.action_frame,
            text="🎲 Random Selection",
            font=("Segoe UI", 11),
            bg=ACCENT_ALT,
            fg=DARK_BG,
            padx=15,
            pady=8,
            relief="flat",
            command=self.random_selection
        )
        self.random_button.pack(fill="x", pady=2)
        
        self.update_display()
    
    def update_clock(self):
        current_time = datetime.now().strftime("%H:%M:%S")
        self.clock_label.config(text=f"🕐 {current_time}")
        self.root.after(1000, self.update_clock)
    
    def get_seat_symbol(self, row, col):
        seat_type = self.system.theaters[1]["seat_types"][(row, col)]
        
        # Check if we have a selected movie and showtime
        if self.system.selected_movie is not None and self.system.selected_showtime is not None:
            key = f"{self.system.selected_movie}_{self.system.selected_showtime}"
            if key in self.system.theaters[1]["seats"]:
                if (row, col) in self.system.theaters[1]["seats"][key]["booked_seats"]:
                    return "▦"  # Booked
                elif self.system.theaters[1]["seats"][key]["matrix"][row][col] == 1:
                    return "■"  # Selected
        
        # Default symbols based on seat type
        if seat_type["type"] == "premium":
            return "▣"
        elif seat_type["type"] == "economy":
            return "▤"
        return "□"
    
    def get_seat_color(self, row, col):
        seat_type = self.system.theaters[1]["seat_types"][(row, col)]
        
        # Check if we have a selected movie and showtime
        if self.system.selected_movie is not None and self.system.selected_showtime is not None:
            key = f"{self.system.selected_movie}_{self.system.selected_showtime}"
            if key in self.system.theaters[1]["seats"]:
                if (row, col) in self.system.theaters[1]["seats"][key]["booked_seats"]:
                    return BOOKED_COLOR
                elif self.system.theaters[1]["seats"][key]["matrix"][row][col] == 1:
                    return HIGHLIGHT
        
        # Default colors based on seat type
        if seat_type["type"] == "premium":
            return PREMIUM_COLOR
        elif seat_type["type"] == "economy":
            return NEUTRAL
        return TEXT_COLOR
    
    def select_movie(self, movie_id):
        self.system.selected_movie = movie_id
        
        # Update button states
        for mid, btn in self.movie_buttons.items():
            if mid == movie_id:
                btn.config(bg=ACCENT, fg=DARK_BG)
            else:
                btn.config(bg=NEUTRAL, fg=TEXT_COLOR)
        
        self.update_showtimes()
        self.refresh_seat_display()
    
    def update_showtimes(self):
        # Clear existing showtime buttons
        for btn in self.showtime_buttons:
            btn.destroy()
        self.showtime_buttons.clear()
        
        if self.system.selected_movie:
            showtimes = self.system.movies[self.system.selected_movie]["showtimes"]
            for time in showtimes:
                btn = tk.Button(
                    self.showtime_frame,
                    text=time,
                    font=("Segoe UI", 9),
                    bg=DARK_BG,
                    fg=TEXT_COLOR,
                    width=8,
                    height=1,
                    relief="flat",
                    command=lambda t=time: self.select_showtime(t)
                )
                btn.pack(side="left", padx=2, pady=2)
                self.showtime_buttons.append(btn)
    
    def select_showtime(self, showtime):
        self.system.selected_showtime = showtime
        
        # Update button states
        for btn in self.showtime_buttons:
            if btn.cget("text") == showtime:
                btn.config(bg=ACCENT, fg=DARK_BG)
            else:
                btn.config(bg=DARK_BG, fg=TEXT_COLOR)
        
        self.refresh_seat_display()
    
    def refresh_seat_display(self):
        """Update all seat buttons to reflect current selection"""
        for row in range(6):
            for col in range(8):
                self.seat_buttons[row][col].config(
                    text=self.get_seat_symbol(row, col),
                    fg=self.get_seat_color(row, col),
                    bg=DARK_BG
                )
        self.update_display()
    
    def on_seat_hover(self, row, col, entering):
        if entering:
            # Only highlight if seat is available
            if self.system.selected_movie and self.system.selected_showtime:
                key = f"{self.system.selected_movie}_{self.system.selected_showtime}"
                if key in self.system.theaters[1]["seats"]:
                    if (row, col) not in self.system.theaters[1]["seats"][key]["booked_seats"]:
                        self.seat_buttons[row][col].config(bg=HOVER_COLOR)
                        price = self.system.get_seat_price(self.system.selected_movie, row, col)
                        seat_type = self.system.theaters[1]["seat_types"][(row, col)]["type"]
                        self.stats_label.config(text=f"Seat {chr(65+row)}{col+1} • {seat_type.title()} • ₹{price:.2f}")
        else:
            self.seat_buttons[row][col].config(bg=DARK_BG)
            self.update_stats()
    
    def select_seat(self, row, col):
        if not self.system.selected_movie:
            messagebox.showwarning("No Movie Selected", "Please select a movie first!")
            return
        
        if not self.system.selected_showtime:
            messagebox.showwarning("No Showtime Selected", "Please select a showtime first!")
            return
        
        key = f"{self.system.selected_movie}_{self.system.selected_showtime}"
        
        # Check if seat is already booked
        if key in self.system.theaters[1]["seats"]:
            if (row, col) in self.system.theaters[1]["seats"][key]["booked_seats"]:
                messagebox.showinfo("Seat Booked", f"Seat {chr(65+row)}{col+1} is already booked!")
                return
        
        # Toggle seat selection
        self.system.toggle_seat(1, self.system.selected_movie, self.system.selected_showtime, row, col)
        self.seat_buttons[row][col].config(
            text=self.get_seat_symbol(row, col),
            fg=self.get_seat_color(row, col)
        )
        self.update_display()
    
    def update_stats(self):
        selected_count = 0
        booked_count = 0
        
        if self.system.selected_movie and self.system.selected_showtime:
            key = f"{self.system.selected_movie}_{self.system.selected_showtime}"
            if key in self.system.theaters[1]["seats"]:
                selected_count = len(self.system.get_selected_seats(1, self.system.selected_movie, self.system.selected_showtime))
                booked_count = len(self.system.theaters[1]["seats"][key]["booked_seats"])
        
        self.stats_label.config(text=f"Selected: {selected_count}/48 | Booked: {booked_count}")
    
    def update_display(self):
        self.update_stats()
        self.update_price_display()
        self.update_summary()
    
    def update_price_display(self):
        total = self.system.calculate_total_price()
        self.price_label.config(text=f"Total: ₹{total:.2f}")
    
    def update_summary(self):
        self.details_text.delete(1.0, tk.END)
        
        if self.system.selected_movie:
            movie = self.system.movies[self.system.selected_movie]
            self.details_text.insert(tk.END, f"🎬 Movie: {movie['name']}\n")
            self.details_text.insert(tk.END, f"📱 Genre: {movie['genre']}\n")
            self.details_text.insert(tk.END, f"⭐ Rating: {movie['rating']}\n")
            self.details_text.insert(tk.END, f"⏱️ Duration: {movie['duration']}\n")
            
            if self.system.selected_showtime:
                self.details_text.insert(tk.END, f"🕐 Showtime: {self.system.selected_showtime}\n")
            
            self.details_text.insert(tk.END, f"\n📋 Description:\n{movie['description']}\n\n")
        
        if self.system.selected_movie and self.system.selected_showtime:
            selected_seats = self.system.get_selected_seats(1, self.system.selected_movie, self.system.selected_showtime)
            if selected_seats:
                self.details_text.insert(tk.END, "🎭 Selected Seats:\n")
                for row, col in selected_seats:
                    seat_type = self.system.theaters[1]["seat_types"][(row, col)]
                    price = self.system.get_seat_price(self.system.selected_movie, row, col)
                    self.details_text.insert(tk.END, f"  Seat {chr(65+row)}{col+1} ({seat_type['type'].title()}) - ₹{price:.2f}\n")
            else:
                self.details_text.insert(tk.END, "No seats selected\n")
    
    def clear_selection(self):
        if self.system.selected_movie and self.system.selected_showtime:
            key = f"{self.system.selected_movie}_{self.system.selected_showtime}"
            if key in self.system.theaters[1]["seats"]:
                for row in range(6):
                    for col in range(8):
                        if (row, col) not in self.system.theaters[1]["seats"][key]["booked_seats"]:
                            self.system.theaters[1]["seats"][key]["matrix"][row][col] = 0
                self.refresh_seat_display()
    
    def random_selection(self):
        self.clear_selection()
        if not self.system.selected_movie or not self.system.selected_showtime:
            messagebox.showwarning("Selection Needed", "Please select a movie and showtime first!")
            return
        
        key = f"{self.system.selected_movie}_{self.system.selected_showtime}"
        if key not in self.system.theaters[1]["seats"]:
            self.system.theaters[1]["seats"][key] = {
                "matrix": [[0 for _ in range(8)] for _ in range(6)],
                "booked_seats": set()
            }
        
        available_seats = []
        for row in range(6):
            for col in range(8):
                if (row, col) not in self.system.theaters[1]["seats"][key]["booked_seats"] and \
                   self.system.theaters[1]["seats"][key]["matrix"][row][col] == 0:
                    available_seats.append((row, col))
        
        if len(available_seats) < 2:
            messagebox.showwarning("Not Enough Seats", "Not enough available seats for random selection!")
            return
        
        num_seats = min(random.randint(2, 4), len(available_seats))
        selected_seats = random.sample(available_seats, num_seats)
        
        for row, col in selected_seats:
            self.system.theaters[1]["seats"][key]["matrix"][row][col] = 1
        
        self.refresh_seat_display()
    
    def confirm_booking(self):
        if not self.system.selected_movie:
            messagebox.showwarning("Incomplete", "Please select a movie!")
            return
        
        if not self.system.selected_showtime:
            messagebox.showwarning("Incomplete", "Please select a showtime!")
            return
        
        key = f"{self.system.selected_movie}_{self.system.selected_showtime}"
        if key not in self.system.theaters[1]["seats"]:
            messagebox.showwarning("No Seats", "Please select at least one seat!")
            return
        
        selected_seats = self.system.get_selected_seats(1, self.system.selected_movie, self.system.selected_showtime)
        if not selected_seats:
            messagebox.showwarning("No Seats", "Please select at least one seat!")
            return
        
        total_price = self.system.calculate_total_price()
        movie_name = self.system.movies[self.system.selected_movie]["name"]
        seat_list = ", ".join([f"{chr(65+row)}{col+1}" for row, col in selected_seats])
        
        result = messagebox.askyesno(
            "Confirm Booking",
            f"Confirm booking for {movie_name}?\n"
            f"Seats: {seat_list}\n"
            f"Total: ₹{total_price:.2f}\n"
            f"Showtime: {self.system.selected_showtime}"
        )
        
        if result:
            # Book the seats
            self.system.book_seats(1, self.system.selected_movie, self.system.selected_showtime, selected_seats)
            
            # Generate booking ID
            booking_id = f"BK{int(time.time()) % 1000000:06d}"
            
            # Show confirmation
            messagebox.showinfo(
                "Booking Confirmed! 🎉",
                f"Booking ID: {booking_id}\n"
                f"Movie: {movie_name}\n"
                f"Seats: {seat_list}\n"
                f"Total: ₹{total_price:.2f}\n\n"
                f"Enjoy your movie!"
            )
            
            # Refresh display
            self.refresh_seat_display()

# ======================== RUN APPLICATION ========================
if __name__ == "__main__":
    root = tk.Tk()
    app = MovieBookingApp(root)

    root.mainloop()
