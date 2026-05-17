from PIL import Image

def cleanup_logo(input_path, output_path, threshold=128):
    # Open the image and convert to RGBA
    img = Image.open(input_path).convert("RGBA")
    datas = img.getdata()

    new_data = []
    for item in datas:
        # item is (r, g, b, a)
        # Convert to grayscale value for thresholding
        # Using standard luminance formula: 0.299R + 0.587G + 0.114B
        grayscale = int(0.299 * item[0] + 0.587 * item[1] + 0.114 * item[2])
        
        if grayscale < threshold:
            # Make it pure black and opaque
            new_data.append((0, 0, 0, 255))
        else:
            # Make it white and transparent
            new_data.append((255, 255, 255, 0))

    img.putdata(new_data)
    img.save(output_path, "PNG")
    print(f"Cleaned logo saved to {output_path}")

if __name__ == "__main__":
    cleanup_logo("images/eagle-logo.png", "images/eagle-logo-cleaned.png")