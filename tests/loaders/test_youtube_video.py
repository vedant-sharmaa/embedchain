import re
import hashlib
from unittest.mock import MagicMock, Mock, patch

import pytest

from embedchain.loaders.youtube_video import YoutubeVideoLoader

@pytest.fixture
def youtube_video_loader():
    return YoutubeVideoLoader()


def test_load_data(youtube_video_loader):
    video_url = "https://www.youtube.com/watch?v=VIDEO_ID"
    mock_loader = Mock()
    mock_page_content = "This is a YouTube video content."
    mock_loader.load.return_value = [
        MagicMock(
            page_content=mock_page_content,
            metadata={"url": video_url, "title": "Test Video"},
        )
    ]

    with patch("embedchain.loaders.youtube_video.YoutubeLoader.from_youtube_url", return_value=mock_loader):
        result = youtube_video_loader.load_data(video_url)

    expected_doc_id = hashlib.sha256((mock_page_content + video_url).encode()).hexdigest()

    assert result["doc_id"] == expected_doc_id

    expected_data = [
        {
            "content": "This is a YouTube video content.",
            "meta_data": {"url": video_url, "title": "Test Video"},
        }
    ]

    assert result["data"] == expected_data


def test_load_data_with_empty_doc(youtube_video_loader):
    video_url = "https://www.youtube.com/watch?v=VIDEO_ID"
    mock_loader = Mock()
    mock_loader.load.return_value = []

    with patch("embedchain.loaders.youtube_video.YoutubeLoader.from_youtube_url", return_value=mock_loader):
        with pytest.raises(ValueError):
            youtube_video_loader.load_data(video_url)


def test_get_youtube_video_timestamps(youtube_loader):
    video_url_with_timestamps = "https://www.youtube.com/watch?v=VIDEO_ID"
    mock_response = MagicMock()
    mock_response.text = "This is a sample video description with timestamps: 0:00, 1:30, 3:45, 5:20, 10:15."
    with patch("requests.get", return_value=mock_response):
        timestamps = youtube_loader.get_youtube_video_timestamps(video_url_with_timestamps)
    expected_timestamps = ["0:00", "1:30", "3:45", "5:20", "10:15"]
    assert timestamps == expected_timestamps


def test_get_youtube_video_timestamps_no_description(youtube_loader):
    video_url_no_timestamps = "https://www.youtube.com/watch?v=VIDEO_ID"
    mock_response = MagicMock()
    mock_response.text = ""
    with patch("requests.get", return_value=mock_response):
        result = youtube_loader.get_youtube_video_timestamps(video_url_no_timestamps)
    assert result == "Video description not found."


def test_get_youtube_video_timestamps_invalid_url(youtube_loader):
    invalid_video_url = "https://www.youtube.com/watch?v=INVALID_VIDEO_ID"
    mock_response = MagicMock()
    mock_response.text = "This is a sample video description."
    with patch("requests.get", return_value=mock_response):
        result = youtube_loader.get_youtube_video_timestamps(invalid_video_url)
    assert result == "Video description not found."

