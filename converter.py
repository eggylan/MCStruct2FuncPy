# -*- coding:utf-8 -*-
from TrimMCStruct import Structure
import os

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
    # 三重循环，遍历所有方块
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

                cmds.append(f"setblock ~{x} ~{y} ~{z} {blockname}")
                print(f"Converted block at {x}, {y}, {z} to setblock command.")

    print("Conversion complete.")
    return "\n".join(cmds)

if __name__ == "__main__":
    path = input("Please enter the path to the .mcstruction file: ")
    default_output = f"{os.path.splitext(os.path.basename(path))[0]}_output.mcfunction"
    output_path = input(f"Please enter the path to the output file, or press enter to use the default path ({default_output}): ") or default_output
    
    print("Starting conversion...")
    cmds = convert(path, output_path)
    with open(output_path, "w") as f:
        f.write(cmds)
    print(f"File has been written to {output_path}")