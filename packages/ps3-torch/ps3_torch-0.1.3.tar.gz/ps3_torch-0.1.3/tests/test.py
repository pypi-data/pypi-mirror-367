from ps3.modeling_ps3 import PS3VisionModel, PS3TextModel, PS3Model
from ps3.image_processing_ps3 import PS3ImageProcessor
from ps3.tokenization_ps3 import PS3Tokenizer
from transformers import AutoTokenizer
from safetensors.torch import load_file
import torch
from open_clip import create_model_from_pretrained, get_tokenizer
from PIL import Image

# # Load HF model
# vision_model = PS3VisionModel.from_pretrained("/home/baifengs/baifengs/projects/open_clip/hf_ckpt/250123_1112_retrain").cuda()
# text_model = PS3TextModel.from_pretrained("/home/baifengs/baifengs/projects/open_clip/hf_ckpt/250123_1112_retrain").cuda()
# processor = PS3ImageProcessor.from_pretrained("/home/baifengs/baifengs/projects/open_clip/hf_ckpt/250123_1112_retrain")
# tokenizer = PS3Tokenizer.from_pretrained("/home/baifengs/baifengs/projects/open_clip/hf_ckpt/250123_1112_retrain")
# vision_model.vision_model.num_hidden_layers_to_return = 2

# Load HF model
vision_model = PS3VisionModel.from_pretrained("nvidia/PS3-1.5K-SigLIP2").cuda()
text_model = PS3TextModel.from_pretrained("nvidia/PS3-1.5K-SigLIP2").cuda()
processor = PS3ImageProcessor.from_pretrained("nvidia/PS3-1.5K-SigLIP2")
tokenizer = PS3Tokenizer.from_pretrained("nvidia/PS3-1.5K-SigLIP2")
vision_model.vision_model.num_hidden_layers_to_return = 2

# Load OpenCLIP model
openclip_model, openclip_processor = create_model_from_pretrained("PS3-1.5K-SigLIP2", 
                                                                  "/home/baifengs/baifengs/projects/open_clip/output/250325_1632/checkpoints/epoch_latest.pt", load_weights_only=False)
openclip_model = openclip_model.cuda()
openclip_tokenizer = get_tokenizer("PS3-1.5K-SigLIP2")
openclip_vision_model = openclip_model.visual
openclip_text_model = openclip_model.text
openclip_vision_model.num_hidden_layers_to_return = 2

# Load image
image = Image.open("/home/baifengs/baifengs/projects/open_clip/tests/images/cat_and_dog.png")

# Test if output aligns for bottom-up selection
openclip_x = openclip_processor(image).unsqueeze(0).cuda()
openclip_out = openclip_vision_model(openclip_x, num_look_close=2, output_hidden_states=True).hidden_states
x = processor(image)["pixel_values"][0].unsqueeze(0).cuda()
out = vision_model(x, num_look_close=2).hidden_states
for a, b in zip(out, openclip_out):
    print(torch.allclose(a, b))
    if not torch.allclose(a, b):
        print(a)
        print(b)

# Test if output aligns for top-down selection
openclip_text = ["a photo of a cat"]
openclip_text = openclip_tokenizer(openclip_text).cuda()
openclip_prompt = openclip_model.prompt_proj(openclip_model.encode_text(openclip_text, normalize=True))
openclip_x = openclip_processor(image).unsqueeze(0).cuda()
openclip_outs = openclip_vision_model(openclip_x, num_look_close=2, prompt=openclip_prompt, output_hidden_states=True)
openclip_out = openclip_outs.hidden_states
openclip_selection_maps = openclip_outs.selection_maps
openclip_selection_probs = openclip_outs.selection_probs

text = ["a photo of a cat"]
text = tokenizer(text).cuda()
prompt = text_model(text).prompt
x = processor(image)["pixel_values"][0].unsqueeze(0).cuda()
outs = vision_model(x, num_look_close=2, prompt=prompt)
out = outs.hidden_states
selection_maps = outs.selection_maps
selection_probs = outs.selection_probs


print(openclip_text)
print(text)
print(openclip_model.encode_text(openclip_text))
print(text_model(text).pooled_output)
print(openclip_prompt)
print(prompt)
print(len(out))
print(len(openclip_out))

for a, b in zip(out, openclip_out):
    print(torch.allclose(a, b))
    if not torch.allclose(a, b):
        print(a)
        print(b)

for a, b in zip(selection_probs, openclip_selection_probs):
    print(torch.allclose(a, b))
    if not torch.allclose(a, b):
        print(a)
        print(b)
        print((a - b).norm() / b.norm())
        print((a - b).abs().max())

for a, b in zip(selection_maps, openclip_selection_maps):
    print(torch.allclose(a, b))
    if not torch.allclose(a, b):
        print(a)
        print(b)
        print((a - b).norm() / b.norm())


# vision_model.save_pretrained("./tmp")
# text_model.save_pretrained("./tmp")
# processor.save_pretrained("./tmp")
# tokenizer.save_pretrained("./tmp")
