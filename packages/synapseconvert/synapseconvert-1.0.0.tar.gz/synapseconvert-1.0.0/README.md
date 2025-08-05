# synapseconvert

A simple two-way converter for Synapse-style libraries (collections → categories → items) using Excel and JSON. This is intended for developers working with [Synapse](https://substrate.biblicalstory.org/synapse), a research transport protocol designed for structured academic resources.

---

## 📦 Installation

The recommended way to install is:

```bash
pip install synapseconvert
```

If that doesn’t work, try:

```bash
python3 -m pip install synapseconvert
```

> ⚠️ On macOS or Linux, you may need `sudo` for a global install:
>
> ```bash
> sudo python3 -m pip install synapseconvert
> ```

Alternatively, to avoid permission issues and keep things clean, use a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
pip install synapseconvert
```

### 🔍 Confirm it installed correctly:

```bash
which synapse-upconvert
synapse-upconvert --help
```

If the command isn’t found, try running it as a module:

```bash
python3 -m synapseconvert.upconvert path/to/input.xlsx path/to/output.json
```

Or install from source:

```bash
git clone https://github.com/BiblicalStory/synapseconvert.git
cd synapseconvert
pip install -e .
```

---

## 🛠 Usage

### Convert from Excel to JSON (Upconvert)

```bash
synapse-upconvert path/to/input.xlsx path/to/output.json
```

This reads a spreadsheet and produces a properly nested Synapse metadata file.

### Convert from JSON to Excel (Downconvert)

```bash
synapse-downconvert path/to/input.json path/to/output.xlsx
```

This flattens a Synapse-style JSON file into a spreadsheet for editing or review.

---

## 📄 Spreadsheet Format

The spreadsheet must contain at least the following columns:

### ✅ Required Columns
- `collection` – the name of the collection (uniform across all rows)
- `category` – the name of the group the item belongs to

### ✅ Optional Item Fields
- `title`, `description`, `author`, `url`, `date`, etc. – all other metadata fields are treated as item fields

### ✅ Optional Collection-Level Fields
These are only read from the **first row** and apply to the whole collection:

- `designator` – short tag used to identify the collection (e.g., `"BST"`)
- `collection_url` – base URL for the collection homepage or API

If these are omitted, the following defaults apply:
- `designator`: `"UNK"`
- `collection_url`: `"https://substrate.biblicalstory.org"`

### ⚠️ Tags Field (Special Case)

- If included, `tags` **must be valid JSON** (not comma-separated strings).
- Example:

```json
["Genesis", "Luke"]
```

If the `tags` field contains malformed JSON (e.g., `Genesis, Luke`), the script will skip it and print a warning.

---

## 📁 Sample Templates

- `sample.xlsx`
- `sample.json`

These are included in the installed package and available from the [GitHub repo](https://github.com/sbaylis22/synapseconvert).

---

## 🧠 Why This Exists

Synapse is designed to bring remote research libraries directly into Obsidian. Since BiblicalStory.org cannot create Synapse files for every research repository in existence, this tool allows developers to build and maintain their own Synapse libraries using spreadsheets or JSON. These libraries can then be added to Synapse in Obsidian to allow live query and navigation.

---

## 🔧 Developer Tools

For advanced usage, clone this repo and run locally:

```bash
git clone https://github.com/BiblicalStory/synapseconvert.git
cd synapseconvert
pip install -e .
```

This allows you to edit the source code and extend it for your own domains or institutions.

---

© 2025 BiblicalStory Incorporated. MIT License.
