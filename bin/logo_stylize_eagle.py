from PIL import Image, ImageFilter, ImageOps

def stylize_eagle(input_path, output_path):
    # Open the image and ensure it's RGBA
    img = Image.open(input_path).convert("RGBA")
    width, height = img.size
    
    # 1. Create a binary mask of the silhouette (Black pixels = 255, others = 0)
    mask = Image.new("L", (width, height), 0)
    pixels = img.load()
    mask_pixels = mask.load()
    
    for y in range(height):
        for x in range(width):
            if pixels[x, y] == (0, 0, 0, 255):
                mask_pixels[x, y] = 255

    # 2. Find the "Outside" using flood fill
    # We create a copy of the mask and flood fill from the corners
    outside_mask = Image.new("L", (width, height), 0)
    outside_pixels = outside_mask.load()
    
    # Simple flood fill from edges to find the exterior
    stack = []
    # Add all edge pixels that are not part of the silhouette to the stack
    for x in range(width):
        if mask_pixels[x, 0] == 0: stack.append((x, 0))
        if mask_pixels[x, height-1] == 0: stack.append((x, height-1))
    for y in range(height):
        if mask_pixels[0, y] == 0: stack.append((0, y))
        if mask_pixels[width-1, y] == 0: stack.append((width-1, y))
        
    while stack:
        x, y = stack.pop()
        if outside_pixels[x, y] == 0:
            outside_pixels[x, y] = 255
            for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < width and 0 <= ny < height:
                    if mask_pixels[nx, ny] == 0 and outside_pixels[nx, ny] == 0:
                        stack.append((nx, ny))

    # 3. Identify the "Face" (Holes)
    # Holes are pixels that are NOT silhouette AND NOT outside
    face_mask = Image.new("L", (width, height), 0)
    face_pixels = face_mask.load()
    for y in range(height):
        for x in range(width):
            if mask_pixels[x, y] == 0 and outside_pixels[x, y] == 0:
                face_pixels[x, y] = 255

    # 4. Find the Outline
    # We can find the outline by eroding the mask and subtracting it from the original
    # Or using a simple 3x3 check
    outline_mask = Image.new("L", (width, height), 0)
    outline_pixels = outline_mask.load()
    for y in range(1, height-1):
        for x in range(1, width-1):
            if mask_pixels[x, y] == 255:
                # If any neighbor is not part of the silhouette, it's an edge
                is_edge = False
                for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                    if mask_pixels[x+dx, y+dy] == 0:
                        is_edge = True
                        break
                if is_edge:
                    outline_pixels[x, y] = 255

    # 5. Compose the final image
    final_img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    final_pixels = final_img.load()
    
    for y in range(height):
        for x in range(width):
            if outline_pixels[x, y] == 255:
                final_pixels[x, y] = (0, 0, 0, 255) # Outline: Black
            elif face_pixels[x, y] == 255:
                final_pixels[x, y] = (0, 0, 0, 255) # Face: Black
            elif mask_pixels[x, y] == 255:
                final_pixels[x, y] = (255, 255, 255, 255) # Body: White
            else:
                final_pixels[x, y] = (0, 0, 0, 0) # Background: Transparent

    final_img.save(output_path, "PNG")
    print(f"Stylized logo saved to {output_path}")

if __name__ == "__main__":
    stylize_eagle("images/eagle-bw.png", "images/eagle-stylized.png")