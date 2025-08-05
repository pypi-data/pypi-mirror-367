# anno2ls

**anno2ls** is a lightweight helper library to manage image and annotation import/export with [Label Studio](https://labelstud.io/). It simplifies importing images, pushing pre-annotated data (like LabelMe format), and removing tasks from your project using the Label Studio API.

---

## 🔧 Features

- Upload multiple images to a Label Studio project
- Import pre-annotated data (supports LabelMe format)
- Delete empty or all tasks from a project
- Fetch all filenames or task metadata from a project

---

## 📦 Installation

You can install via pip (after publishing to PyPI):

```bash
pip install anno2ls

Or use it locally:

git clone https://github.com/Vaaaaaalllll/anno2ls
cd anno2ls
pip install .
```

---

## 🧠 Usage

from anno2ls import anno2ls

```bash
# Initialize
from anno2ls import anno2ls

api_token = "your_label_studio_token"
ls_url = "https://your.labelstudio.instance"
project_id = 97

anno = anno2ls(token=api_token, url=ls_url)

# Upload all images from a directory
anno.import_images("path/to/image/folder", project_id)

# Import annotations in LabelMe format
anno.import_preannotated("path/to/json/folder", project_id)

# Delete all tasks in the project
anno.delete_all_task(project_id)

# Delete only empty (no annotation) tasks
anno.delete_empty_task(project_id)

# Get list of all task image filenames
filenames = anno.get_all_filenames(project_id)
```

---

## 📝 Annotation Format Support

Currently supported:

* LabelMe: Each image must have a .json file with the same base name (minus prefix) in the specified folder.

---

## 👤 Author

Val Kenneth Arado
📧 aradovalkenneth@gmail.com

---

## 🌐 Project Links

GitHub: https://github.com/Vaaaaaalllll/anno2ls
Label Studio: https://labelstud.io
