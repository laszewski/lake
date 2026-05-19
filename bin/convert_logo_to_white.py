from PIL import Image, ImageOps
import sys
import os

def invert_image(input_path, output_path):
    try:
        with Image.open(input_path) as img:
            # Convert to RGBA to preserve transparency
            img = img.convert("RGBA")
            
            # Split into channels
            r, g, b, a = img.split()
            
            # Invert RGB channels
            # For a simple black to white conversion of a logo, 
            # we can invert the RGB values.
            rgb = Image.merge("RGB", (r, g, b))
            inverted_rgb = ImageOps.invert(rgb)
            
            # Merge back with original alpha channel
            final_img = Image.merge("RGBA", (*inverted_rgb.split(), a))
            
            final_img.save(output_path)
            print(f"Successfully converted {input_path} to {output_path}")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    input_file = "docs/images/eagle-logo.png"
    output_file = "docs/images/eagle-logo-white.png"
    invert_image(input_file, output_file)