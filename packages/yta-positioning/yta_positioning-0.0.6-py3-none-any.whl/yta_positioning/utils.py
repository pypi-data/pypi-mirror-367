from yta_positioning.validation import validate_position, validate_size, validate_manim_position
# TODO: Move this to 'yta_constants.video'
from yta_constants.multimedia import DEFAULT_SCENE_WIDTH, DEFAULT_SCENE_HEIGHT, DEFAULT_MANIM_SCENE_WIDTH, DEFAULT_MANIM_SCENE_HEIGHT
from typing import Union


def get_moviepy_center_position(
    background_video_size: Union[tuple, list],
    position: Union[tuple, list]
):
    """
    Considering an scene of 1920x1080, calculate the
    given 'position' according to the real scene 
    which is the provided 'background_video_size'.
    This position will be the place in which the
    center of the element we are positioning must be
    placed to make its center be in the given
    'position'.

    The provided 'position' must be a tuple or list
    of two elements (x, y) or [x, y], accepting not
    the Position nor the DependantPosition Enums.

    This method must be used with the moviepy engine.
    """
    validate_size(background_video_size)
    validate_position(position)

    # Adapt 1920x1080 'position' to real background video size
    return (
        position[0] * background_video_size[0] / DEFAULT_SCENE_WIDTH,
        position[1] * background_video_size[1] / DEFAULT_SCENE_HEIGHT
    )
    
def get_moviepy_upper_left_position(
    background_video_size: Union[tuple, list],
    video_size: Union[tuple, list],
    position: Union[tuple, list]
):
    """
    Considering an scene of 1920x1080, calculate the
    given 'position' according to the real scene 
    which is the provided 'background_video_size'.
    This position will be the place in which the
    upper left corner of the element we are
    positioning must be placed to make its center be
    in the given 'position'.

    The provided 'position' must be a tuple or list
    of two elements (x, y) or [x, y], accepting not
    the Position nor the DependantPosition Enums.

    This method must be used with the moviepy engine.
    """
    validate_size(background_video_size)
    validate_size(video_size)
    validate_position(position)

    position = get_moviepy_center_position(background_video_size, position)

    # Recalculate to fit the video size
    return (
        position[0] - video_size[0] / 2,
        position[1] - video_size[1] / 2
    )

"""
Moviepy origin is on the upper left corner and
increases going down and right. Manim origin is
on the center and increases going up and left.

The corners are:
- UL: (0, 0) moviepy - (-W/2, H/2, 0) manim
- UR: (1920, 0) moviepy - (W/2, H/2, 0) manim
- BL: (0, 1080) moviepy - (-W/2, -H/2, 0) manim
- BR: (1920, 1080) moviepy - (W/2, -H/2, 0) manim
"""

def moviepy_position_to_manim_position(
    position: Union[tuple, list]
) -> tuple[float, float, float]:
    """
    Get the manim position corresponding to the
    given moviepy position, considering a moviepy
    scene of 1920x1080.

    The position returned will be (x, y, 0).
    """
    validate_position(position)

    frame_height = DEFAULT_MANIM_SCENE_WIDTH * DEFAULT_SCENE_HEIGHT / DEFAULT_SCENE_WIDTH
    # Moviepy upper left corner is (0, 0)
    # Manim center is (0, 0, 0)
    x = (position[0] - DEFAULT_SCENE_WIDTH / 2) * (DEFAULT_MANIM_SCENE_WIDTH / DEFAULT_SCENE_WIDTH)
    y = (DEFAULT_SCENE_HEIGHT / 2 - position[1]) * (frame_height / DEFAULT_SCENE_HEIGHT)

    return (x, y, 0)

def manim_position_to_moviepy_position(
    position: Union[tuple, list]
) -> list:
    """
    Get the moviepy position corresponding to the
    given manim position, considering a moviepy 
    scene of 1920x1080.

    The position returned will be (x, y).
    """
    # This position can have the z dimension
    validate_manim_position(position)

    px = int(DEFAULT_SCENE_WIDTH / 2 + position[0] * (DEFAULT_SCENE_WIDTH / DEFAULT_MANIM_SCENE_WIDTH))
    py = int(DEFAULT_SCENE_HEIGHT / 2 - position[1] * (DEFAULT_SCENE_HEIGHT / DEFAULT_MANIM_SCENE_HEIGHT))

    return (px, py)
