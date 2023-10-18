
from PIL import Image
import sys, os
import numpy as np
import imageio
from scipy import ndimage
import json
from enum import Enum
from typing import Dict

class Attribute(Enum):
    body = 1
    bottomwear = 2
    eyes = 3
    hair = 4
    shoes = 5
    topwear = 6
    action = 7,
    resample = 8

attributes = {
    Attribute.body: {
        "0": "a man with skin of reddish-orange color",
        "1": "a man with skin of yellowish-orange color",
        "2": "a man with skin of teal-blue color",
        "3": "a man with pale white skin",
        "4": "a man with skin of dark-orange color",
        "5": "a man with brown skin",
        "6": "an orc with green skin"
    },
    Attribute.bottomwear: {
        "0": "white shorts",
        "1": "leather pants",
        "2": "red shorts",
        "3": "white pants",
        "4": "light green shorts",
        "5": "dark green pants",
        "6": "leather sash",
        "no": "without pants"
    },
    Attribute.eyes: {
        "0": "blue eyes",
        "1": "brown eyes",
        "2": "red eyes",
        "3": "green eyes",
        "4": "yellow eyes",
        "no": "black eyes",
    },
    Attribute.hair : {
        "0": "short green hair",
        "1": "purple man bun hair",
        "2": "short yellow hair",
        "3": "short gray hair",
        "4": "short pinkish-red hair",
        "5": "curly pinkish-purple hair",
        "6": "half-shaven gray hair",
        "7": "short red hair",
        "8": "short pink hair",
        "9": "curly orange hair",
        "no": "no hair"
    },
    Attribute.shoes: {
        "0": "brown shoes",
        "1": "yellow shoes",
        "2": "white shoes",
        "no": "barefoot"
    },
    Attribute.topwear: {
        "0": "red shirt", 
        "1": "blue shirt", 
        "2": "white shirt",
        "3": "gray armor",
        "4": "leather armor",
        "5": "white formal shirt with tie",
        "6": "gray chainmail",
        "no": "shirtless"
    }
}

actions = {
    'casting a spell': {
        'back view': list(range(0, 7)),
        'left-side view': list(range(13, 20)),
        'front view': list(range(26, 33)),
        'right-sided view': list(range(39, 46))
    },
    'dancing': {
        'back view': list(range(52, 60)),
        'left-side view': list(range(65, 73)),
        'front view': list(range(78, 86)),
        'right-sided view': list(range(91, 99))
    },
    'walking': {
        'back view': list(range(104, 113)),
        'left-side view': list(range(117, 126)),
        'front view': list(range(130, 139)),
        'right-sided view': list(range(143, 152))
    },
    'slashing': {
        'back view': list(range(156, 162)),
        'left-side view': list(range(169, 175)),
        'front view': list(range(182, 188)),
        'right-sided view': list(range(195, 201))
    },
    'waving his arms': {
        'back view': list(range(208, 221)),
        'left-side view': list(range(221, 234)),
        'front view': list(range(234, 247)),
        'right-sided view': list(range(247, 260))
    },
    'falling': {'front view': list(range(260, 266))}
}

colors = ["white", "yellow", "silver", "gray", "green", "azure"]
# create dictionary of all attribute variants; structure: atrr_img = {'body': {'0': Img, ...}, ...}
attr_img:Dict[Attribute, Dict[str, Image.Image]] = {} 
for attr_name, attr_values in attributes.items():
    attr_img[attr_name] = {}
    for name in attr_values:
        if (name == "no"): 
            attr_img[attr_name][name] = Image.NONE;
            continue
        img_path = os.path.join(attr_name.name, f"{name}.png")
        attr_img[attr_name][name] = Image.open(img_path)

def get_random_char() -> Dict[Attribute, Dict[str, object]]:
    character = {}
    for k, v in attributes.items():
        rnd_key = np.random.choice(list(v.keys()))
        character[k] = {rnd_key: v[rnd_key]}
    
    rnd_action_key = np.random.choice(list(actions.keys()))
    rnd_action_val = actions[rnd_action_key]
    
    rnd_side_key = np.random.choice(list(rnd_action_val.keys()))
    rnd_side_val = rnd_action_val[rnd_side_key]
    
    character[Attribute.action] = {rnd_action_key: {rnd_side_key: rnd_side_val}}
    return character

