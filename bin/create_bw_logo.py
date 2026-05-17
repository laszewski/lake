from PIL import Image

def create_bw_logo(input_path, output_path):
    # Open the image and convert to RGBA
    img = Image.open(input_path).convert("RGBA")
    datas = img.getdata()

    new_data = []
    for item in datas:
        # item is (r, g, b, a)
        # User wants to include (0, 0, 0, 255) and the rest set to (0, 0, 0, 0)
        if item == (0, 0, 0, 255):
            new_data.append((0, 0, 0, 255))
        else:
            new_data.append((0, 0, 0, 0))

    img.putdata(new_data)
    img.save(output_path, "PNG")
    print(f"B&W logo saved to {output_path}")

if __name__ == "__main__":
    create_bw_logo("images/eagle-logo.png", "images/eagle-bw.png")