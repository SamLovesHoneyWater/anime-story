from diffusers import DiffusionPipeline, EulerAncestralDiscreteScheduler, DPMSolverMultistepScheduler
import os
import torch

pipe = DiffusionPipeline.from_pretrained(
    "Meina/MeinaMix_V11",
    torch_dtype=torch.float16,
    safety_checker=None
)
pipe.scheduler = EulerAncestralDiscreteScheduler.from_config(pipe.scheduler.config)
pipe.to("cuda")

def simple_diffuse(prompt):
    """Generate an image using the diffusion pipeline with the given prompt."""
    negative_prompt = "(worst quality, low quality:1.4), (duplicate:1.6), (twin:1.6), (clone:1.6), (ugly:1.4), (disfigured:1.4), (distorted:1.4), (bad anatomy:1.4), (bad hands:1.4), (extra fingers:1.4), (bad fingers:1.4), (fused fingers:1.4), (distorted background), (extra characters:1.4), (strange hair:1.4), (zombie, sketch, interlocked fingers, comic)"
    
    image = pipe(
        prompt,
        negative_prompt=negative_prompt,
        width=1024,
        height=768,
        num_inference_steps=45,
        guidance_scale=7,
        generator=torch.manual_seed(42)
    ).images[0]
    return image

def generate_diffuse_shot(shot_description, character_feature, index):
    gender = character_feature["gender"]
    character_description = character_feature["description"]
    # Force single character
    if "M" in gender:
        prompt = "(1boy:1.2), (solo:1.2), "
    elif "F" in gender:
        prompt = "(1girl:1.2), (solo:1.2), "
    else:
        raise ValueError(f"Invalid gender: {gender}, expected 'M' or 'F'")
    prompt += f"(masterpiece), {character_description}, {shot_description}"
    print(f"[INFO] Shot {index} prompt: {prompt}")
    image = simple_diffuse(prompt)
    # Create output directory if it doesn't exist
    os.makedirs("images", exist_ok=True)

    # Save image
    filename = f"images/scene_{index:04d}.png"
    image.save(filename)
    return filename

if __name__ == "__main__":
    prompt = "(1girl), (masterpiece), (beautiful), (long hair:1.2), (white hair), (spread hair), (shiny red eyes), realistic anime visual novel, scene: standing gracefully beside the sofa in the living room, setting: late morning, soft sunlight, attire: elegant and simple white nightgown, attire draping softly and emitting an ethereal air, action: standing still, face serene and beautiful, delicate hands loosely clasped, looking calmly toward me, camera: medium shot facing directly, background: sunlit curtains and hints of indoor plants, a tranquil yet poignant atmosphere"
    prompt = "(1girl), (masterpiece), (beautiful), (long hair:1.2), (white hair), (spread hair), (shiny red eyes), scene: standing gracefully beside the sofa in the living room, setting: late morning, soft sunlight, attire: elegant and simple white nightgown, attire draping softly and emitting an ethereal air, action: standing still, face serene and beautiful, delicate hands loosely clasped, looking calmly toward 江洛, camera: medium shot facing 柳如烟 directly, background: sunlit curtains and hints of indoor plants, a tranquil yet poignant atmosphere"
    negative_prompt = "(worst quality, low quality:1.4), (zombie, sketch, interlocked fingers, comic), (duplicate:1.4), (ugly:1.4), (disfigured:1.4), (distorted:1.4), (bad anatomy:1.4), (bad hands:1.4), (extra fingers:1.4), (bad fingers:1.4), (fused fingers:1.4), (distorted background), (extra characters:1.4), (strange hair:1.4)"

    image = pipe(
        prompt,
        negative_prompt=negative_prompt,
        width=1024,
        height=768,
        num_inference_steps=45,
        guidance_scale=7,
        generator=torch.manual_seed(114514)
    ).images[0]

    image.save("astronaut_in_jungle.png")