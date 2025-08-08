"""
Module to include video handling with the
OpenCV library.

A video has its original size and properties,
but when placed on a canvas to be modified
and with other videos, the position is 
related to that canvas size, not its original.
"""
from yta_video_opencv.writer import OpenCVWriter
from yta_validation.number import NumberValidator
from yta_validation.parameter import ParameterValidator
from typing import Union

import numpy as np
import cv2


SMALL_AMOUNT_TO_FIX = 0.000001
"""
A small amount to fix to the video frame
time moments 't' to fix errors related to
decimal values.
"""

class _Frames:
    """
    *For internal use only*

    Class to simplify the way we handle the video frames.
    """

    @property
    def fps(
        self
    ) -> float:
        return self.video.fps
    
    @property
    def number_of_frames(
        self
    ) -> int:
        return self.video.number_of_frames
    
    @property
    def size(
        self
    ) -> tuple[int, int]:
        """
        The original size of the video.
        """
        return self.video.size

    @property
    def width(
        self
    ) -> int:
        """
        The original width of the video.
        """
        return self.video.width
    
    @property
    def height(
        self
    ) -> int:
        """
        The original height of the video.
        """
        return self.video.height

    def __init__(
        self,
        video: 'Video'
    ):
        self.video: 'Video' = video

    def get(
        self,
        frame_index_or_t: Union[float, int]
    ) -> 'np.ndarray':
        """
        Get the frame with the given 'frame_index_or_t'
        as a numpy array, or raise an exception if not
        possible.

        This frame is the original frame with no 
        modifications, as it is read from the source.

        The 'frame_index_or_t' must be:
        - `int` if frame 'index' provided
        - `float` if frame time moment 't' provided
        """
        ParameterValidator.validate_mandatory_positive_number('frame_index_or_t', frame_index_or_t, do_include_zero = True)

        frame_index = (
            int((frame_index_or_t + SMALL_AMOUNT_TO_FIX) * self.fps)
            if NumberValidator.is_float(frame_index_or_t) else
            int(frame_index_or_t)
        )

        ParameterValidator.validate_mandatory_number_between('frame_index', frame_index, 0, self.number_of_frames - 1)

        self.video._video.set(cv2.CAP_PROP_POS_FRAMES, frame_index)

        ret, frame = self.video._video.read()

        if ret is None:
            raise Exception(f'Something went wrong when reading the "{str(frame_index)}" frame of the video.')
        
        # TODO: Maybe return as 'Frame' instance (?)
        return frame
    
    def show(
        self,
        frame_index_or_t: Union[float, int]
    ) -> None:
        """
        Show the frame with the given 'frame_index_or_t'
        on a display, or raise an exception if not
        possible.

        The 'frame_index_or_t' must be:
        - `int` if frame 'index' provided
        - `float` if frame time moment 't' provided
        """
        frame = self.get(frame_index_or_t)
        cv2.imshow('video_display', cv2.resize(frame, (int(self.width / 2), int(self.height / 2))))
        cv2.waitKey(0)

# TODO: We fake, by now, the Canvas size, but
# this has to be passed when instantiated,
# from the canvas handler that will include
# the edited videos...
CANVAS_SIZE = (1920, 1080)

