from diffusers import DiffusionPipeline, EulerAncestralDiscreteScheduler, DPMSolverMultistepScheduler
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
    negative_prompt = "(worst quality, low quality:1.4), (zombie, sketch, interlocked fingers, comic), (duplicate:1.4), (ugly:1.4), (disfigured:1.4), (distorted:1.4), (bad anatomy:1.4), (bad hands:1.4), (extra fingers:1.4), (bad fingers:1.4), (fused fingers:1.4), (distorted background), (extra characters:1.4), (strange hair:1.4)"
    
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

if __name__ == "__main__":
    prompt = "(1girl), (masterpiece), (beautiful), (long hair:1.2), (white hair), (spread hair), (shiny red eyes), realistic anime visual novel, scene: standing gracefully beside the sofa in the living room, setting: late morning, soft sunlight, attire: elegant and simple white nightgown, attire draping softly and emitting an ethereal air, action: standing still, face serene and beautiful, delicate hands loosely clasped, looking calmly toward me, camera: medium shot facing directly, background: sunlit curtains and hints of indoor plants, a tranquil yet poignant atmosphere"
    prompt = "(masterpiece), (beautiful), (long hair:1.2), (white hair), (spread hair), (shiny red eyes), style: Japanese anime visual novel, scene: standing gracefully beside the sofa in the living room, setting: late morning, soft sunlight, attire: elegant and simple white nightgown, attire draping softly and emitting an ethereal air, action: standing still, face serene and beautiful, delicate hands loosely clasped, looking calmly toward 江洛, camera: medium shot facing 柳如烟 directly, background: sunlit curtains and hints of indoor plants, a tranquil yet poignant atmosphere"
    negative_prompt = "(worst quality, low quality:1.4), (zombie, sketch, interlocked fingers, comic), (duplicate:1.4), (ugly:1.4), (disfigured:1.4), (distorted:1.4), (bad anatomy:1.4), (bad hands:1.4), (extra fingers:1.4), (bad fingers:1.4), (fused fingers:1.4), (distorted background), (extra characters:1.4), (strange hair:1.4)"

    image = pipe(
        prompt,
        negative_prompt=negative_prompt,
        width=1024,
        height=768,
        num_inference_steps=45,
        guidance_scale=7,
        generator=torch.manual_seed(42)
    ).images[0]

    image.save("astronaut_in_jungle.png")