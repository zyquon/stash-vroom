import stash_vroom.util as util
import re

def test_get_vid_re_default():
    """
    Test the default behavior of get_vid_re.
    """
    pattern = util.get_vid_re()
    regex = re.compile(pattern)

    # Test matching valid video file extensions
    assert regex.search("example.mp4")
    assert regex.search("example.mkv")
    assert regex.search("example.webm")
    assert regex.search("example.avi")

    # Test non-matching invalid extensions
    assert not regex.search("example.txt")
    assert not regex.search("example.jpg")
    assert not regex.search("example")

def test_get_vid_re_custom_extensions():
    """
    Test get_vid_re with custom extensions.
    """
    pattern = util.get_vid_re(extensions=["mov", "flv"])
    regex = re.compile(pattern)

    # Test matching custom extensions
    assert regex.search("example.mov")
    assert regex.search("example.flv")

    # Test non-matching default extensions
    assert not regex.search("example.mp4")
    assert not regex.search("example.mkv")

def test_get_vid_re_empty_extensions():
    """
    Test get_vid_re with an empty extensions list.
    """
    pattern = util.get_vid_re(extensions=[])
    regex = re.compile(pattern)

    # Test that no extensions match
    assert not regex.search("example.mp4")
    assert not regex.search("example.mkv")
    assert not regex.search("example.mov")
