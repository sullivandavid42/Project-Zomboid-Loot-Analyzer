# Project Zomboid Loot Analyzer

This project is a web tool to analyze and explore loot distributions from Project Zomboid mod files.

It helps modders and curious players to:
- Parse and explore **room distributions** (`Room_Dist.txt`),
- Parse **procedural containers** (`Procedural_Dist.txt`),
- Explore **Outfits**, **Bags**, and other special blocks,
- Search for items, containers, rooms, outfits, or bags,
- Find which rooms can contain a container,
- Find which containers or special blocks contain a specific item,
- View spawn weights / chances (NOT RELIABLE YET, SKIP THAT),
- Display results with color-coded, collapsible sections.

---

## 🌟 Features

✅ Parse and visualize rooms, containers, outfits, bags, and “other” blocks  
✅ Search by **container**, **item**, **room**, **outfit**, or **bag**  
✅ Show spawn weights and container/item ratios  
✅ Show which rooms include a given container  
✅ Color-coded panels and buttons for intuitive navigation  
✅ Scrollable and collapsible side panels for easy exploration  
✅ Works completely in the browser — no server, no install

---

## 📦 How to use

1. Clone or download this repository.
2. Open the `Item_Dist_Analyser.html` file in your browser.
3. Upload from the cloned repo:
   -  `Room_Dist.txt` file (rooms, outfits, bags).
   -  `Procedural_Dist.txt` file (containers).
4. Use the search box and buttons to explore the data. You can click on any right column item / room / container / outfit name to auto complete the searchbox.

---

## 🔧 Requirements

- A modern web browser (Chrome, Firefox, Edge, Safari)
- No server, no database, no backend — **everything runs locally**

---

## 🛠 Example use cases

- Find all rooms where the `ToolStoreTools` container can appear.
- Check which containers can spawn a `Sledgehammer`.
- Analyze which outfits drop rare items and their drop chances.
- Explore bag loot and other special blocks.

---

## 💡 Notes

- The tool parses `.txt` files I made in this repo for now, it is a modified version of the game's files. I'll change this system later, but files are up to date at the 05/05/2025 date
- Outfits and Bags are automatically detected by their names (`Outfit_` or `Bag_` prefix).
- Blocks starting with uppercase letters but not `Outfit_` or `Bag_` are treated as “Other”, and sometimes no data can be retrived.

---

## 🤝 Contributing

Pull requests are welcome!  
If you find bugs or want to suggest improvements, feel free to open an issue.

---

## 📜 License

This project is open source and licensed under the MIT License.

---

## 💬 Contact

For questions, feel free to open an issue or reach out on GitHub!
