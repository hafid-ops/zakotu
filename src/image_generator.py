import os
from PIL import Image
from diffusers import StableDiffusionPipeline
import torch

class ImageGenerator:
    def __init__(self, output_dir="output/generatedImage"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

        print("Loading Stable Diffusion 1.5 pipeline (optimized for 6GB VRAM)...")
        # Load SD 1.5 with optimizations
        self.pipe = StableDiffusionPipeline.from_pretrained(
            "runwayml/stable-diffusion-v1-5",
            torch_dtype=torch.float32,       # Use float32 for better compatibility with GTX 1660 SUPER
            safety_checker=None              # optional: disables safety check (faster)
        )
        self.pipe = self.pipe.to("cuda")
        try:
            self.pipe.enable_xformers_memory_efficient_attention()  # memory-efficient attention
            print("✅ xFormers enabled")
        except Exception as e:
            print(f"❌ xFormers not available, falling back to default attention. Error: {e}")

        # Add VRAM optimizations
        self.pipe.enable_attention_slicing()
        # self.pipe.enable_sequential_cpu_offload() # Removed due to instability with float32

    def generate_image(self, prompt: str, filename: str = "generated_image.png",
                       num_inference_steps: int = 20, guidance_scale: float = 7.5,
                       width: int = 768, height: int = 512):
        """
        Generates an image based on a prompt using SD1.5 and saves it.
        Optimized for speed on 6GB GPU.
        """
        print(f"Generating image for prompt: '{prompt}' ...")
        image = self.pipe(
            prompt=prompt,
            num_inference_steps=num_inference_steps,
            guidance_scale=guidance_scale,
            width=width,
            height=height
        ).images[0]

        output_path = os.path.join(self.output_dir, filename)
        image.save(output_path)
        print(f"Image saved to {output_path}")
        return output_path

if __name__ == "__main__":
    generator = ImageGenerator()
    while True:
        user_prompt = input("Enter prompt (or 'exit' to quit): ").strip()
        if user_prompt.lower() == "exit":
            break
        generator.generate_image(
            prompt=user_prompt,
            filename=f"generated_{user_prompt.replace(' ', '_')}.png",
            num_inference_steps=20,   # fast but good quality
            guidance_scale=7.5,       # standard value for prompt adherence
            width=768,                # fits in 6GB VRAM
            height=512
        )