random_characters = [get_random_char() for i in range(1024)]

data_dir = "data"
images_dir = "images"
metadata_path = os.path.join(data_dir, "metadata.jsonl");
data_images_dir = os.path.join(data_dir, "images")
jsoncontent = []
if not os.path.exists(data_images_dir):
    os.makedirs(data_images_dir)

def img_name(dict)-> str:
    return next(iter(dict.items()))[0]

def description(dict)-> str:
    return next(iter(dict.items()))[1]

jsoncontent = []
for i_char, character in enumerate(random_characters):
    # get current cached images ()
    body_img = attr_img[Attribute.body][img_name(character[Attribute.body])]
    bottomwear_img = attr_img[Attribute.bottomwear][img_name(character[Attribute.bottomwear])] 
    eyes_img = attr_img[Attribute.eyes][img_name(character[Attribute.eyes])]
    hair_img = attr_img[Attribute.hair][img_name(character[Attribute.hair])] 
    shoes_img = attr_img[Attribute.shoes][img_name(character[Attribute.shoes])]
    topwear_img = attr_img[Attribute.topwear][img_name(character[Attribute.topwear])] 
    imgs = [body_img, bottomwear_img, hair_img, eyes_img, shoes_img, topwear_img]    
    
    body_desc = description(character[Attribute.body])
    bottomwear_desc = description(character[Attribute.bottomwear])
    eyes_desc = description(character[Attribute.eyes])
    hair_desc = description(character[Attribute.hair])
    shoes_desc = description(character[Attribute.shoes])
    topwear_desc = description(character[Attribute.topwear])
    action_desc, frames_dict = next(iter(character[Attribute.action].items())) 
    side_desc, frames = next(iter(frames_dict.items()))
    
    isOrc = img_name(character[Attribute.body]) == "6"
    if (isOrc):
        imgs.remove(eyes_img)
        imgs.remove(hair_img)
        imgs.remove(topwear_img)
        eyes_desc = "black eyes"
        hair_desc = "no hair"
        topwear_desc = "without shirt"
        
    bg_color = np.random.choice(colors)
    resize = int(1024 / len(frames))
    resize_desc = f"each frame has size of {resize}x{resize} pixels"
    frame_size = 64
    max_frames_per_row = 13
    frame_row = int(frames[0] / max_frames_per_row)
    # sequence_img = Image.new("RGBA", (frame_size * len(frames), frame_size), "white")
    sequence_img = Image.new("RGBA", (1024, 1024), bg_color)
    
    for i, frame_i in enumerate(frames):
        box = (i * frame_size, frame_row * frame_size, (i + 1) * frame_size, (frame_row + 1) * frame_size)
        frame = Image.new("RGBA", (frame_size, frame_size), bg_color)
        # stack each attribute into main frame 
        for img in imgs:
            if (img is Image.NONE):
                continue
            attr_frame = img.crop(box).convert("RGBA")
            frame.alpha_composite(attr_frame)
        
        sequence_img.alpha_composite(frame.resize((resize, resize)), (i * resize, 512 - int(resize / 2)))
    
    filename = f"{images_dir}/{i_char}.png"
    jsoncontent.append({"file_name": filename,
                        "text": f"Sprite animation showing {body_desc} that is {action_desc}, composed of {len(frames)} slightly different frames, {resize_desc}, {side_desc}, character has {hair_desc}, {bottomwear_desc}, {eyes_desc}, {shoes_desc}, {topwear_desc}, sprite sequence is centered, with the solid {bg_color} background, pixel art style, game asset."})
    sequence_img.save(os.path.join(data_dir, images_dir, f"{i_char}.png"))

with open(metadata_path, "w") as jsonfile:
    for item in jsoncontent:
        json.dump(item, jsonfile)
        jsonfile.write('\n')
