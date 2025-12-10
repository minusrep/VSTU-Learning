import customtkinter as ctk
from tkinter import ttk
from pymongo import MongoClient
from datetime import datetime, timedelta


client = MongoClient("mongodb://localhost:27017/")
db = client["Spotify"]
collection = db["Core"]


def safe_list(value):
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, str):
        return [value]
    return []


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Spotify MongoDB Viewer")
        self.geometry("1700x900")
        ctk.set_appearance_mode("dark")

        # ---------- FILTERS ----------
        filter_frame = ctk.CTkScrollableFrame(self, height=200)
        filter_frame.pack(fill="x", pady=10, padx=10)

        # ---- TEXT FILTERS ----
        self.track_name_entry = ctk.CTkEntry(filter_frame, placeholder_text="Track name...")
        self.track_name_entry.grid(row=0, column=0, padx=5, pady=5)
        self.track_name_entry.bind("<KeyRelease>", lambda e: self.update_table())

        self.artist_entry = ctk.CTkEntry(filter_frame, placeholder_text="Artist name...")
        self.artist_entry.grid(row=0, column=1, padx=5, pady=5)
        self.artist_entry.bind("<KeyRelease>", lambda e: self.update_table())

        self.album_entry = ctk.CTkEntry(filter_frame, placeholder_text="Album name...")
        self.album_entry.grid(row=0, column=2, padx=5, pady=5)
        self.album_entry.bind("<KeyRelease>", lambda e: self.update_table())

        # ---- POPULARITY SLIDERS ----
        self.track_pop_min = ctk.CTkSlider(filter_frame, from_=0, to=100, number_of_steps=100, command=lambda e: self.update_table())
        self.track_pop_max = ctk.CTkSlider(filter_frame, from_=0, to=100, number_of_steps=100, command=lambda e: self.update_table())
        ctk.CTkLabel(filter_frame, text="Track popularity min").grid(row=1, column=0)
        self.track_pop_min.grid(row=2, column=0, padx=5)
        ctk.CTkLabel(filter_frame, text="Track popularity max").grid(row=1, column=1)
        self.track_pop_max.grid(row=2, column=1, padx=5)
        self.track_pop_max.set(100)

        # ---- ARTIST POPULARITY SLIDERS ----
        self.artist_pop_min = ctk.CTkSlider(filter_frame, from_=0, to=100, number_of_steps=100, command=lambda e: self.update_table())
        self.artist_pop_max = ctk.CTkSlider(filter_frame, from_=0, to=100, number_of_steps=100, command=lambda e: self.update_table())
        ctk.CTkLabel(filter_frame, text="Artist popularity min").grid(row=3, column=0)
        self.artist_pop_min.grid(row=4, column=0, padx=5)
        ctk.CTkLabel(filter_frame, text="Artist popularity max").grid(row=3, column=1)
        self.artist_pop_max.grid(row=4, column=1, padx=5)
        self.artist_pop_max.set(100)

        # ---- ARTIST FOLLOWERS ----
        self.follow_min = ctk.CTkSlider(filter_frame, from_=0, to=1_000_000_000, command=lambda e: self.update_table())
        self.follow_max = ctk.CTkSlider(filter_frame, from_=0, to=1_000_000_000, command=lambda e: self.update_table())
        ctk.CTkLabel(filter_frame, text="Artist followers min").grid(row=5, column=0)
        self.follow_min.grid(row=6, column=0, padx=5)
        ctk.CTkLabel(filter_frame, text="Artist followers max").grid(row=5, column=1)
        self.follow_max.grid(row=6, column=1, padx=5)
        self.follow_max.set(1_000_000_000)

        # ---- EXPLICIT ----
        self.explicit_var = ctk.StringVar(value="any")
        ctk.CTkLabel(filter_frame, text="Explicit:").grid(row=0, column=3)
        ctk.CTkOptionMenu(filter_frame, values=["any", "true", "false"],
                          variable=self.explicit_var,
                          command=lambda e: self.update_table()).grid(row=0, column=4, padx=5)

        # ---- ALBUM TYPE ----
        self.album_type_var = ctk.StringVar(value="any")
        ctk.CTkLabel(filter_frame, text="Album Type:").grid(row=1, column=3)
        ctk.CTkOptionMenu(filter_frame, values=["any", "album", "single", "compilation"],
                          variable=self.album_type_var,
                          command=lambda e: self.update_table()).grid(row=1, column=4, padx=5)

        # ---- DATE RANGE ----
        self.date_from = ctk.CTkEntry(filter_frame, placeholder_text="From: YYYY-MM-DD")
        self.date_to = ctk.CTkEntry(filter_frame, placeholder_text="To: YYYY-MM-DD")
        self.date_from.grid(row=2, column=3, padx=5)
        self.date_to.grid(row=2, column=4, padx=5)
        self.date_from.bind("<KeyRelease>", lambda e: self.update_table())
        self.date_to.bind("<KeyRelease>", lambda e: self.update_table())

        # ---- LAST YEAR CHECKBOX ----
        self.last_year_var = ctk.BooleanVar()
        ctk.CTkCheckBox(filter_frame, text="Last year", variable=self.last_year_var,
                        command=self.update_table).grid(row=3, column=3)

        # Refresh button
        ctk.CTkButton(filter_frame, text="Refresh", command=self.update_table).grid(row=3, column=4, padx=5)

        # ---------- TABLE ----------
        table_frame = ctk.CTkFrame(self)
        table_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.columns = [
            "track_id", "track_name", "track_number", "track_popularity",
            "track_duration_ms", "explicit", "artist_name", "artist_popularity",
            "artist_followers", "artist_genres", "album_id", "album_name",
            "album_release_date", "album_total_tracks", "album_type"
        ]

        self.table = ttk.Treeview(table_frame, columns=self.columns, show="headings")
        for col in self.columns:
            self.table.heading(col, text=col)
            self.table.column(col, width=150, anchor="w")

        self.table.pack(fill="both", expand=True)

        self.update_table()

    # -----------------------------------------------------------------------
    def build_query(self):
        query = {}

        # text
        if self.track_name_entry.get().strip():
            query["track_name"] = {"$regex": self.track_name_entry.get().strip(), "$options": "i"}

        if self.artist_entry.get().strip():
            query["artist_name"] = {"$regex": self.artist_entry.get().strip(), "$options": "i"}

        if self.album_entry.get().strip():
            query["album_name"] = {"$regex": self.album_entry.get().strip(), "$options": "i"}

        # numeric pop
        query["track_popularity"] = {"$gte": int(self.track_pop_min.get()), "$lte": int(self.track_pop_max.get())}
        query["artist_popularity"] = {"$gte": int(self.artist_pop_min.get()), "$lte": int(self.artist_pop_max.get())}
        query["artist_followers"] = {"$gte": int(self.follow_min.get()), "$lte": int(self.follow_max.get())}

        # explicit
        if self.explicit_var.get() == "true":
            query["explicit"] = True
        elif self.explicit_var.get() == "false":
            query["explicit"] = False

        # album type
        if self.album_type_var.get() != "any":
            query["album_type"] = self.album_type_var.get()

        # last year
        if self.last_year_var.get():
            query["album_release_date"] = {"$gte": datetime.now() - timedelta(days=365)}

        # date range
        from_val = self.date_from.get().strip()
        to_val = self.date_to.get().strip()

        if from_val or to_val:
            query.setdefault("album_release_date", {})
            if from_val:
                try:
                    query["album_release_date"]["$gte"] = datetime.fromisoformat(from_val)
                except:
                    pass
            if to_val:
                try:
                    query["album_release_date"]["$lte"] = datetime.fromisoformat(to_val)
                except:
                    pass

        return query

    # -----------------------------------------------------------------------
    def update_table(self):
        query = self.build_query()
        docs = list(collection.find(query))

        for row in self.table.get_children():
            self.table.delete(row)

        for d in docs:
            artist_genres = safe_list(d.get("artist_genres"))

            album_date = d.get("album_release_date")
            if isinstance(album_date, datetime):
                album_date = album_date.strftime("%Y-%m-%d")

            self.table.insert("", "end", values=[
                d.get("track_id", ""),
                d.get("track_name", ""),
                d.get("track_number", ""),
                d.get("track_popularity", ""),
                d.get("track_duration_ms", ""),
                d.get("explicit", ""),
                d.get("artist_name", ""),
                d.get("artist_popularity", ""),
                d.get("artist_followers", ""),
                ", ".join(artist_genres),
                d.get("album_id", ""),
                d.get("album_name", ""),
                album_date or "",
                d.get("album_total_tracks", ""),
                d.get("album_type", ""),
            ])


if __name__ == "__main__":
    App().mainloop()
