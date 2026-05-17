from PIL import Image

def list_colors(image_path):
    img = Image.open(image_path).convert("RGBA")
    colors = set(img.getdata())
    
    print(f"Unique colors in {image_path}:")
    for color in sorted(list(colors)):
        print(color)
    print(f"Total unique colors: {len(colors)}")

if __name__ == "__main__":
    list_colors("images/eagle-logo.png")