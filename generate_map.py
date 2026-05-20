import json
import os

def main():
    # Map dimensions
    width = 100
    height = 100
    
    # Initialize all tiles as wall tile (ID 2)
    grid = [[2 for _ in range(width)] for _ in range(height)]
    
    # Carve helper functions (empty space is ID 0)
    def carve(x1, x2, y1, y2):
        for y in range(y1, y2 + 1):
            for x in range(x1, x2 + 1):
                if 0 <= x < width and 0 <= y < height:
                    grid[y][x] = 0

    def build_wall(x1, x2, y1, y2):
        for y in range(y1, y2 + 1):
            for x in range(x1, x2 + 1):
                if 0 <= x < width and 0 <= y < height:
                    grid[y][x] = 2

    # --- CARVE LEFT SIDE (cols 0-45) ---
    
    # 1. Carve the main columns (Left Shaft, Right Shaft, Middle Ledges)
    # Left Shaft: cols 2-19, rows 26-97
    carve(2, 19, 26, 97)
    # Right Shaft: cols 27-44, rows 18-97
    carve(27, 44, 18, 97)
    # Middle Ledges (to connect them at specific floors)
    # Ledge 1 (Floor 98): carve rows 94-97
    carve(20, 26, 94, 97)
    # Ledge 2 (Floor 86): carve rows 82-85
    carve(20, 26, 82, 85)
    # Ledge 3 (Floor 74): carve rows 70-73
    carve(20, 26, 70, 73)
    # Ledge 4 (Floor 62): carve rows 58-61
    carve(20, 26, 58, 61)
    # Ledge 5 (Floor 50): carve rows 46-49
    carve(20, 26, 46, 49)
    # Ledge 6 (Floor 38): carve rows 34-37
    carve(20, 26, 34, 37)
    # Ledge 7 (Floor 26): carve rows 22-25
    carve(20, 26, 22, 25)

    # 2. Build the climbing platforms in the shafts
    # Right Shaft Climbs (1, 3, 5, 7)
    # Climb 1:
    build_wall(38, 42, 94, 95)
    build_wall(29, 33, 90, 91)
    # Climb 3:
    build_wall(38, 42, 70, 71)
    build_wall(29, 33, 66, 67)
    # Climb 5:
    build_wall(38, 42, 46, 47)
    build_wall(29, 33, 42, 43)
    # Climb 7:
    build_wall(38, 42, 22, 23)

    # Left Shaft Climbs (2, 4, 6)
    # Climb 2:
    build_wall(4, 8, 82, 83)
    build_wall(13, 17, 78, 79)
    # Climb 4:
    build_wall(4, 8, 58, 59)
    build_wall(13, 17, 54, 55)
    # Climb 6:
    build_wall(4, 8, 34, 35)
    build_wall(13, 17, 30, 31)

    # 3. Add solid floors to separate the vertical shafts
    # Right Shaft Floors: Floor 74, Floor 50, Floor 26.
    build_wall(27, 44, 74, 75)
    build_wall(27, 44, 50, 51)
    build_wall(27, 44, 26, 27)
    
    # Left Shaft Floors: Floor 86, Floor 62, Floor 38.
    build_wall(2, 19, 86, 87)
    build_wall(2, 19, 62, 63)
    build_wall(2, 19, 38, 39)

    # --- CARVE PVP ARENA (cols 10-89, rows 4-17) ---
    carve(10, 89, 4, 17) # Floor of arena is 18.
    
    # Arena Floating Platforms (Low, High)
    # Low platforms (row 14-15)
    build_wall(20, 30, 14, 15)
    build_wall(40, 59, 14, 15)
    build_wall(69, 79, 14, 15)
    # High platforms (row 10-11)
    build_wall(30, 45, 10, 11)
    build_wall(54, 69, 10, 11)

    # --- MIRROR LEFT SIDE TO RIGHT SIDE ---
    # Copy from left (0 to 45) to right (54 to 99)
    for y in range(height):
        for x in range(46):
            grid[y][99 - x] = grid[y][x]

    # Leave columns 46 to 53 as solid wall divider from row 23 to 98
    build_wall(46, 53, 23, 98)

    # Flatten the 2D grid into a 1D list
    flat_data = []
    for row in grid:
        flat_data.extend(row)

    # --- CREATE OBJECTS ---
    objects = []
    obj_id = 1

    def add_object(obj_type, name, tile_x, tile_y, properties=None):
        nonlocal obj_id
        # Convert tile coordinates to pixel coordinates (top-left corner for Tiled objects)
        x_pixel = tile_x * 32
        y_pixel = tile_y * 32
        obj = {
            "height": 32,
            "id": obj_id,
            "name": name,
            "rotation": 0,
            "type": obj_type,
            "visible": True,
            "width": 32,
            "x": x_pixel,
            "y": y_pixel
        }
        if properties:
            obj["properties"] = [
                {"name": k, "type": "int", "value": v} for k, v in properties.items()
            ]
        objects.append(obj)
        obj_id += 1

    # Spawn players
    # Dino starts on left starting room
    add_object("Dino", "dino", 6, 96)
    # Alien starts on right starting room (mirror of col 6 is 93)
    add_object("Alien", "alien", 93, 96)

    # Define left-side mob list (col, row, name, properties)
    left_mobs = [
        # Ledge 2 (Scout)
        (23, 85, "grunt", {"health": 40, "speed": 6, "damage": 5, "aggro_range": 350}),
        # Ledge 3 (Grunt)
        (23, 73, "grunt", {"health": 60, "speed": 3, "damage": 8, "aggro_range": 250}),
        # Ledge 4 (Guardian)
        (23, 61, "grunt", {"health": 120, "speed": 2, "damage": 12, "aggro_range": 200}),
        # Ledge 5 (Brute)
        (23, 49, "grunt", {"health": 80, "speed": 4, "damage": 18, "aggro_range": 300}),
        # Ledge 6 (Grunt & Scout)
        (21, 37, "grunt", {"health": 60, "speed": 3, "damage": 8, "aggro_range": 250}),
        (25, 37, "grunt", {"health": 40, "speed": 6, "damage": 5, "aggro_range": 350}),
        # Ledge 7 (Boss & Guardian)
        (22, 25, "grunt", {"health": 200, "speed": 3, "damage": 25, "aggro_range": 500}),
        (26, 25, "grunt", {"health": 120, "speed": 2, "damage": 12, "aggro_range": 200})
    ]

    # Add left mobs and mirror them to the right
    for col, row, name, props in left_mobs:
        # Left Mob
        add_object("Mob", name, col, row, props)
        # Right Mob (Mirrored)
        add_object("Mob", name, 99 - col, row, props)

    # Define left-side coin list (col, row)
    left_coins = [
        # starting room
        (12, 96), (16, 96),
        # Ledge 2
        (22, 84), (25, 84),
        # Ledge 3
        (22, 72), (25, 72),
        # Ledge 4
        (22, 60), (25, 60),
        # Ledge 5
        (22, 48), (25, 48),
        # Ledge 6
        (23, 36),
        # Ledge 7
        (21, 24), (24, 24),
        # Arena (left half, which will be mirrored to right half)
        (25, 17), (40, 17),
        (20, 13), (40, 13),
        (37, 9)
    ]

    # Add left coins and mirror them to the right
    for col, row in left_coins:
        # Left Coin
        add_object("Coin", "coin", col, row)
        # Right Coin (Mirrored)
        add_object("Coin", "coin", 99 - col, row)

    # Build the full map structure
    map_json = {
        "compressionlevel": -1,
        "height": height,
        "width": width,
        "infinite": False,
        "orientation": "orthogonal",
        "renderorder": "right-down",
        "tileheight": 32,
        "tilewidth": 32,
        "type": "map",
        "version": "1.10",
        "tiledversion": "1.11.2",
        "nextlayerid": 3,
        "nextobjectid": obj_id,
        "tilesets": [{"firstgid": 1, "source": "tileset.tsx"}],
        "layers": [
            {
                "data": flat_data,
                "height": height,
                "width": width,
                "id": 1,
                "name": "Tile Layer 1",
                "opacity": 1,
                "type": "tilelayer",
                "visible": True,
                "x": 0,
                "y": 0
            },
            {
                "draworder": "topdown",
                "id": 2,
                "name": "Object Layer 1",
                "objects": objects,
                "opacity": 1,
                "type": "objectgroup",
                "visible": True,
                "x": 0,
                "y": 0
            }
        ]
    }

    # Save to maps/main_map.json
    output_dir = os.path.join(os.path.dirname(__file__), "maps")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "main_map.json")
    
    with open(output_path, "w") as f:
        json.dump(map_json, f)
        
    print(f"Successfully generated new map at {output_path}")

if __name__ == "__main__":
    main()
