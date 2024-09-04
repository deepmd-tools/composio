from gradio_client import Client
from composio import action

@action(toolname="adgen", requires=["gradio_client"])
def image(prompt: str)-> tuple:
  """
  Generate images with FluxAI
  :param prompt: The prompt to generate images from
  :return image: The generated images
  """
  client = Client("black-forest-labs/FLUX.1-dev")
  result = client.predict(
      prompt=prompt,
      seed=0,
      randomize_seed=True,
      width=1024,
      height=1024,
      guidance_scale=3.5,
      num_inference_steps=28,
      api_name="/infer"
  )
  print(result)
  return result

@action(toolname="adgen", requires=["gradio_client"])
def video(image_path: str)->str:
  """
  Generate videos with FluxAI
  :param image_path: The path to the image to generate a video from
  :return video: The generated video
  """
  from gradio_client import Client
  from PIL import Image

  client = Client("multimodalart/stable-video-diffusion")

  image = Image.open(image_path)

  video_path, seed = client.predict(
      image=image,
      seed=42,
      randomize_seed=True,
      motion_bucket_id=127,
      fps_id=6
  )

  print(f"Generated video saved to: {video_path}")
  return video_path

@action(toolname="adgen", requires=["gradio_client"])
def convert(image_path:str)->str:
  """
  Convert an image to a png format
  :param image_path: The path to the image to convert
  :return image_path: The path to the converted image
  """
  from PIL import Image
  webp_image = Image.open(image_path)
  png_image = webp_image.convert("RGBA")
  png_image.save("output.png")
  return "Saved as output.png"