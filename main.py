import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import re

class ItemDistAnalyser:
    def __init__(self, root):
        self.root = root
        root.title("Item Dist Analyser")
        root.geometry("1100x650")

        self.rooms = {}
        self.containers = {}
        self.outfits = {}
        self.bags = {}
        self.others = {}
        self.all_items_set = set()

        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Treeview", rowheight=25)
        style.map("TButton",
                  background=[("active", "#ececec")],
                  foreground=[("active", "#000")])

        top_frame = ttk.Frame(root)
        top_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(top_frame, text="Upload Room_Dist.txt", command=self.load_rooms_file).pack(side=tk.LEFT, padx=2)
        ttk.Button(top_frame, text="Upload Proced.txt", command=self.load_containers_file).pack(side=tk.LEFT, padx=2)

        self.search_entry = ttk.Entry(top_frame)
        self.search_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

        self.buttons = {}
        for label, cmd, color in [("By Room", self.search_by_room, "#00acc1"),
                                  ("By Container", self.search_by_container, "#fb8c00"),
                                  ("By Item", self.search_by_item, "#8e24aa"),
                                  ("By Outfit", self.search_by_outfit, "#43a047"),
                                  ("By Bag", self.search_by_bag, "#d81b60"),
                                  ("By Other", self.search_by_other, "#546e7a"),
                                  ("Clear", self.clear_output, "#607d8b")]:
            btn = tk.Button(top_frame, text=label, command=cmd, bg=color, fg="white")
            btn.pack(side=tk.LEFT, padx=2)
            self.buttons[label] = btn

        main_pane = ttk.PanedWindow(root, orient=tk.HORIZONTAL)
        main_pane.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.notebook = ttk.Notebook(main_pane)
        self.listboxes = {}
        tab_colors = {"Rooms": "#e0f7fa", "Containers": "#fff3e0", "Items": "#f3e5f5",
                      "Outfits": "#e8f5e9", "Bags": "#fce4ec", "Others": "#eceff1"}
        for name in ["Rooms", "Containers", "Items", "Outfits", "Bags", "Others"]:
            frame = tk.Frame(self.notebook, bg=tab_colors[name])
            lb = tk.Listbox(frame)
            lb.pack(fill=tk.BOTH, expand=True)
            lb.bind('<<ListboxSelect>>', self.on_listbox_select)
            self.notebook.add(frame, text=name)
            self.listboxes[name.lower()] = lb
        main_pane.add(self.notebook, weight=1)

        right_frame = ttk.Frame(main_pane)
        main_pane.add(right_frame, weight=3)

        columns = ("Type", "Name", "Details")
        self.tree = ttk.Treeview(right_frame, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=250)
        self.tree.pack(fill=tk.BOTH, expand=True)

        # Define Treeview tags/colors
        self.tree.tag_configure("Room", background="#b2ebf2")
        self.tree.tag_configure("Container", background="#ffe0b2")
        self.tree.tag_configure("Item", background="#e1bee7")
        self.tree.tag_configure("Outfit", background="#c8e6c9")
        self.tree.tag_configure("Bag", background="#f8bbd0")
        self.tree.tag_configure("Other", background="#cfd8dc")

    def on_listbox_select(self, event):
        lb = event.widget
        selection = lb.curselection()
        if selection:
            value = lb.get(selection[0])
            self.search_entry.delete(0, tk.END)
            self.search_entry.insert(0, value)

    def load_rooms_file(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
            self.parse_rooms(text)
            messagebox.showinfo("Info", "Rooms, Outfits, Bags et Others loaded")
            self.update_listboxes()

    def load_containers_file(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
            self.parse_containers(text)
            messagebox.showinfo("Info", "Containers loaded")
            self.update_listboxes()

    def parse_rooms(self, text):
        self.rooms, self.outfits, self.bags, self.others = {}, {}, {}, {}
        text = re.sub(r'local\s+distributionTable\s*=\s*{', '', text).strip()
        blocks = re.finditer(r'(\w+)\s*=\s*{', text)
        for match in blocks:
            name = match.group(1)
            start = match.end()
            brace_count = 1
            i = start
            while i < len(text) and brace_count:
                if text[i] == '{': brace_count += 1
                elif text[i] == '}': brace_count -= 1
                i += 1
            block = text[start:i-1]
            items_match = re.search(r'items\s*=\s*{(.*?)}', block, re.S)
            if name.startswith('Outfit_'):
                self.outfits[name] = self.extract_items(items_match)
            elif name.startswith('Bag_'):
                self.bags[name] = self.extract_items(items_match)
            elif re.match(r'^[A-Z]', name):
                self.others[name] = self.extract_items(items_match)
            else:
                self.rooms[name] = re.findall(r'name\s*=\s*"([^"]+)"', block)
        self.update_all_items()

    def parse_containers(self, text):
        self.containers = {}
        text = re.sub(r'ProceduralDistributions\.list\s*=\s*{', '', text).strip()
        blocks = re.finditer(r'(\w+)\s*=\s*{', text)
        for match in blocks:
            name = match.group(1)
            start = match.end()
            brace_count = 1
            i = start
            while i < len(text) and brace_count:
                if text[i] == '{': brace_count += 1
                elif text[i] == '}': brace_count -= 1
                i += 1
            block = text[start:i-1]
            items_match = re.search(r'items\s*=\s*{(.*?)}', block, re.S)
            self.containers[name] = self.extract_items(items_match)
        self.update_all_items()

    def extract_items(self, items_match):
        if not items_match:
            return []
        raw_items = [i.strip().strip('"').strip("'") for i in items_match.group(1).split(',') if i.strip()]
        items = []
        i = 0
        while i < len(raw_items) - 1:
            item, weight = raw_items[i], raw_items[i + 1]
            if not item.startswith('--'):
                items.append({'name': item, 'weight': weight})
                self.all_items_set.add(item)
            i += 2
        return items

    def update_all_items(self):
        self.items = sorted(list(self.all_items_set))

    def update_listboxes(self):
        data = {
            "rooms": sorted(self.rooms.keys()),
            "containers": sorted(self.containers.keys()),
            "items": self.items,
            "outfits": sorted(self.outfits.keys()),
            "bags": sorted(self.bags.keys()),
            "others": sorted(self.others.keys())
        }
        for key, lb in self.listboxes.items():
            lb.delete(0, tk.END)
            for item in data[key]:
                lb.insert(tk.END, item)

    def search_by_room(self):
        q = self.search_entry.get().strip()
        containers = self.rooms.get(q, [])
        self.show_tree([("Room", q, c) for c in containers])

    def search_by_container(self):
        q = self.search_entry.get().strip()
        rooms = [r for r, plist in self.rooms.items() if q in plist]
        items = [f"{it['name']} ({it['weight']})" for it in self.containers.get(q, [])]
        results = [("Container", q, i) for i in items] + [("Room", r, f"Contains {q}") for r in rooms]
        self.show_tree(results)

    def search_by_item(self):
        q = self.search_entry.get().strip()
        results = []
        for c, items in self.containers.items():
            total = sum(float(it['weight']) for it in items)
            for it in items:
                if it['name'] == q:
                    pct = (float(it['weight']) / total) * 100 if total else 0
                    results.append(("Container", c, f"{it['weight']}/{total:.1f} = {pct:.1f}%"))
        for r, plist in self.rooms.items():
            count = sum(1 for p in plist if any(it['name'] == q for it in self.containers.get(p, [])))
            if count:
                results.append(("Room", r, f"{count} container(s) with item"))
        if not results:
            results.append(("Item", q, "Aucun résultat trouvé."))
        self.show_tree(results)

    def search_by_outfit(self):
        self.search_generic(self.outfits, "Outfit")

    def search_by_bag(self):
        self.search_generic(self.bags, "Bag")

    def search_by_other(self):
        self.search_generic(self.others, "Other")

    def search_generic(self, group, label):
        q = self.search_entry.get().strip()
        items = [f"{it['name']} ({it['weight']})" for it in group.get(q, [])]
        if items:
            results = [(label, q, i) for i in items]
        else:
            results = [(label, q, "Aucun résultat trouvé.")]
        self.show_tree(results)

    def show_tree(self, data):
        self.tree.delete(*self.tree.get_children())
        for type_, name, details in data:
            tag = "Other"
            if type_ == "Room":
                tag = "Room"
            elif type_ == "Container":
                tag = "Container"
            elif type_ == "Item":
                tag = "Item"
            elif type_ == "Outfit":
                tag = "Outfit"
            elif type_ == "Bag":
                tag = "Bag"
            self.tree.insert("", tk.END, values=(type_, name, details), tags=(tag,))

    def clear_output(self):
        self.tree.delete(*self.tree.get_children())

# Main program
if __name__ == "__main__":
    root = tk.Tk()
    app = ItemDistAnalyser(root)
    root.mainloop()
