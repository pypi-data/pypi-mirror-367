from textual.app import App, ComposeResult
from textual.screen import Screen
from textual.containers import Center, Horizontal, Vertical
from textual.widgets import Label, Button, Header, Footer, LoadingIndicator
from tkinter import filedialog
from PIL import Image
import pillow_avif
import tkinter as tk
from textual import work
import cv2
import numpy as np

file_path = None
img = None
model_path = None
scale = None
output_image_path = None
input_image_path = None

filetype_map = {
    "AVIF": [("AVIF files", "*.avif")],
    "PNG": [("PNG files", "*.png")],
    "WEBP": [("WEBP files", "*.webp")],
    "BMP": [("BMP files", "*.bmp")],
    "JPEG": [("JPEG files", "*.jpeg")],
    "JPG": [("JPG files", "*.jpg")]
}

class ToolSelector(Screen):
    CSS_PATH = "style.tcss"
    BINDINGS = [("escape", "app.pop_screen", "To Previous Page")]

    def on_mount(self) -> None:
        self.screen.styles.background = "red"

    def compose(self) -> ComposeResult:
            yield Header(show_clock=True)
            yield Footer()
            with Center():
                yield Button("Change Filetype", id="selectBt1")
            with Center():
                yield Button("Remove Background", id="selectBt2")
            with Center():
                yield Button("Scale Image", id="selectBt3")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "selectBt1":
            self.app.push_screen(FiletypeConverter())
        elif event.button.id == "selectBt2":
            self.app.push_screen(RemovingBackground())
        elif event.button.id == "selectBt3":
            self.app.push_screen(Upscaler())
        else:
            pass
    
class FiletypeConverter(Screen):
    CSS_PATH = "style.tcss"
    BINDINGS = [("escape", "app.pop_screen", "To Previous Page")]

    def on_mount(self) -> None:
        self.screen.styles.background = "red"

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Footer()

        with Vertical(id="main-container"):
            yield Label("Select the filetype you would like to convert to:", id="conversionTitle")
            with Horizontal(id="button-container"):
                if img.format == "PNG":
                    yield Button("PNG", id="PNG", disabled=True)
                else:
                    yield Button("PNG", id="PNG")

                if img.format == "JPG":
                    yield Button("JPG", id="JPG", disabled=True)
                else:
                    yield Button("JPG", id="JPG")

                if img.format == "JPEG":
                    yield Button("JPEG", id="JPEG", disabled=True)
                else:
                    yield Button("JPEG", id="JPEG")

                if img.format == "BMP":
                    yield Button("BMP", id="BMP", disabled=True)
                else:
                    yield Button("BMP", id="BMP")

                if img.format == "WEBP":
                    yield Button("WEBP", id="WEBP", disabled=True)
                else:
                    yield Button("WEBP", id="WEBP")

                if img.format == "AVIF":
                    yield Button("AVIF", id="AVIF", disabled=True)
                else:
                    yield Button("AVIF", id="AVIF")

    def on_button_pressed(self, event: Button.Pressed) -> None:

        format_map = {
        "AVIF": "AVIF",
        "PNG": "PNG",
        "WEBP": "WEBP",
        "BMP": "BMP",
        "JPEG": "JPEG",
        "JPG": "JPEG"
        }

        file_format = format_map.get(event.button.id, None)

        filetypes = filetype_map.get(event.button.id, [("All files", "*.*")])
        root = tk.Tk()
        root.attributes('-topmost', True)
        root.withdraw()
        save_path = filedialog.asksaveasfilename(parent=root, filetypes=filetypes, defaultextension=filetypes[0][1][1:])
        root.destroy()
        if save_path:
            if file_format:
                img.save(save_path, format=file_format)
                app.pop_screen()
            else:
                img.save(save_path)
        else:
            pass

class CompleteActionPage(Screen):
    CSS_PATH = "style.tcss"
    BINDINGS = [("escape", "app.pop_screen", "To Previous Page")]

    def on_mount(self) -> None:
        self.screen.styles.background = "red"

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Footer()
        with Center():
            yield Label("Your generation is complete and has been downloaded to your selected location!")
        with Center():
            yield Button("Go to home page", id="homeButton")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.app.switch_screen(ToolSelector())

