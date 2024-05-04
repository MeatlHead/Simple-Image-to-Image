import tkinter as tk
from tkinter import ttk  # Import ttk for themed widgets
from PIL import Image, ImageTk
import torch
import os

# Set the environment variable to disable oneDNN custom operations
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

from diffusers import StableDiffusionXLImg2ImgPipeline
from diffusers.utils import load_image

def generate_image(url, prompt):
    # Load the model pipeline
    pipe = StableDiffusionXLImg2ImgPipeline.from_pretrained(
        "stabilityai/stable-diffusion-xl-refiner-1.0", torch_dtype=torch.float16, variant="fp16", use_safetensors=True
    )
    pipe.enable_model_cpu_offload()

    # Compile the UNet model for improved inference speed
    pipe.unet = torch.compile(pipe.unet, mode="reduce-overhead", fullgraph=True)

    # Load and convert the image
    init_image = load_image(url).convert("RGB")

    # Update progress bar
    progress_bar["value"] = 20
    root.update_idletasks()

    # Perform image translation
    image = pipe(prompt, image=init_image).images

    # Update progress bar
    progress_bar["value"] = 80
    root.update_idletasks()

    # Convert the generated image tensor to PIL image
    generated_image = torch.tensor(image[0]).cpu().detach().numpy().transpose(1, 2, 0)
    generated_image = (generated_image * 255).astype("uint8")

    # Update progress bar
    progress_bar["value"] = 100
    root.update_idletasks()

    return generated_image

def select_image():
    url = entry_image_url.get()
    prompt = entry_prompt.get()

    # Update progress bar
    progress_bar["value"] = 10
    root.update_idletasks()

    generated_image = generate_image(url, prompt)
    display_image(generated_image)

def display_image(image):
    # Display the generated image in the GUI
    image = Image.fromarray(image)
    image.thumbnail((300, 300))  # Resize image for display
    photo = ImageTk.PhotoImage(image)
    label_output_image.config(image=photo)
    label_output_image.image = photo

# Create GUI
root = tk.Tk()
root.title("Image Translation")

# Image URL Entry
label_image_url = tk.Label(root, text="Image URL:")
label_image_url.grid(row=0, column=0, padx=5, pady=5)
entry_image_url = tk.Entry(root, width=50)
entry_image_url.grid(row=0, column=1, padx=5, pady=5)

# Prompt Entry
label_prompt = tk.Label(root, text="Prompt:")
label_prompt.grid(row=1, column=0, padx=5, pady=5)
entry_prompt = tk.Entry(root, width=50)
entry_prompt.grid(row=1, column=1, padx=5, pady=5)

# Generate Button
button_generate = tk.Button(root, text="Generate", command=select_image)
button_generate.grid(row=2, column=0, columnspan=2, padx=5, pady=5)

# Progress Bar
progress_bar = ttk.Progressbar(root, orient="horizontal", length=200, mode="determinate")
progress_bar.grid(row=3, column=0, columnspan=2, padx=5, pady=5)

# Output Image Display
label_output_image = tk.Label(root)
label_output_image.grid(row=4, column=0, columnspan=2, padx=5, pady=5)

root.mainloop()