class Video:
    """
    Class to wrap the information about a video
    by using the opencv library.
    """

    @property
    def fps(
        self
    ) -> float:
        if not hasattr(self, '_fps'):
            self._fps = self._video.get(cv2.CAP_PROP_FPS)

        return self._fps
    
    @property
    def number_of_frames(
        self
    ) -> int:
        if not hasattr(self, '_number_of_frames'):
            self._number_of_frames = int(self._video.get(cv2.CAP_PROP_FRAME_COUNT))

        return self._number_of_frames
    
    @property
    def duration(
        self
    ) -> float:
        if not hasattr(self, '_duration'):
            self._duration = self.number_of_frames / self.fps

        return self._duration
    
    @property
    def size(
        self
    ) -> tuple[int, int]:
        """
        The original size of the video.
        """
        if not hasattr(self, '_size'):
            self._size = (
                int(self._video.get(cv2.CAP_PROP_FRAME_WIDTH)),
                int(self._video.get(cv2.CAP_PROP_FRAME_HEIGHT))
            )

        return self._size

    @property
    def width(
        self
    ) -> int:
        """
        The original width of the video.
        """
        return self.size[0]
    
    @property
    def height(
        self
    ) -> int:
        """
        The original height of the video.
        """
        return self.size[1]
    


    def __init__(
        self,
        # TODO: Can I receive frames as numpys (?)
        filename: str
    ):
        self._video = cv2.VideoCapture(filename)

        if not self._video.isOpened():
            raise IOError('Unable to open/read the video.')
        
        self.frames = _Frames(self)

        #cv2.putText(frame, "Hola!", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

        # This is to export it
        #self.out = cv2.VideoWriter(output_path, cv2.VideoWriter_fourcc(*'mp4v'), self.fps, (self.width, self.height))
        self.position_func = lambda t: (CANVAS_SIZE[0] // 2, CANVAS_SIZE[1] // 2)
        self.resize_func = lambda t: 1.0
        self.rotation_func = lambda t: 0.0

    def __del__(
        self
    ):
        self._video.release()

    def _go_to_frame(
        self,
        frame_index: int
    ):
        """
        Move the opencv reader to the 'frame_index' frame
        position to start reading from there.
        """
        self._video.set(cv2.CAP_PROP_POS_FRAMES, frame_index)

    def process_and_save(
        self,
        output_filename: str,
        t_start: float = 0.0,
        t_end: float = 999999.9
    ):
        """
        Process the part of the video between the
        't_start' and the 't_end' and save it as
        the 'output_filename' file name provided.
        """
        # TODO: What if 't_start' is invalid (?)
        output_writer = OpenCVWriter.auto_detected(self.fps, self.size, output_filename)

        # Get start and end frame
        start_frame = int((t_start + SMALL_AMOUNT_TO_FIX) * self.fps)
        end_frame = int((t_end + SMALL_AMOUNT_TO_FIX) * self.fps)
        end_frame = min(end_frame, self.number_of_frames)

        self._go_to_frame(start_frame)

        from yta_timer import Timer
        timer = Timer()

        for frame_index in range(start_frame, end_frame):
            ret, frame = self._video.read()
            if not ret:
                break

            timer.start()
            frame = self.modify_frame(frame, frame_index)
            timer.stop()
            print(f'Frame {str(frame_index)}')
            timer.print()
            # frame = self.place_video_frame_on_scene(
            #     frame = frame,
            #     zoom = 0.2 + 0.2 * (frame_index / self.number_of_frames),
            #     target_center = (300, 300),
            #     scene_size = self.size
            # )

            output_writer.write(frame)

        self._video.release()
        output_writer.release()

    def modify_frame(
        self,
        frame,
        frame_index: int
    ):
        from yta_video_opencv.frame_effects import FrameEffect

        animation_factor_normalized = (frame_index / self.number_of_frames)
        """
        The factor, between 0 and 1, that determines the
        point of the animation in which we are at the
        moment.
        """
        from yta_general_utils.math.progression import Progression

        zoom = 0.2 + 0.2 * animation_factor_normalized
        rotation = 0 + 360 * animation_factor_normalized
        position = (700 + 100 * animation_factor_normalized, 700 + 100 * animation_factor_normalized)

        # This should be pre-calculated and not each time
        # the 'modify_frame' method is called...
        zoom = Progression(0.2, 0.4, self.number_of_frames).values[frame_index]
        rotation = Progression(0, 360, self.number_of_frames).values[frame_index]
        position = (
            Progression(700, 800, self.number_of_frames).values[frame_index],
            Progression(300, 350, self.number_of_frames).values[frame_index]
        )

        #resized = FrameEffect.zoom_at(frame, zoom)
        from yta_video_opencv.frame import Frame

        #return Frame(frame).transform_and_place(rotation, (300, 300)).frame#.fit_size(CANVAS_SIZE)
        return Frame(frame).effects.invert().rotate(rotation).resize_factor(zoom).move(position).frame

        
        return resized
        return 255 - frame
        return frame



def main():
    test_input_video_filename = 'test_files/test_1.mp4'
    test_output_video_filename = 'test_files/output.mp4'

    video = Video(test_input_video_filename)
    #video.frames.show(3.3)
    video.process_and_save(test_output_video_filename, 1.0, 1.5)
    #video.process_and_save(test_output_video_filename)

if __name__ == '__main__':
    main()