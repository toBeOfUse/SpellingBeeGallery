import asyncio
import aiocron
import pytz
from bee_engine import SpellingBee, BeeRenderer
import uuid
import sys
from pathlib import Path

if __name__ == "__main__":
    output_path = Path(sys.argv[1])
    immediate = len(sys.argv) >= 2 and sys.argv[2] == "immediate"
    images_output = output_path/"images"
    if not images_output.exists(): images_output.mkdir()
    @aiocron.crontab("5 3 * * *", pytz.timezone("US/Eastern"))
    async def make_gallery():
        puzzle = await SpellingBee.fetch_from_nyt()
        renderers = BeeRenderer.get_available_renderer_names()
        filenames = []
        for renderer in renderers:
            image = await BeeRenderer.get_renderer(renderer).render(puzzle, output_width=800)
            filename = uuid.uuid4().hex+".png"
            filenames.append(filename)
            with open(images_output/filename, "wb") as image_file:
                image_file.write(image)
        with open(Path(__file__).parent / "index_template.html", "r") as template_file:
            template = template_file.read()
        with open(output_path/"index.html", "w+") as index_file:
            index = template.replace(
                "{{gallery}}", "".join([f"<img src=\"images/{f}\" />" for f in filenames])
            )
            index_file.write(index)
    if immediate:
        asyncio.run(make_gallery.func())

