# -*- coding:utf-8 -*-
from TrimMCStruct import Structure
import os

# 本项目中受CC BY-SA 4.0协议保护的部分由此开始

def group_blocks(sorted_tiles, size):
    
    shapes = []
    tiles = sorted_tiles.copy()
    while tiles:
        # 获取第一个方块
        model_entry = tiles.pop(0)
        startX, startY, startZ = model_entry["x"], model_entry["y"], model_entry["z"]
        maxX, maxY, maxZ = startX, startY, startZ
        blockname = model_entry["blockname"]
        
        # Z轴方向
        z = startZ + 1
        while z < size[2]:
            if any(tile["x"] == startX and tile["y"] == startY and tile["z"] == z and tile["blockname"] == blockname for tile in tiles):
                maxZ = z
                z += 1
            else:
                break
        # Y轴方向
        y = startY + 1
        while y < size[1]:
            valid = True
            for zi in range(startZ, maxZ+1):
                if not any(tile["x"] == startX and tile["y"] == y and tile["z"] == zi and tile["blockname"] == blockname for tile in tiles):
                    valid = False
                    break
            if valid:
                maxY = y
                y += 1
            else:
                break
        # X轴方向
        x = startX + 1
        while x < size[0]:
            valid = True
            for yi in range(startY, maxY+1):
                for zi in range(startZ, maxZ+1):
                    if not any(tile["x"] == x and tile["y"] == yi and tile["z"] == zi and tile["blockname"] == blockname for tile in tiles):
                        valid = False
                        break
                if not valid:
                    break
            if valid:
                maxX = x
                x += 1
            else:
                break

        # 从tiles中移除已经处理的方块
        to_remove = []
        for i, tile in enumerate(tiles):
            if (
                startX <= tile["x"] <= maxX and 
                startY <= tile["y"] <= maxY and
                startZ <= tile["z"] <= maxZ and
                tile["blockname"] == blockname
            ):
                to_remove.append(i)
        for index in sorted(to_remove, reverse=True):
            tiles.pop(index)
        shapes.append({"blockname": blockname, "low": [startX, startY, startZ], "high": [maxX, maxY, maxZ]})
    return shapes

# 本项目中受CC BY-SA 4.0协议保护的部分由此结束

def convert(path, output_path=""):
    filename = os.path.splitext(os.path.basename(path))[0]
    if not output_path:
        output_path = f"{filename}_output.mcfunction"
        
    with open(path, "rb") as f:
        struct = Structure.load(f)

    xsize, ysize, zsize = struct.size

    if os.path.exists(output_path):
        os.remove(output_path)

    cmds = []
    sorted_tiles = []
    # 收集所有非空气方块
    for x in range(xsize):
        for y in range(ysize):
            for z in range(zsize):
                block = struct.get_block((x, y, z))
                if block.identifier == "minecraft:air":
                    continue
                blockname = block.stringify(
                    with_namespace=False,
                    with_states=True
                ).replace(": ", "=").replace(" []", "") \
                    .replace("=1", "=true").replace("=0", "=false") \
                    .replace('direction"=true', 'direction"=1') \
                    .replace('direction"=false', 'direction"=0') \
                    .replace('redstone_signal"=false', 'redstone_signal"=0') \
                    .replace('redstone_signal"=true', 'redstone_signal"=1') \
                    .replace('block_light_level"=true', 'block_light_level"=1') \
                    .replace('block_light_level"=false', 'block_light_level"=0') \
                    .replace('liquid_depth"=true', 'liquid_depth"=1') \
                    .replace('liquid_depth"=false', 'liquid_depth"=0') \
                    # 替换数据值

                sorted_tiles.append({"x": x, "y": y, "z": z, "blockname": blockname})

    # 使用group_blocks进行三维优化
    shapes = group_blocks(sorted_tiles, [xsize, ysize, zsize])

    # 生成指令
    for shape in shapes:
        blockname = shape["blockname"]
        low = shape["low"]
        high = shape["high"]
        if low == high:
            x, y, z = low
            cmds.append(f"setblock ~{x} ~{y} ~{z} {blockname}")
        else:
            x1, y1, z1 = low
            x2, y2, z2 = high
            cmds.append(f"fill ~{x1} ~{y1} ~{z1} ~{x2} ~{y2} ~{z2} {blockname}")

    print("Conversion complete.")
    return "\n".join(cmds)

if __name__ == "__main__":
    path = input("Please enter the path of the .mcstructure file: ")
    default_output = f"{os.path.splitext(os.path.basename(path))[0]}_output.mcfunction"
    output_path = input(f"Please enter the path of the output file, or press Enter to use the default path ({default_output}): ") or default_output
    print("Converting, please wait...")
    cmds = convert(path, output_path)
    with open(output_path, "w") as f:
        f.write(cmds)
    print(f"File has been written to {output_path}")