class RemovingBackground(Screen):
    CSS_PATH = "style.tcss"

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Footer()
        with Center():
            yield Label("Removing Background", id="bgRemoveTitle")
        with Center():
            self.loader = LoadingIndicator()
            yield self.loader
        with Center():
            yield Label("Warning! JPEG/JPG and BMP files do not support transparent backgrounds, they will be white instead.", id="bgRemoveInstructions")

    def on_mount(self) -> None:
        self.screen.styles.background = "red"
        self.loader.display = True
        self.get_save_path()


    def get_save_path(self) -> None:
        global img, filetype_map
        
        current_format = getattr(img, 'format', 'PNG') if img else 'PNG'
        format_to_button_map = {"JPEG": "JPG"}
        button_id = format_to_button_map.get(current_format, current_format)
        
        root = tk.Tk()
        root.attributes('-topmost', True)
        root.withdraw()
        
        filetypes = filetype_map.get(button_id, [("PNG files", "*.png")])
        extension = filetypes[0][1][1:]
        
        bg_output_path = filedialog.asksaveasfilename(
            parent=root, 
            initialfile = "background-removed-image",
            filetypes=filetypes,
            defaultextension=extension
        )
        root.destroy()
        
        if bg_output_path:
            self.bg_output_path = bg_output_path
            format_map = {"JPG": "JPEG", "PNG": "PNG", "BMP": "BMP", "WEBP": "WEBP", "AVIF": "AVIF"}
            self.save_format = format_map.get(button_id, "PNG")
            self.do_background_removal()
        else:
            self.stop_loading()
            self.app.pop_screen()

    @work(thread=True)
    def do_background_removal(self) -> None:
        global img, file_path
        
        try:
            from rembg import remove
        except ImportError:
            self.app.call_from_thread(self.stop_loading)
            self.app.call_from_thread(self.app.pop_screen)
            return
        
        if hasattr(self, 'bg_output_path') and file_path:
            try:
                input_img = Image.open(file_path)
                output = remove(input_img)
                
                save_format = getattr(self, 'save_format', 'PNG')
            
                if save_format == 'JPEG' and output.mode == 'RGBA':
                    rgb_output = Image.new('RGB', output.size, (255, 255, 255))
                    rgb_output.paste(output, mask=output.split()[-1])
                    output = rgb_output
                
                output.save(self.bg_output_path, format=save_format)
                
            except Exception as e:
                pass
        
        self.app.call_from_thread(self.stop_loading)
        self.app.call_from_thread(self.app.push_screen, CompleteActionPage())

    def stop_loading(self) -> None:
        self.loader.display = False

class Upscaler(Screen):
    CSS_PATH = "style.tcss"
    BINDINGS = [("escape", "app.pop_screen", "To Previous Page")]

    def on_mount(self) -> None:
        self.screen.styles.background = "red"

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Footer()
        
        global input_image_path, file_path
        input_image_path = file_path
        
        try:
            image = cv2.imread(input_image_path)
            if image is None:
                raise ValueError(f"Could not load image from {input_image_path}")
            
            height, width = image.shape[:2]
            resolution_text = f"Current Resolution: {width}x{height}"
        except Exception as e:
            resolution_text = f"Error loading image: {str(e)}"
        
        with Vertical(id="main-container-scale"):
            with Center():
                yield Label(resolution_text, id="res")
            with Center():
                yield Label("Scale (Higher Scale = Higher Quality/More Time)")
            with Horizontal(id="button-container-scale"):
                yield Button("x2", id="x2")
                yield Button("x3", id="x3")
                yield Button("x4", id="x4")
            with Center():
                yield Label("This process may take up to 5 minutes", id="scaleDisclaimer")
            with Center():
                yield Label("You will be asked where to save the file on the next step")
            
    def on_button_pressed(self, event: Button.Pressed) -> None:
        global img, model_path, scale, button_id_scale
        
        if event.button.id == "x2":
            model_path = "./EDSR_x2.pb"
            scale = 2
        elif event.button.id == "x3":
            model_path = "./EDSR_x3.pb"
            scale = 3
        elif event.button.id == "x4":
            model_path = "./EDSR_x4.pb"
            scale = 4        
        
        current_format = getattr(img, 'format', 'PNG') if img else 'PNG'
        format_to_button_map = {"JPEG": "JPG"}
        button_id_scale = format_to_button_map.get(current_format, current_format)
        
        root = tk.Tk()
        root.attributes('-topmost', True)
        root.withdraw()
        
        filetypes = [("PNG files", "*.png"), ("JPEG files", "*.jpg"), ("All files", "*.*")]
        extension = ".png"
        
        global output_image_path
        output_image_path = filedialog.asksaveasfilename(
            parent=root, 
            initialfile="upscaled-image",
            filetypes=filetypes,
            defaultextension=extension
        )
        root.destroy()
        
        if output_image_path:
            self.app.switch_screen(UpscalerLoading())

