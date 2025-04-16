import os
import customtkinter as ctk
from tkinter import filedialog
from PIL import Image, ImageTk
import json
from collections import defaultdict

class PowerCropper:
    def __init__(self, root):
        self.root = root
        self.root.title("Power Cropper")

        # --- THEME ---
        ctk.set_default_color_theme("blue")

        self.crop_size = (1024, 1024)
        self.images = []
        self.current_index = 0
        self.cropped_info = {}
        self.cropped_info["data"] = {}
        self.cropped_info_file = "cropped_info.json"
        self.dimension_counts = defaultdict(int)

        self.custom_mode = False
        self.custom_start = None
        self.last_cropped_entry = {}  # Changed to dict
        self.current_folder = None
        self.radio_buttons = {}

        # --- Main Frames ---
        main_frame = ctk.CTkFrame(root)
        main_frame.pack(side=ctk.TOP, fill=ctk.BOTH, expand=True)

        # Left and right frames
        left_frame = ctk.CTkFrame(main_frame)
        left_frame.pack(side=ctk.LEFT, fill=ctk.BOTH, expand=True)

        self.right_frame = ctk.CTkFrame(main_frame, width=200)
        self.right_frame.pack(side=ctk.RIGHT, fill=ctk.Y)
        self.right_frame.pack_propagate(False)
        self.right_frame.pack_forget()

        control_frame = ctk.CTkFrame(root)
        control_frame.pack(side=ctk.BOTTOM, fill=ctk.X, pady=5)

        self.dim_label = ctk.CTkLabel(left_frame, text="", font=("Arial", 12))
        self.dim_label.pack(pady=2)

        # Cropped Info Label
        self.cropped_label = ctk.CTkLabel(left_frame, text="", font=("Arial", 10), text_color="yellow")
        self.cropped_label.pack(pady=2)

        # --- SCROLLABLE CANVAS SETUP ---
        canvas_frame = ctk.CTkFrame(left_frame)
        canvas_frame.pack(fill=ctk.BOTH, expand=True)

        self.canvas = ctk.CTkCanvas(canvas_frame, cursor="cross", bg="black", highlightthickness=0)
        self.canvas.pack(side=ctk.LEFT, fill=ctk.BOTH, expand=True)

        self.v_scroll = ctk.CTkScrollbar(canvas_frame, orientation=ctk.VERTICAL, command=self.canvas.yview)
        self.v_scroll.pack(side=ctk.RIGHT, fill=ctk.Y)
        self.h_scroll = ctk.CTkScrollbar(left_frame, orientation=ctk.HORIZONTAL, command=self.canvas.xview)
        self.h_scroll.pack(fill=ctk.X)

        self.canvas.configure(yscrollcommand=self.v_scroll.set, xscrollcommand=self.h_scroll.set)

        # Mousewheel bindings (platform-independent)
        self.canvas.bind("<Enter>", lambda e: self._bind_mousewheel())
        self.canvas.bind("<Leave>", lambda e: self._unbind_mousewheel())

        open_button = ctk.CTkButton(control_frame, text="Open Folder", command=self.load_folder)
        open_button.pack(side=ctk.LEFT, padx=5)
        self.prev_button = ctk.CTkButton(control_frame, text="Prev", state=ctk.DISABLED, command=self.prev_image)
        self.prev_button.pack(side=ctk.LEFT, padx=5)
        self.next_button = ctk.CTkButton(control_frame, text="Next", state=ctk.DISABLED, command=self.next_image)
        self.next_button.pack(side=ctk.LEFT, padx=5)

        # Size presets + custom
        self.size_var = ctk.StringVar(value="1024x1024")
        size_frame = ctk.CTkFrame(control_frame)
        size_frame.pack(side=ctk.LEFT, padx=10)

        # Portrait/Landscape Preference
        self.orientation_preference = ctk.StringVar(value="portrait")
        ctk.CTkLabel(size_frame, text="Prefer:").pack(side=ctk.LEFT)
        self.portrait_radio = ctk.CTkRadioButton(size_frame, text="Portrait", variable=self.orientation_preference, value="portrait", command=self.update_largest_radio_button)
        self.landscape_radio = ctk.CTkRadioButton(size_frame, text="Landscape", variable=self.orientation_preference, value="landscape", command=self.update_largest_radio_button)
        self.portrait_radio.pack(side=ctk.LEFT)
        self.landscape_radio.pack(side=ctk.LEFT)
        self.orientation_preference.set("portrait")

        self.dimension_labels = [
            ("512x512", "512x512"),
            ("1024x1024", "1024x1024"),
            ("512x768", "512x768"),
            ("768x1024", "768x1024"),
            ("768x512", "768x512"),
            ("1024x768", "1024x768"),
            ("Custom", "custom")
        ]
        self.radio_buttons = {}
        for label in self.dimension_labels:
            rb = ctk.CTkRadioButton(size_frame, text=label[0], variable=self.size_var, 
                                value=label[1], command=self.update_size)
            rb.pack(side=ctk.LEFT)
            self.radio_buttons[label[1]] = rb

        # --- SHORTCUT LEGEND ---
        shortcut_text = "A=Prev  D=Next  S=Save  X=Del W=Last cropped  Wheel=VScroll  Shift+Wheel=HScroll"
        self.shortcut_label = ctk.CTkLabel(control_frame, text=shortcut_text, font=("Arial", 10))
        self.shortcut_label.pack(side=ctk.RIGHT, padx=10)

        # --- DIMENSION COUNTS PANEL ---
        self.counts_frame = ctk.CTkFrame(self.right_frame)
        self.counts_frame.pack(side=ctk.TOP, fill=ctk.BOTH, expand=True)

        self.counts_label = ctk.CTkLabel(self.counts_frame, text="Cropped Dimensions:\n\n", justify=ctk.LEFT, font=("Arial", 16))
        self.counts_label.pack(padx=5, pady=20)

        # "Jump to Last Cropped" Button
        jump_cropped_button = ctk.CTkButton(control_frame, text="Jump to Last Cropped", command=self.jump_to_last_cropped)
        jump_cropped_button.pack(side=ctk.LEFT, padx=5)
        
        self.rect = None
        self.rect_coords = None
        self.current_image = None
        self.save_folder = None
        self.custom_dim_text = None
        self.image_on_canvas = None

        # Event bindings
        self.canvas.bind("<Button-1>", self.on_mouse_down)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_up)
        self.root.bind("a", lambda e: self.prev_image())
        self.root.bind("d", lambda e: self.next_image())
        self.root.bind("s", lambda e: self.quick_save())
        self.root.bind("x", lambda e: self.delete_current_image())
        self.root.bind("<w>", lambda e: self.jump_to_last_cropped())

        # Load cropped info from file
        self.load_cropped_info()
        self.load_last_cropped_entries()  # Load all last cropped entries

    # Mousewheel support
    def _on_mousewheel(self, event):
        # Windows, macOS
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def _on_mousewheel_linux_up(self, event):
        # Linux scroll up
        self.canvas.yview_scroll(-1, "units")

    def _on_mousewheel_linux_down(self, event):
        # Linux scroll down
        self.canvas.yview_scroll(1, "units")

    def _bind_mousewheel(self):
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind_all("<Shift-MouseWheel>", lambda e: self.canvas.xview_scroll(int(-1*(e.delta/120)), "units"))
        self.canvas.bind_all("<Button-4>", self._on_mousewheel_linux_up)
        self.canvas.bind_all("<Button-5>", self._on_mousewheel_linux_down)
        # Horizontal scroll (Linux)
        self.canvas.bind_all("<Shift-Button-4>", lambda e: self.canvas.xview_scroll(-1, "units"))
        self.canvas.bind_all("<Shift-Button-5>", lambda e: self.canvas.xview_scroll(1, "units"))

    def _unbind_mousewheel(self):
        self.canvas.unbind_all("<MouseWheel>")
        self.canvas.unbind_all("<Button-4>")
        self.canvas.unbind_all("<Button-5>")
        self.canvas.unbind_all("<Shift-Button-4>")
        self.canvas.unbind_all("<Shift-Button-5>")

    def update_size(self):
        val = self.size_var.get()
        if val == "custom":
            self.custom_mode = True
            self.clear_existing_rect()
        else:
            self.custom_mode = False
            self.crop_size = tuple(map(int, val.split("x")))
            self.clear_existing_rect()

    def load_folder(self):
        folder = filedialog.askdirectory()
        if not folder:
            return

        self.images = [os.path.abspath(os.path.join(folder, f)) for f in os.listdir(folder)
                      if f.lower().endswith(('png', 'jpg', 'jpeg', 'bmp'))]
        self.images.sort()
        if not self.images:
            return

        self.current_index = 0
        self.save_folder = os.path.join(folder, "cropped")
        os.makedirs(self.save_folder, exist_ok=True)
        self.current_folder = folder

        self.load_current_image()
        self.update_dimension_counts()
        self.jump_to_last_cropped()
        self.next_button.configure(state=ctk.NORMAL)
        self.prev_button.configure(state=ctk.NORMAL)

        # Make the right panel visible
        self.right_frame.pack(side=ctk.RIGHT, fill=ctk.Y)

    def load_current_image(self):
        if not self.images:
            self.canvas.delete("all")
            self.root.title("Power Cropper")
            self.current_image = None
            self.clear_existing_rect()
            self.dim_label.configure(text="")
            self.cropped_label.configure(text="")
            self.right_frame.pack_forget()
            return

        self.current_image = Image.open(self.images[self.current_index])
        self.tk_img = ImageTk.PhotoImage(self.current_image)
        self.canvas.delete("all")
        self.image_on_canvas = self.canvas.create_image(0, 0, anchor=ctk.NW, image=self.tk_img)
        # Set scroll region to image size
        w, h = self.current_image.size
        self.canvas.configure(scrollregion=(0, 0, w, h))
        index_text = f"({self.current_index + 1}/{len(self.images)})"
        self.dim_label.configure(text=f"Image size: {w} x {h} px  {index_text}")
        self.root.title(f"{os.path.basename(self.images[self.current_index])}")
        self.clear_existing_rect()
        self.update_radio_button_highlights(w, h)
        self.set_largest_radio_button(w, h)
        self.draw_previous_crops()
        self.update_cropped_label()

    def clear_existing_rect(self):
        if self.rect:
            self.canvas.delete(self.rect)
        self.rect = None
        self.rect_coords = None
        if self.custom_dim_text:
            self.canvas.delete(self.custom_dim_text)
            self.custom_dim_text = None
        self.canvas.delete("previous_crop")

    def on_mouse_down(self, event):
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        if self.custom_mode:
            self.clear_existing_rect()
            self.custom_start = (x, y)
            self.rect = self.canvas.create_rectangle(x, y, x, y, outline='red', width=2)
        else:
            self.place_rectangle(event)

    def on_mouse_drag(self, event):
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        if self.custom_mode:
            x0, y0 = self.custom_start
            x1, y1 = x, y
            self.canvas.coords(self.rect, x0, y0, x1, y1)
            # Calculate dimensions
            width = abs(x1 - x0)
            height = abs(y1 - y0)
            dim_text = f"{width} x {height}"
            # Show or move the dimension text near the mouse
            if self.custom_dim_text:
                self.canvas.coords(self.custom_dim_text, x + 15, y + 15)
                self.canvas.itemconfig(self.custom_dim_text, text=dim_text, fill="yellow")
            else:
                self.custom_dim_text = self.canvas.create_text(
                    x + 15, y + 15, text=dim_text,
                    fill="yellow", font=("Arial", 12, "bold"), anchor="nw"
                )

    def on_mouse_up(self, event):
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        if self.custom_mode and self.rect and self.custom_start:
            x0, y0 = self.custom_start
            x1, y1 = x, y
            # Ensure coordinates are within image bounds
            x0, x1 = max(0, min(x0, self.current_image.width)), max(0, min(x1, self.current_image.width))
            y0, y1 = max(0, min(y0, self.current_image.height)), max(0, min(y1, self.current_image.height))
            left, right = sorted([x0, x1])
            top, bottom = sorted([y0, y1])
            self.rect_coords = (left, top, right, bottom)
            self.save_custom_crop()
            self.custom_start = None
            # Remove the dimension text
            if self.custom_dim_text:
                self.canvas.delete(self.custom_dim_text)
                self.custom_dim_text = None
            self.next_image()

    def place_rectangle(self, event):
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        self.clear_existing_rect()
        x0 = x - self.crop_size[0]//2
        y0 = y - self.crop_size[1]//2
        x0 = max(0, min(x0, self.current_image.width - self.crop_size[0]))
        y0 = max(0, min(y0, self.current_image.height - self.crop_size[1]))
        x1 = x0 + self.crop_size[0]
        y1 = y0 + self.crop_size[1]
        self.rect = self.canvas.create_rectangle(
            x0, y0, x1, y1,
            outline='red', width=2)
        self.rect_coords = (x0, y0, x1, y1)

    def quick_save(self):
        if not self.rect_coords or not self.save_folder:
            return
        x0, y0, x1, y1 = map(int, self.rect_coords)
        crop = self.current_image.crop((x0, y0, x1, y1))
        image_path = self.images[self.current_index]
        base_name = os.path.splitext(os.path.basename(image_path))[0]
        crop_size_str = f"{x1-x0}x{y1-y0}"
        save_path = os.path.join(self.save_folder, f"{base_name}_cropped_{crop_size_str}.png")
        crop.save(save_path)
        entry = {"size": crop_size_str, "coords": (x0, y0, x1, y1), "image_path": image_path, "folder": self.current_folder}
        self.save_cropped_info(image_path, crop_size_str, (x0, y0, x1, y1))
        self.last_cropped_entry[self.current_folder] = entry  # Store by folder
        self.save_last_cropped_entries()
        self.update_dimension_counts()
        self.next_image()

    def save_custom_crop(self):
        if not self.rect_coords or not self.save_folder:
            return
        x0, y0, x1, y1 = map(int, self.rect_coords)
        if x1 - x0 < 2 or y1 - y0 < 2:
            return
        crop = self.current_image.crop((x0, y0, x1, y1))
        image_path = self.images[self.current_index]
        base_name = os.path.splitext(os.path.basename(image_path))[0]
        crop_size_str = f"{x1-x0}x{y1-y0}"
        save_path = os.path.join(self.save_folder, f"{base_name}_cropped_{crop_size_str}.png")
        crop.save(save_path)
        entry = {"size": crop_size_str, "coords": (x0, y0, x1, y1), "image_path": image_path, "folder": self.current_folder}
        self.save_cropped_info(image_path, crop_size_str, (x0, y0, x1, y1))
        self.last_cropped_entry[self.current_folder] = entry  # Store by folder
        self.save_last_cropped_entries()
        self.update_dimension_counts()
        self.next_image()

    def next_image(self):
        if not self.images:
            return
        self.current_index = (self.current_index + 1) % len(self.images)
        self.load_current_image()

    def prev_image(self):
        if not self.images:
            return
        self.current_index = (self.current_index - 1) % len(self.images)
        self.load_current_image()

    def delete_current_image(self):
        if not self.images:
            return

        image_path = self.images[self.current_index]
        self.remove_cropped_info(image_path)

        # Remove the physical file
        try:
            os.remove(image_path)
        except OSError as e:
            print(f"Error deleting {image_path}: {e}")

        # Remove from the list and adjust index
        del self.images[self.current_index]
        if not self.images:
            self.canvas.delete("all")
            self.images = []
            self.current_image = None
            self.clear_existing_rect()
            self.dim_label.config(text="")
            self.cropped_label.config(text="")
            self.right_frame.pack_forget()
            return

        self.current_index = min(self.current_index, len(self.images) - 1)
        self.load_current_image()

    def save_current_crop(self):
        if self.current_image and self.rect_coords:
            x0, y0, x1, y1 = map(int, self.rect_coords)
            crop_size_str = f"{x1-x0}x{y1-y0}"
            image_path = self.images[self.current_index]
            self.save_cropped_info(image_path, crop_size_str, (x0, y0, x1, y1))
            self.update_dimension_counts()

    def load_cropped_info(self):
        try:
            with open(self.cropped_info_file, 'r') as f:
                self.cropped_info = json.load(f)
        except FileNotFoundError:
            self.cropped_info = {"data": {}}
        except json.JSONDecodeError:
            self.cropped_info = {"data": {}}

    def save_cropped_info(self, image_path, size, coords):
        folder = self.current_folder

        if folder not in self.cropped_info["data"]:
            self.cropped_info["data"][folder] = {}

        if image_path not in self.cropped_info["data"][folder]:
            self.cropped_info["data"][folder][image_path] = []

        exists = any(crop["size"] == size and crop["coords"] == coords for crop in self.cropped_info["data"][folder][image_path])
        if not exists:
            self.cropped_info["data"][folder][image_path].append({"size": size, "coords": coords})
            self.save_cropped_info_to_file()

    def remove_cropped_info(self, image_path):
        folder = self.current_folder
        if folder in self.cropped_info["data"] and image_path in self.cropped_info["data"][folder]:
            del self.cropped_info["data"][folder][image_path]
            if not self.cropped_info["data"][folder]:
                del self.cropped_info["data"][folder]
            self.save_cropped_info_to_file()
            self.update_dimension_counts()

    def save_cropped_info_to_file(self):
        try:
            with open(self.cropped_info_file, 'w') as f:
                json.dump(self.cropped_info, f, indent=2)
        except Exception as e:
            print(f"Error saving cropped info: {e}")

    def update_dimension_counts(self):
        self.dimension_counts.clear()
        folder = self.current_folder
        if folder and folder in self.cropped_info["data"]:
            for image_path, crops in self.cropped_info["data"][folder].items():
                for crop in crops:
                    self.dimension_counts[crop["size"]] += 1
        self.update_counts_label()

    def update_counts_label(self):
        text = "Cropped Dimensions:\n\n"
        for dim, count in sorted(self.dimension_counts.items()):
            text += f"{dim}: {count}\n"
        self.counts_label.configure(text=text)

    def draw_previous_crops(self):
        if not self.current_image:
            return
        image_path = self.images[self.current_index]
        folder = self.current_folder

        if folder in self.cropped_info["data"] and image_path in self.cropped_info["data"][folder]:
            for crop in self.cropped_info["data"][folder][image_path]:
                x0, y0, x1, y1 = crop["coords"]
                self.canvas.create_rectangle(x0, y0, x1, y1, outline="yellow", width=2, tags="previous_crop")

    def update_cropped_label(self):
        if not self.images:
            return

        image_path = self.images[self.current_index]
        folder = self.current_folder

        if folder in self.cropped_info["data"] and image_path in self.cropped_info["data"][folder]:
            cropped_dims = [crop["size"] for crop in self.cropped_info["data"][folder][image_path]]
            self.cropped_label.configure(text="Cropped sizes: " + ", ".join(cropped_dims))
        else:
            self.cropped_label.configure(text="Not yet cropped")

    def jump_to_last_cropped(self):
        if not self.current_folder:
            return

        if self.current_folder not in self.last_cropped_entry:
            return

        last_cropped = self.last_cropped_entry[self.current_folder]

        image_path = last_cropped["image_path"]
        try:
            index = self.images.index(image_path)
            self.current_index = index
            self.load_current_image()
        except ValueError:
            print("Last cropped image not found in current folder.")

    def save_last_cropped_entries(self):
        try:
            with open("last_cropped.json", 'w') as f:
                json.dump(self.last_cropped_entry, f, indent=2)
        except Exception as e:
            print(f"Error saving last cropped entries: {e}")

    def load_last_cropped_entries(self):
        try:
            with open("last_cropped.json", 'r') as f:
                self.last_cropped_entry = json.load(f)
        except FileNotFoundError:
            self.last_cropped_entry = {}
        except json.JSONDecodeError:
            self.last_cropped_entry = {}

    def update_radio_button_highlights(self, width, height):
        for label, value in self.dimension_labels:
            rb = self.radio_buttons[value]
            if value == "custom":
                rb.configure(text_color="lime")
                continue
            w, h = map(int, value.split("x"))
            # Highlight green if fits in image
            if w <= width and h <= height:
                rb.configure(text_color="lime")
                rb.configure(state=ctk.NORMAL)
            else:
                rb.configure(state=ctk.DISABLED) # Disable the radiobutton

    def set_largest_radio_button(self, width, height):
        # Find all fitting resolutions
        fitting = []
        for label, value in self.dimension_labels:
            if value == "custom":
                continue
            w, h = map(int, value.split("x"))
            if w <= width and h <= height:
                fitting.append((w, h, value))

        if not fitting:
            self.size_var.set("custom")
            self.update_size()
            return

        # Prefer orientation
        prefer = self.orientation_preference.get()
        if prefer == "portrait":
            fitting.sort(key=lambda x: (x[0] <= x[1], x[0]*x[1]), reverse=True)
        else:
            fitting.sort(key=lambda x: (x[0] >= x[1], x[0]*x[1]), reverse=True)

        # Select the best fit
        best = fitting[0][2]
        self.size_var.set(best)
        self.update_size()

    def update_largest_radio_button(self):
        """Updates the selected radio button when orientation preference changes."""
        if self.current_image:
            w, h = self.current_image.size
            self.set_largest_radio_button(w,h)

if __name__ == "__main__":
    root = ctk.CTk()
    app = PowerCropper(root)
    root.geometry("1200x800")
    root.mainloop()
