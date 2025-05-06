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

        # Ajout du bouton pour voir les favoris
        ttk.Button(top_frame, text="View Favorites", command=self.show_favorites).pack(side=tk.LEFT, padx=2)
        # Ajout du bouton pour générer la structure
        ttk.Button(top_frame, text="Generate Structure", command=self.open_generate_structure).pack(side=tk.LEFT, padx=2)

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
        # --- CONTEXT MENU FOR CONTAINERS LISTBOX ---
        self.containers_menu = tk.Menu(self.root, tearoff=0)
        self.containers_menu.add_command(label="Add to favorites list", command=self.add_selected_listbox_container_to_favorites)
        self.listboxes['containers'].bind('<Button-3>', self.on_containers_listbox_right_click)
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

        # Ajout pour gestion des favoris containers
        self.favorite_containers = set()
        self.tree_menu = tk.Menu(self.root, tearoff=0)
        self.tree_menu.add_command(label="Add to favorites list", command=self.add_selected_container_to_favorites)
        self.tree.bind("<Button-3>", self.on_tree_right_click)

        # --- AJOUT : menu contextuel rapide sur la liste principale des conteneurs ---
    def add_selected_container_to_favorites(self):
        selected = self.tree.selection()
        if not selected:
            return
        item_id = selected[0]
        values = self.tree.item(item_id, 'values')
        if len(values) > 1 and values[0] == "Container":
            container_name = values[1]
            if container_name not in self.favorite_containers:
                self.favorite_containers.add(container_name)
                messagebox.showinfo("Favorites", f"Container '{container_name}' added to favorites list.")
            else:
                messagebox.showinfo("Favorites", f"Container '{container_name}' is already in favorites.")

    def on_tree_right_click(self, event):
        item_id = self.tree.identify_row(event.y)
        if not item_id:
            return
        values = self.tree.item(item_id, 'values')
        if len(values) > 0 and values[0] == "Container":
            self.tree.selection_set(item_id)
            self.tree_menu.post(event.x_root, event.y_root)

    def add_selected_listbox_container_to_favorites(self):
        lb = self.listboxes['containers']
        selection = lb.curselection()
        if not selection:
            return
        container_name = lb.get(selection[0])
        if container_name not in self.favorite_containers:
            self.favorite_containers.add(container_name)
            messagebox.showinfo("Favorites", f"Container '{container_name}' added to favorites list.")
        else:
            messagebox.showinfo("Favorites", f"Container '{container_name}' is already in favorites.")

    def on_containers_listbox_right_click(self, event):
        lb = self.listboxes['containers']
        # Sélectionne l'élément sous la souris
        index = lb.nearest(event.y)
        if index >= 0:
            lb.selection_clear(0, tk.END)
            lb.selection_set(index)
            lb.activate(index)
            lb.focus_set()
            try:
                self.containers_menu.tk_popup(event.x_root, event.y_root)
            finally:
                self.containers_menu.grab_release()

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
            messagebox.showinfo("Info", "Rooms, Outfits, Bags and Others loaded")
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
            results.append(("Item", q, "No results found."))
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
            results = [(label, q, "No results found.")]
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

    def show_favorites(self):
        # Nouvelle fenêtre pour édition des favoris
        fav_win = tk.Toplevel(self.root)
        fav_win.title("Favorite Containers")
        fav_win.geometry("350x400")
        tk.Label(fav_win, text="Favorite containers list:").pack(pady=5)
        fav_listbox = tk.Listbox(fav_win, selectmode=tk.MULTIPLE)
        fav_listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        for fav in sorted(self.favorite_containers):
            fav_listbox.insert(tk.END, fav)
        def remove_selected():
            selected = list(fav_listbox.curselection())[::-1]
            for idx in selected:
                name = fav_listbox.get(idx)
                fav_listbox.delete(idx)
                self.favorite_containers.discard(name)
        btn_frame = tk.Frame(fav_win)
        btn_frame.pack(pady=5)
        tk.Button(btn_frame, text="Remove selection", command=remove_selected).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Close", command=fav_win.destroy).pack(side=tk.LEFT, padx=5)

    def open_generate_structure(self):
        if not self.favorite_containers:
            messagebox.showinfo("Structure", "No favorite containers to generate.")
            return
        # Dictionnaire temporaire pour stocker les items par container
        container_items = {c: [] for c in self.favorite_containers}
        win = tk.Toplevel(self.root)
        win.title("Generate container structure")
        win.geometry("900x750")
        win.configure(bg="#f4f6fa")
        frame = tk.Frame(win, bg="#f4f6fa")
        frame.pack(fill=tk.BOTH, expand=True)

        # --- Zone items custom du joueur ---
        custom_items_frame = tk.LabelFrame(frame, text="Custom items (one per line)", bg="#e3f2fd", fg="#1565c0", font=("Segoe UI", 10, "bold"), bd=2, relief=tk.GROOVE)
        custom_items_frame.pack(fill=tk.X, padx=14, pady=8)
        custom_items_text = tk.Text(custom_items_frame, height=4, font=("Segoe UI", 10), bg="#ffffff")
        custom_items_text.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5, pady=5)
        update_custom_btn = tk.Button(custom_items_frame, text="Update list", width=18, bg="#90caf9", fg="#0d47a1", font=("Segoe UI", 9, "bold"))
        update_custom_btn.pack(side=tk.RIGHT, padx=5)
        # Listbox pour sélection rapide custom avec scrollbar
        custom_listbox_frame = tk.Frame(frame, bg="#f4f6fa")
        custom_listbox_frame.pack(fill=tk.X, padx=14, pady=2)
        tk.Label(custom_listbox_frame, text="Quick select from your custom items", bg="#f4f6fa", fg="#1976d2", font=("Segoe UI", 9, "italic")).pack(anchor="w")
        custom_listbox = tk.Listbox(custom_listbox_frame, selectmode=tk.MULTIPLE, height=6, font=("Consolas", 10), bg="#e3f2fd")
        custom_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        custom_scroll = tk.Scrollbar(custom_listbox_frame, orient="vertical", command=custom_listbox.yview)
        custom_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        custom_listbox.config(yscrollcommand=custom_scroll.set)
        def update_custom_list():
            custom_listbox.delete(0, tk.END)
            items = [l.strip() for l in custom_items_text.get("1.0", tk.END).splitlines() if l.strip()]
            for it in items:
                custom_listbox.insert(tk.END, it)
        update_custom_btn.config(command=update_custom_list)

        # --- Zone items de base du jeu avec scrollbar ---
        base_items_frame = tk.LabelFrame(frame, text="Default game items (from loaded files)", bg="#e8f5e9", fg="#1b5e20", font=("Segoe UI", 10, "bold"), bd=2, relief=tk.GROOVE)
        base_items_frame.pack(fill=tk.X, padx=14, pady=8)
        base_listbox_frame = tk.Frame(base_items_frame, bg="#e8f5e9")
        base_listbox_frame.pack(fill=tk.X)
        tk.Label(base_listbox_frame, text="Quick select from all known game items", bg="#e8f5e9", fg="#388e3c", font=("Segoe UI", 9, "italic")).pack(anchor="w")
        base_listbox = tk.Listbox(base_listbox_frame, selectmode=tk.MULTIPLE, height=6, font=("Consolas", 10), bg="#e8f5e9")
        base_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        base_scroll = tk.Scrollbar(base_listbox_frame, orient="vertical", command=base_listbox.yview)
        base_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        base_listbox.config(yscrollcommand=base_scroll.set)
        for it in sorted(self.items):
            base_listbox.insert(tk.END, it)

        canv = tk.Canvas(frame, bg="#f4f6fa")
        scroll_y = tk.Scrollbar(frame, orient="vertical", command=canv.yview)
        inner = tk.Frame(canv, bg="#f4f6fa")
        inner.bind("<Configure>", lambda e: canv.configure(scrollregion=canv.bbox("all")))
        canv.create_window((0, 0), window=inner, anchor="nw")
        canv.configure(yscrollcommand=scroll_y.set)
        canv.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0,8))
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        entry_widgets = {}
        for container in sorted(self.favorite_containers):
            group = tk.LabelFrame(inner, text=container, bg="#fffde7", fg="#f57c00", font=("Segoe UI", 10, "bold"), bd=2, relief=tk.GROOVE)
            group.pack(fill=tk.X, padx=10, pady=8, anchor="n")
            tk.Label(group, text="Item name", bg="#fffde7", fg="#e65100", font=("Segoe UI", 9)).grid(row=0, column=0)
            tk.Label(group, text="Spawn chance", bg="#fffde7", fg="#e65100", font=("Segoe UI", 9)).grid(row=0, column=1)
            tk.Label(group, text="Rolls", bg="#fffde7", fg="#e65100", font=("Segoe UI", 9)).grid(row=0, column=2)
            item_var = tk.StringVar()
            chance_var = tk.StringVar(value="5")
            rolls_var = tk.StringVar(value="2")
            entry = tk.Entry(group, textvariable=item_var, width=28, font=("Segoe UI", 10))
            entry.grid(row=1, column=0, padx=2)
            entry2 = tk.Entry(group, textvariable=chance_var, width=8, font=("Segoe UI", 10))
            entry2.grid(row=1, column=1, padx=2)
            entry3 = tk.Entry(group, textvariable=rolls_var, width=8, font=("Segoe UI", 10))
            entry3.grid(row=1, column=2, padx=2)
            # Listbox items du container avec scrollbar
            items_list_frame = tk.Frame(group, bg="#fffde7")
            items_list_frame.grid(row=2, column=0, columnspan=6, pady=3, sticky="ew")
            items_list = tk.Listbox(items_list_frame, width=50, height=3, font=("Consolas", 10), bg="#fffde7")
            items_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            items_scroll = tk.Scrollbar(items_list_frame, orient="vertical", command=items_list.yview)
            items_scroll.pack(side=tk.RIGHT, fill=tk.Y)
            items_list.config(yscrollcommand=items_scroll.set)
            # Fabrique pour callbacks corrects
            def make_refresh_items_list(c, il):
                def _refresh():
                    il.delete(0, tk.END)
                    for idx, d in enumerate(container_items[c]):
                        il.insert(tk.END, f"{d['item']} (Chance: {d['chance']}, Rolls: {d['rolls']})")
                    refresh_all()
                return _refresh
            refresh_items_list = make_refresh_items_list(container, items_list)
            def make_add_item(c, iv, cv, rv, refresh_func):
                def _add():
                    item = iv.get().strip()
                    try:
                        chance = int(cv.get())
                    except ValueError:
                        chance = 5
                    try:
                        rolls = int(rv.get())
                    except ValueError:
                        rolls = 2
                    if item:
                        container_items[c].append({'item': item, 'chance': chance, 'rolls': rolls})
                        refresh_func()
                        iv.set("")
                return _add
            def make_remove_selected(c, il, refresh_func):
                def _remove():
                    sel = list(il.curselection())[::-1]
                    for idx in sel:
                        del container_items[c][idx]
                    refresh_func()
                return _remove
            # Ajout depuis la liste custom
            def make_add_from_custom(c, cv, rv, refresh_func):
                def _add():
                    try:
                        chance = int(cv.get())
                    except ValueError:
                        chance = 5
                    try:
                        rolls = int(rv.get())
                    except ValueError:
                        rolls = 2
                    selected = list(custom_listbox.curselection())
                    for idx in selected:
                        item = custom_listbox.get(idx)
                        if not any(d['item'] == item for d in container_items[c]):
                            container_items[c].append({'item': item, 'chance': chance, 'rolls': rolls})
                    refresh_func()
                return _add
            # Ajout depuis la liste de base
            def make_add_from_base(c, cv, rv, refresh_func):
                def _add():
                    try:
                        chance = int(cv.get())
                    except ValueError:
                        chance = 5
                    try:
                        rolls = int(rv.get())
                    except ValueError:
                        rolls = 2
                    selected = list(base_listbox.curselection())
                    for idx in selected:
                        item = base_listbox.get(idx)
                        if not any(d['item'] == item for d in container_items[c]):
                            container_items[c].append({'item': item, 'chance': chance, 'rolls': rolls})
                    refresh_func()
                return _add
            add_item = make_add_item(container, item_var, chance_var, rolls_var, refresh_items_list)
            remove_selected = make_remove_selected(container, items_list, refresh_items_list)
            add_from_custom = make_add_from_custom(container, chance_var, rolls_var, refresh_items_list)
            add_from_base = make_add_from_base(container, chance_var, rolls_var, refresh_items_list)
            tk.Button(group, text="Add", command=add_item, bg="#ffe0b2", fg="#e65100", font=("Segoe UI", 9, "bold")).grid(row=1, column=3, padx=6)
            tk.Button(group, text="+ from custom list", command=add_from_custom, bg="#e3f2fd", fg="#1976d2", font=("Segoe UI", 9)).grid(row=1, column=4, padx=6)
            tk.Button(group, text="+ from default items", command=add_from_base, bg="#e8f5e9", fg="#388e3c", font=("Segoe UI", 9)).grid(row=1, column=5, padx=6)
            tk.Button(group, text="Remove selection", command=remove_selected, bg="#ffcdd2", fg="#b71c1c", font=("Segoe UI", 9)).grid(row=3, column=0, columnspan=3, pady=2)
            entry_widgets[container] = (item_var, chance_var, rolls_var, items_list)

        # --- Zone de sortie code généré ---
        output_frame = tk.LabelFrame(win, text="Generated Lua code (ready to copy)", bg="#f4f6fa", fg="#263238", font=("Segoe UI", 10, "bold"), bd=2, relief=tk.GROOVE)
        output_frame.pack(fill=tk.BOTH, padx=14, pady=10, expand=True)
        output = tk.Text(output_frame, height=13, font=("Consolas", 11), bg="#eceff1")
        output.pack(fill=tk.BOTH, padx=8, pady=8, expand=True)
        def copy_to_clipboard():
            win.clipboard_clear()
            win.clipboard_append(output.get("1.0", tk.END))
        copy_btn = tk.Button(output_frame, text="Copy code", command=copy_to_clipboard, bg="#b2dfdb", fg="#00695c", font=("Segoe UI", 10, "bold"))
        copy_btn.pack(anchor="e", padx=12, pady=(0,8))
        def generate():
            result = []
            # Header
            result.append("require 'Items/ProceduralDistributions'\n")
            result.append("local CHANGE_MOD_NAME_HERE_Distribution = {")
            # Containers
            for c in sorted(container_items):
                items = container_items[c]
                if not items:
                    continue
                items_str = ', '.join(f'"{d["item"]}", {d["chance"]}' for d in items)
                rolls = items[-1]['rolls'] if items else 2
                struct = f"    {c} = {{ items = {{ {items_str} }}, rolls = {rolls} }},"
                result.append(struct)
            result.append("}\n")
            # Footer Lua code (concaténation ligne à ligne, pas de triple quotes)
            result.append("local ProceduralDistributions_list = ProceduralDistributions.list")
            result.append("local table_insert = table.insert\n")
            result.append("local function insertInDistribution(distrib)")
            result.append("    for k, v in pairs(distrib) do")
            result.append("        local ProceduralDistributions_list_k = ProceduralDistributions_list[k]")
            result.append("        if ProceduralDistributions_list_k then")
            result.append("            local items = v.items")
            result.append("            local ProceduralDistributions_list_k_items = ProceduralDistributions_list_k.items")
            result.append("            if items then")
            result.append("                for i = 1, #items do")
            result.append("                    table_insert(ProceduralDistributions_list_k_items, items[i])")
            result.append("                end")
            result.append("            end")
            result.append("        else")
            result.append('            print("[CHANGE_MOD_NAME_HERE] WARNING: Distribution inexistante: " .. tostring(k))')
            result.append("        end")
            result.append("    end")
            result.append("end\n")
            result.append("insertInDistribution(CHANGE_MOD_NAME_HERE_Distribution)")
            output.delete(1.0, tk.END)
            output.insert(tk.END, '\n'.join(result))
        def refresh_all():
            generate()
        # Génération du texte final
        tk.Button(win, text="Generate structure", command=generate, bg="#bbdefb", fg="#0d47a1", font=("Segoe UI", 10, "bold")).pack(pady=8)
        generate()
        # Appeler generate() après chaque ajout/suppression d'item
        for container in sorted(self.favorite_containers):
            entry_widgets[container][3].bind('<<ListboxSelect>>', lambda e: generate())

# Main program
if __name__ == "__main__":
    root = tk.Tk()
    app = ItemDistAnalyser(root)
    root.mainloop()