class UpscalerLoading(Screen):
    CSS_PATH = "style.tcss"

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Footer()
        with Center():
            self.loader = LoadingIndicator()
            yield self.loader

    def on_mount(self) -> None:
        self.screen.styles.background = "red"
        self.loader.display = True
        self.upscaleImage()

    @work(thread=True)
    def upscaleImage(self) -> None:
        global model_path, scale, output_image_path, input_image_path
        
        try:
            if not input_image_path or not model_path or not output_image_path:
                raise ValueError("Missing required paths")
            
            image = cv2.imread(input_image_path)
            if image is None:
                raise ValueError(f"Could not load image from {input_image_path}")
            
            print(f"Original image shape: {image.shape}")
            print(f"Image dtype: {image.dtype}")
            
            if len(image.shape) != 3:
                raise ValueError(f"Expected 3D image (H,W,C), got {len(image.shape)}D")
            
            if image.dtype != np.uint8:
                image = image.astype(np.uint8)
            
            if image.shape[2] == 1:
                image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
            elif image.shape[2] == 4:
                image = cv2.cvtColor(image, cv2.COLOR_BGRA2BGR)
            
            print(f"Processed image shape: {image.shape}")
            
            sr = cv2.dnn_superres.DnnSuperResImpl_create()
            
            import os
            if not os.path.exists(model_path):
                raise FileNotFoundError(f"Model file not found: {model_path}")
            
            sr.readModel(model_path)
            sr.setModel("edsr", scale)
            
            print("Starting upscaling...")
            upscaled = sr.upsample(image)
            print(f"Upscaled image shape: {upscaled.shape}")
            
            success = cv2.imwrite(output_image_path, upscaled)
            if not success:
                raise ValueError(f"Failed to save image to {output_image_path}")
            
            print("Upscaling completed successfully!")
            
        except Exception as e:
            print(f"Error during upscaling: {str(e)}")
            self.app.call_from_thread(self.show_error, str(e))
            return
        
        self.app.call_from_thread(self.stop_loading)
        self.app.call_from_thread(self.app.push_screen, CompleteActionPage())

    def stop_loading(self) -> None:
        self.loader.display = False
    
    def show_error(self, error_message: str) -> None:
        print(f"Upscaling failed: {error_message}")
        self.stop_loading()

class ImageTerminalApp(App):

    CSS_PATH = "style.tcss"
    SCREENS = {"toolselect": ToolSelector}

    def on_mount(self) -> None:
        self.screen.styles.background = "red"

    def compose(self) -> ComposeResult:
                yield Header(show_clock=True)
                yield Footer()
                with Center():
                    yield Label("Image Terminal: An Image Manipulation Program", id="title")
                with Center():
                    yield Button("Upload Image!", id="upload_button")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "upload_button":
            filetypes = [("Image files", "*.png *.jpg *.jpeg *.bmp *.WEBP *.avif")]
            global file_path
            global img
            img = None
            root = tk.Tk()
            root.attributes('-topmost', True)
            root.withdraw()
            file_path = filedialog.askopenfilename(parent=root, filetypes=filetypes)
            root.destroy()
            if not file_path:
                pass
            else:
                img = Image.open(file_path)
                self.push_screen(ToolSelector())
        else:
            pass

if __name__ == "__main__":
    app = ImageTerminalApp()
    app.run()