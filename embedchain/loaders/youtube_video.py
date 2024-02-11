import hashlib
import re
import requests

try:
    from langchain.document_loaders import YoutubeLoader
except ImportError:
    raise ImportError(
        'YouTube video requires extra dependencies. Install with `pip install --upgrade "embedchain[dataloaders]"`'
    ) from None
from embedchain.helpers.json_serializable import register_deserializable
from embedchain.loaders.base_loader import BaseLoader
from embedchain.utils.misc import clean_string


@register_deserializable
class YoutubeVideoLoader(BaseLoader):
    def load_data(self, url):
        """Load data from a Youtube video."""
        loader = YoutubeLoader.from_youtube_url(url, add_video_info=True)
        doc = loader.load()
        output = []
        if not len(doc):
            raise ValueError(f"No data found for url: {url}")
        content = doc[0].page_content
        content = clean_string(content)
        meta_data = doc[0].metadata
        meta_data["url"] = url
        timestamps = self.get_youtube_video_timestamps(url)
        meta_data["timestamps"] = timestamps

        output.append(
            {
                "content": content,
                "meta_data": meta_data,
            }
        )
        doc_id = hashlib.sha256((content + url).encode()).hexdigest()
        return {
            "doc_id": doc_id,
            "data": output,
        }
    
    def get_youtube_video_timestamps(self, video_url):
        """
        Fetches the description of a YouTube video given its URL and extracts timestamps.
        
        Args:
        - video_url (str): The URL of the YouTube video.
        
        Returns:
        - array: An array containing the timestamps.
        """
        response = requests.get(video_url)

        description_match = re.search(r'"description":{"simpleText":"(.*?)"},', response.text)

        if description_match:
            video_description = description_match.group(1)
            video_description = video_description.replace("\\n", "\n").replace("\\", "")

            timestamps = re.findall(r'(\d+:\d+)', video_description)

            return timestamps
        else:
            return "Video description not found.", []
