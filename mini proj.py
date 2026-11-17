
import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import date, datetime, timedelta

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


# -------------------- FILES AND THEME --------------------

ACTIVITY_FILE = "activities.json"
SETTINGS_FILE = "settings.json"

BG = "#FFF7FB"
CARD = "#FFFFFF"
PINK = "#F7C8DE"
PINK_DARK = "#C45B8B"
LAVENDER = "#E9DFFC"
PURPLE = "#8064A2"
TEXT = "#382D45"
MUTED = "#81758B"
BORDER = "#F0E5F2"
MINT = "#D7F3E3"
BLUE = "#DDEBFF"


def load_json(filename, default):
    if os.path.exists(filename):
        try:
            with open(filename, "r") as file:
                return json.load(file)
        except (json.JSONDecodeError, OSError):
            return default
    return default


def save_json(filename, data):
    with open(filename, "w") as file:
        json.dump(data, file, indent=4)


# -------------------- MAIN APPLICATION --------------------

class TimeTrackApp:

    def __init__(self, root):
        self.root = root
        self.root.title("TimeTrack - Screen Time & Productivity Tracker")
        self.root.geometry("1100x720")
        self.root.minsize(900, 620)
        self.root.configure(bg=BG)

        self.activities = load_json(ACTIVITY_FILE, [])
        self.settings = load_json(SETTINGS_FILE, {"daily_goal": 180})

        self.editing_index = None
        self.report_canvas = None

        self.setup_style()
        self.create_header()
        self.create_tabs()

        self.refresh_all()

    # -------------------- STYLE --------------------

    def setup_style(self):
        style = ttk.Style()
        style.theme_use("clam")

        style.configure(
            "Treeview",
            background=CARD,
            foreground=TEXT,
            rowheight=30,
            fieldbackground=CARD,
            font=("Arial", 10)
        )

        style.configure(
            "Treeview.Heading",
            background=LAVENDER,
            foreground=TEXT,
            font=("Arial", 10, "bold")
        )

        style.map(
            "Treeview",
            background=[("selected", PINK)],
            foreground=[("selected", TEXT)]
        )

        style.configure(
            "TNotebook",
            background=BG,
            borderwidth=0
        )

        style.configure(
            "TNotebook.Tab",
            background=LAVENDER,
            foreground=TEXT,
            padding=[16, 9],
            font=("Arial", 10, "bold")
        )

        style.map(
            "TNotebook.Tab",
            background=[("selected", PINK)],
            foreground=[("selected", TEXT)]
        )

    # -------------------- HELPER FUNCTIONS --------------------

    def make_button(self, parent, text, command, color=PINK):
        return tk.Button(
            parent,
            text=text,
            command=command,
            bg=color,
            fg=TEXT,
            activebackground=LAVENDER,
            activeforeground=TEXT,
            relief="flat",
            font=("Arial", 10, "bold"),
            padx=13,
            pady=7,
            cursor="hand2"
        )

    def make_card(self, parent, title):
        frame = tk.Frame(
            parent,
            bg=CARD,
            highlightbackground=BORDER,
            highlightthickness=1
        )

        tk.Label(
            frame,
            text=title,
            bg=CARD,
            fg=TEXT,
            font=("Arial", 12, "bold")
        ).pack(anchor="w", padx=15, pady=(12, 5))

        return frame

    def get_today_activities(self):
        today = date.today().isoformat()
        return [
            a for a in self.activities
            if a.get("date") == today
        ]

    def get_productive_minutes(self):
        return sum(
            int(a.get("duration", 0))
            for a in self.get_today_activities()
            if a.get("productive", False)
        )

    def get_screen_minutes(self):
        return sum(
            int(a.get("duration", 0))
            for a in self.get_today_activities()
            if a.get("screen_time", False)
        )

    def format_time(self, minutes):
        hours = minutes // 60
        mins = minutes % 60

        if hours:
            return f"{hours} hr {mins} min"

        return f"{mins} min"

    # -------------------- HEADER --------------------

    def create_header(self):
        header = tk.Frame(self.root, bg=BG)
        header.pack(fill="x", padx=25, pady=18)

        tk.Label(
            header,
            text="♡ TimeTrack",
            bg=BG,
            fg=PINK_DARK,
            font=("Arial", 24, "bold")
        ).pack(side="left")

        tk.Label(
            header,
            text="Screen Time & Productivity Tracker",
            bg=BG,
            fg=MUTED,
            font=("Arial", 10)
        ).pack(side="left", padx=15, pady=10)

        tk.Label(
            header,
            text=date.today().strftime("%d %B %Y"),
            bg=BG,
            fg=PURPLE,
            font=("Arial", 10, "bold")
        ).pack(side="right", pady=10)

    # -------------------- TABS --------------------

    def create_tabs(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        self.dashboard_tab = tk.Frame(self.notebook, bg=BG)
        self.add_tab = tk.Frame(self.notebook, bg=BG)
        self.history_tab = tk.Frame(self.notebook, bg=BG)
        self.reports_tab = tk.Frame(self.notebook, bg=BG)
        self.goals_tab = tk.Frame(self.notebook, bg=BG)

        self.notebook.add(self.dashboard_tab, text="Dashboard")
        self.notebook.add(self.add_tab, text="Add Activity")
        self.notebook.add(self.history_tab, text="Activity History")
        self.notebook.add(self.reports_tab, text="Reports")
        self.notebook.add(self.goals_tab, text="Goals")

        self.create_dashboard()
        self.create_add_activity()
        self.create_history()
        self.create_reports()
        self.create_goals()

    # -------------------- DASHBOARD --------------------

    def create_dashboard(self):
        container = tk.Frame(self.dashboard_tab, bg=BG)
        container.pack(fill="both", expand=True, padx=20, pady=20)

        tk.Label(
            container,
            text="Your Daily Overview ♡",
            bg=BG,
            fg=TEXT,
            font=("Arial", 19, "bold")
        ).pack(anchor="w", pady=(0, 15))

        cards = tk.Frame(container, bg=BG)
        cards.pack(fill="x")

        self.screen_card = self.make_card(cards, "Screen Time")
        self.screen_card.pack(side="left", fill="both", expand=True, padx=5)

        self.screen_value = tk.Label(
            self.screen_card,
            text="0 min",
            bg=CARD,
            fg=PINK_DARK,
            font=("Arial", 21, "bold")
        )
        self.screen_value.pack(anchor="w", padx=15, pady=10)

        self.productive_card = self.make_card(cards, "Productive Time")
        self.productive_card.pack(side="left", fill="both", expand=True, padx=5)

        self.productive_value = tk.Label(
            self.productive_card,
            text="0 min",
            bg=CARD,
            fg=PURPLE,
            font=("Arial", 21, "bold")
        )
        self.productive_value.pack(anchor="w", padx=15, pady=10)

        self.goal_card = self.make_card(cards, "Daily Goal Progress")
        self.goal_card.pack(side="left", fill="both", expand=True, padx=5)

        self.goal_value = tk.Label(
            self.goal_card,
            text="0%",
            bg=CARD,
            fg=PURPLE,
            font=("Arial", 21, "bold")
        )
        self.goal_value.pack(anchor="w", padx=15, pady=10)

        summary = self.make_card(container, "Today's Activities")
        summary.pack(fill="both", expand=True, pady=20)

        self.today_list = tk.Listbox(
            summary,
            bg=CARD,
            fg=TEXT,
            font=("Arial", 11),
            relief="flat",
            height=10
        )
        self.today_list.pack(fill="both", expand=True, padx=15, pady=10)

    def refresh_dashboard(self):
        screen = self.get_screen_minutes()
        productive = self.get_productive_minutes()
        goal = int(self.settings.get("daily_goal", 180))

        self.screen_value.config(text=self.format_time(screen))
        self.productive_value.config(text=self.format_time(productive))

        percentage = int((productive / goal) * 100) if goal > 0 else 0
        self.goal_value.config(text=f"{percentage}%")

        self.today_list.delete(0, tk.END)

        activities = self.get_today_activities()

        if not activities:
            self.today_list.insert(tk.END, "No activities added today.")
        else:
            for activity in activities:
                name = activity.get("name", "Untitled")
                duration = activity.get("duration", 0)
                category = activity.get("category", "Other")

                self.today_list.insert(
                    tk.END,
                    f"♡  {name}  |  {duration} min  |  {category}"
                )

    # -------------------- ADD / EDIT ACTIVITY --------------------

    def create_add_activity(self):
        container = tk.Frame(self.add_tab, bg=BG)
        container.pack(fill="both", expand=True, padx=30, pady=25)

        tk.Label(
            container,
            text="Add Your Activity ♡",
            bg=BG,
            fg=TEXT,
            font=("Arial", 19, "bold")
        ).pack(anchor="w", pady=(0, 20))

        form = self.make_card(container, "Activity Details")
        form.pack(fill="x", padx=5)

        fields = tk.Frame(form, bg=CARD)
        fields.pack(fill="x", padx=20, pady=15)

        tk.Label(fields, text="Activity Name", bg=CARD, fg=TEXT).grid(
            row=0, column=0, sticky="w", pady=8
        )

        self.name_entry = tk.Entry(fields, width=35, font=("Arial", 11))
        self.name_entry.grid(row=0, column=1, sticky="w", padx=15, pady=8)

        tk.Label(fields, text="Date (YYYY-MM-DD)", bg=CARD, fg=TEXT).grid(
            row=1, column=0, sticky="w", pady=8
        )

        self.date_entry = tk.Entry(fields, width=35, font=("Arial", 11))
        self.date_entry.grid(row=1, column=1, sticky="w", padx=15, pady=8)
        self.date_entry.insert(0, date.today().isoformat())

        tk.Label(fields, text="Duration (minutes)", bg=CARD, fg=TEXT).grid(
            row=2, column=0, sticky="w", pady=8
        )

        self.duration_entry = tk.Entry(fields, width=35, font=("Arial", 11))
        self.duration_entry.grid(row=2, column=1, sticky="w", padx=15, pady=8)

        tk.Label(fields, text="Category", bg=CARD, fg=TEXT).grid(
            row=3, column=0, sticky="w", pady=8
        )

        self.category_var = tk.StringVar(value="Study")

        categories = [
            "Study",
            "Education",
            "Work",
            "Entertainment",
            "Social Media",
            "Health",
            "Other"
        ]

        self.category_menu = ttk.Combobox(
            fields,
            textvariable=self.category_var,
            values=categories,
            state="readonly",
            width=32
        )
        self.category_menu.grid(row=3, column=1, sticky="w", padx=15, pady=8)

        self.screen_var = tk.BooleanVar(value=True)
        self.productive_var = tk.BooleanVar(value=False)

        tk.Checkbutton(
            fields,
            text="Count as Screen Time",
            variable=self.screen_var,
            bg=CARD,
            fg=TEXT,
            activebackground=CARD
        ).grid(row=4, column=1, sticky="w", padx=15, pady=5)

        tk.Checkbutton(
            fields,
            text="Count as Productive Time",
            variable=self.productive_var,
            bg=CARD,
            fg=TEXT,
            activebackground=CARD
        ).grid(row=5, column=1, sticky="w", padx=15, pady=5)

        button_frame = tk.Frame(container, bg=BG)
        button_frame.pack(anchor="w", padx=5, pady=18)

        self.save_button = self.make_button(
            button_frame,
            "♡ Save Activity",
            self.add_activity
        )
        self.save_button.pack(side="left", padx=(0, 10))

        self.cancel_button = self.make_button(
            button_frame,
            "Cancel Edit",
            self.cancel_edit,
            LAVENDER
        )
        self.cancel_button.pack(side="left")
        self.cancel_button.pack_forget()

    def clear_activity_form(self):
        self.name_entry.delete(0, tk.END)

        self.date_entry.delete(0, tk.END)
        self.date_entry.insert(0, date.today().isoformat())

        self.duration_entry.delete(0, tk.END)

        self.category_var.set("Study")
        self.screen_var.set(True)
        self.productive_var.set(False)

    def add_activity(self):
        name = self.name_entry.get().strip()
        activity_date = self.date_entry.get().strip()
        duration_text = self.duration_entry.get().strip()

        if not name:
            messagebox.showwarning("Missing Details", "Please enter an activity name.")
            return

        try:
            datetime.strptime(activity_date, "%Y-%m-%d")
        except ValueError:
            messagebox.showwarning(
                "Invalid Date",
                "Please enter the date in YYYY-MM-DD format."
            )
            return

        try:
            duration = int(duration_text)
            if duration <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning(
                "Invalid Duration",
                "Please enter a valid duration in minutes."
            )
            return

        activity = {
            "name": name,
            "date": activity_date,
            "duration": duration,
            "category": self.category_var.get(),
            "screen_time": self.screen_var.get(),
            "productive": self.productive_var.get()
        }

        if self.editing_index is not None:
            index = self.editing_index
            old_activity = self.activities[index]

            self.activities[index] = activity

            try:
                save_json(ACTIVITY_FILE, self.activities)
            except OSError as error:
                self.activities[index] = old_activity
                messagebox.showerror("Save Error", str(error))
                return

            self.cancel_edit()
            self.refresh_all()
            messagebox.showinfo("Updated", "Activity updated successfully ♡")

        else:
            self.activities.append(activity)

            try:
                save_json(ACTIVITY_FILE, self.activities)
            except OSError as error:
                self.activities.pop()
                messagebox.showerror("Save Error", str(error))
                return

            self.clear_activity_form()
            self.refresh_all()
            messagebox.showinfo("Saved", "Activity saved successfully ♡")

    def edit_activity(self):
        selected = self.history_tree.selection()

        if not selected:
            messagebox.showwarning(
                "Select Activity",
                "Please select an activity to edit."
            )
            return

        index = int(selected[0])

        if index < 0 or index >= len(self.activities):
            return

        activity = self.activities[index]

        self.editing_index = index

        self.name_entry.delete(0, tk.END)
        self.name_entry.insert(0, activity.get("name", ""))

        self.date_entry.delete(0, tk.END)
        self.date_entry.insert(0, activity.get("date", ""))

        self.duration_entry.delete(0, tk.END)
        self.duration_entry.insert(0, str(activity.get("duration", "")))

        self.category_var.set(activity.get("category", "Study"))
        self.screen_var.set(activity.get("screen_time", False))
        self.productive_var.set(activity.get("productive", False))

        self.save_button.config(text="♡ Update Activity")
        self.cancel_button.pack(side="left")

        self.notebook.select(self.add_tab)

    def cancel_edit(self):
        self.editing_index = None
        self.clear_activity_form()

        self.save_button.config(text="♡ Save Activity")
        self.cancel_button.pack_forget()

    # -------------------- ACTIVITY HISTORY --------------------

    def create_history(self):
        container = tk.Frame(self.history_tab, bg=BG)
        container.pack(fill="both", expand=True, padx=20, pady=20)

        tk.Label(
            container,
            text="Activity History",
            bg=BG,
            fg=TEXT,
            font=("Arial", 19, "bold")
        ).pack(anchor="w", pady=(0, 15))

        search_frame = tk.Frame(container, bg=BG)
        search_frame.pack(fill="x", pady=5)

        tk.Label(
            search_frame,
            text="Search Activity:",
            bg=BG,
            fg=TEXT
        ).pack(side="left")

        self.search_entry = tk.Entry(search_frame, width=30)
        self.search_entry.pack(side="left", padx=10)

        self.make_button(
            search_frame,
            "Search",
            self.search_activities,
            LAVENDER
        ).pack(side="left", padx=5)

        self.make_button(
            search_frame,
            "Show All",
            self.refresh_history,
            BLUE
        ).pack(side="left", padx=5)

        table_frame = tk.Frame(container, bg=CARD)
        table_frame.pack(fill="both", expand=True, pady=12)

        columns = (
            "name",
            "date",
            "duration",
            "category",
            "screen",
            "productive"
        )

        self.history_tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            selectmode="browse"
        )

        headings = {
            "name": "Activity Name",
            "date": "Date",
            "duration": "Duration",
            "category": "Category",
            "screen": "Screen Time",
            "productive": "Productive"
        }

        widths = {
            "name": 190,
            "date": 120,
            "duration": 100,
            "category": 140,
            "screen": 110,
            "productive": 110
        }

        for column in columns:
            self.history_tree.heading(column, text=headings[column])
            self.history_tree.column(
                column,
                width=widths[column],
                anchor="center"
            )

        scrollbar = ttk.Scrollbar(
            table_frame,
            orient="vertical",
            command=self.history_tree.yview
        )

        self.history_tree.configure(yscrollcommand=scrollbar.set)

        self.history_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        buttons = tk.Frame(container, bg=BG)
        buttons.pack(anchor="w", pady=8)

        self.make_button(
            buttons,
            "Edit Selected",
            self.edit_activity,
            LAVENDER
        ).pack(side="left", padx=(0, 8))

        self.make_button(
            buttons,
            "Delete Selected",
            self.delete_activity,
            PINK
        ).pack(side="left")

    def refresh_history(self, activities=None):
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)

        if activities is None:
            activities = self.activities

        for index, activity in enumerate(self.activities):
            if activity not in activities:
                continue

            self.history_tree.insert(
                "",
                "end",
                iid=str(index),
                values=(
                    activity.get("name", ""),
                    activity.get("date", ""),
                    f"{activity.get('duration', 0)} min",
                    activity.get("category", ""),
                    "Yes" if activity.get("screen_time") else "No",
                    "Yes" if activity.get("productive") else "No"
                )
            )

    def search_activities(self):
        query = self.search_entry.get().strip().lower()

        if not query:
            self.refresh_history()
            return

        results = [
            activity for activity in self.activities
            if query in activity.get("name", "").lower()
            or query in activity.get("category", "").lower()
            or query in activity.get("date", "").lower()
        ]

        self.refresh_history(results)

    def delete_activity(self):
        selected = self.history_tree.selection()

        if not selected:
            messagebox.showwarning(
                "Select Activity",
                "Please select an activity to delete."
            )
            return

        index = int(selected[0])

        if self.editing_index == index:
            messagebox.showwarning(
                "Activity Being Edited",
                "Please cancel editing before deleting this activity."
            )
            return

        confirm = messagebox.askyesno(
            "Confirm Delete",
            "Are you sure you want to delete this activity?"
        )

        if not confirm:
            return

        deleted_activity = self.activities.pop(index)

        try:
            save_json(ACTIVITY_FILE, self.activities)
        except OSError as error:
            self.activities.insert(index, deleted_activity)
            messagebox.showerror("Delete Error", str(error))
            return

        self.refresh_all()
        messagebox.showinfo("Deleted", "Activity deleted successfully.")

    # -------------------- REPORTS --------------------

    def create_reports(self):
        container = tk.Frame(self.reports_tab, bg=BG)
        container.pack(fill="both", expand=True, padx=20, pady=20)

        tk.Label(
            container,
            text="Your Productivity Reports",
            bg=BG,
            fg=TEXT,
            font=("Arial", 19, "bold")
        ).pack(anchor="w", pady=(0, 10))

        self.report_frame = tk.Frame(container, bg=CARD)
        self.report_frame.pack(fill="both", expand=True, pady=10)

        self.make_button(
            container,
            "Refresh Reports",
            self.refresh_reports,
            LAVENDER
        ).pack(anchor="w", pady=5)

    def refresh_reports(self):
        for widget in self.report_frame.winfo_children():
            widget.destroy()

        if self.report_canvas:
            self.report_canvas.get_tk_widget().destroy()
            self.report_canvas = None

        if not self.activities:
            tk.Label(
                self.report_frame,
                text="Add activities to view your reports ♡",
                bg=CARD,
                fg=MUTED,
                font=("Arial", 12)
            ).pack(pady=40)
            return

        category_totals = {}

        for activity in self.activities:
            category = activity.get("category", "Other")
            category_totals[category] = (
                category_totals.get(category, 0)
                + int(activity.get("duration", 0))
            )

        days = [
            date.today() - timedelta(days=i)
            for i in range(6, -1, -1)
        ]

        productive_totals = []

        for day in days:
            total = sum(
                int(a.get("duration", 0))
                for a in self.activities
                if a.get("date") == day.isoformat()
                and a.get("productive", False)
            )
            productive_totals.append(total)

        figure, axes = plt.subplots(1, 2, figsize=(10, 4))
        figure.patch.set_facecolor(CARD)

        categories = list(category_totals.keys())
        values = list(category_totals.values())

        axes[0].bar(categories, values)
        axes[0].set_title("Time by Category")
        axes[0].set_ylabel("Minutes")
        axes[0].tick_params(axis="x", rotation=35)

        axes[1].plot(
            [day.strftime("%d %b") for day in days],
            productive_totals,
            marker="o"
        )
        axes[1].set_title("Productive Time - Last 7 Days")
        axes[1].set_ylabel("Minutes")
        axes[1].tick_params(axis="x", rotation=35)

        figure.tight_layout()

        self.report_canvas = FigureCanvasTkAgg(
            figure,
            master=self.report_frame
        )

        self.report_canvas.draw()
        self.report_canvas.get_tk_widget().pack(
            fill="both",
            expand=True
        )

        plt.close(figure)

    # -------------------- GOALS --------------------

    def create_goals(self):
        container = tk.Frame(self.goals_tab, bg=BG)
        container.pack(fill="both", expand=True, padx=25, pady=25)

        tk.Label(
            container,
            text="Set Your Daily Goal ♡",
            bg=BG,
            fg=TEXT,
            font=("Arial", 19, "bold")
        ).pack(anchor="w", pady=(0, 20))

        goal_card = self.make_card(container, "Daily Productive Time Goal")
        goal_card.pack(fill="x", padx=5)

        self.goal_entry = tk.Entry(goal_card, width=25, font=("Arial", 12))
        self.goal_entry.pack(anchor="w", padx=20, pady=12)

        self.goal_entry.insert(
            0,
            str(self.settings.get("daily_goal", 180))
        )

        self.make_button(
            goal_card,
            "♡ Save Goal",
            self.save_goal
        ).pack(anchor="w", padx=20, pady=(0, 15))

        self.goal_status = tk.Label(
            container,
            text="",
            bg=BG,
            fg=PURPLE,
            font=("Arial", 12, "bold")
        )
        self.goal_status.pack(anchor="w", padx=5, pady=20)

    def save_goal(self):
        try:
            goal = int(self.goal_entry.get())

            if goal <= 0:
                raise ValueError

        except ValueError:
            messagebox.showwarning(
                "Invalid Goal",
                "Please enter a valid number of minutes."
            )
            return

        old_goal = self.settings.get("daily_goal", 180)
        self.settings["daily_goal"] = goal

        try:
            save_json(SETTINGS_FILE, self.settings)
        except OSError as error:
            self.settings["daily_goal"] = old_goal
            messagebox.showerror("Save Error", str(error))
            return

        self.refresh_all()

        messagebox.showinfo(
            "Goal Saved",
            "Your daily goal has been updated ♡"
        )

    # -------------------- REFRESH EVERYTHING --------------------

    def refresh_all(self):
        self.refresh_dashboard()
        self.refresh_history()
        self.refresh_reports()

        if hasattr(self, "goal_status"):
            goal = int(self.settings.get("daily_goal", 180))
            productive = self.get_productive_minutes()

            self.goal_status.config(
                text=(
                    f"Today's progress: "
                    f"{self.format_time(productive)} / "
                    f"{self.format_time(goal)}"
                )
            )


# -------------------- RUN APPLICATION --------------------

if __name__ == "__main__":
    root = tk.Tk()
    app = TimeTrackApp(root)
    root.mainloop()
