<p align="center">
  <img src="https://i.postimg.cc/VspF3NCC/Fenix-logo-icon.png" alt="FeniX logo" width="100">
</p>

# FeniX

> **🔥 FeniX — No fluff. No clutter. Just simple, fast, and ready to deploy.**

FeniX is a blazing fast and ultra-minimal Python full-stack web framework.



## Features
- Minimal routing system
- Single HTML template file for all views
- Variable replacement like `{{ name }}`
- Only 2 user files needed (`app.py` and `templates.html`)

## Folder Tree
```bash
myApp/
├── app.py
└── templates.html
````
## Quick Start

```bash
pip install pyfenix
```

## 📜 FeniX CLI Commands

| Command              | Description                                                   | Example Usage           |
|----------------------|---------------------------------------------------------------|-------------------------|
| `fx`                 | Show welcome message, description, and latest information     | `fx`                    |
| `fx version`         | Show the installed FeniX framework version                    | `fx version`            |
| `fx make project`    | Create a new minimal project with `app.py` & `templates.html`  | `fx make project`       |
| `fx server`          | Start the development server in the current directory         | `fx server`             |


---
##### 01. Welcom
![CLI Screenshot](https://i.postimg.cc/QxFdK4B5/image.png)

---
##### 02. Version
![CLI Screenshot](https://i.postimg.cc/BbLfbzhn/image.png)
---
##### 03. Create Project
![CLI Screenshot](https://i.postimg.cc/DZQbDCQm/image.png)
## Example
```python
from fenix import App

app = App()

@app.route("/")
def home():
    return app.render("home", name="Azeem")

app.run()
```
## templates.html
```html
{% template "home" %}
<html><body>Hello {{ name }}</body></html>
```
## License
MIT License


---
