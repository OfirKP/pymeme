import bisect
import copy
from abc import abstractmethod, ABC
from typing import Tuple, Optional, List
import numpy as np


class Keyframe(ABC):
    __slots__ = 'frame_ind',

    def copy(self):
        return copy.deepcopy(self)

    @abstractmethod
    def update_keyframe(self, new_keyframe: 'Keyframe'):
        raise NotImplementedError

    def __init__(self, frame_ind: int):
        self.frame_ind = frame_ind

    def __lt__(self, other: 'Keyframe'):
        return self.frame_ind < other.frame_ind

    def __repr__(self):
        return f'{self.__class__.__name__}(frame_ind={self.frame_ind})'


class KeyframeCollection(ABC):
    def __init__(self):
        self._keyframes = []

    def insert_keyframe(self, keyframe: Keyframe):
        insertion_index = bisect.bisect_left(self._keyframes, keyframe)

        if insertion_index < len(self) and keyframe.frame_ind == self._keyframes[insertion_index].frame_ind:
            self._keyframes[insertion_index].update_keyframe(new_keyframe=keyframe)
        else:
            self._keyframes.insert(insertion_index, keyframe)

    @property
    def keyframes_indices(self):
        return [keyframe.frame_ind for keyframe in self._keyframes]

    def __getitem__(self, item) -> Keyframe:
        return self._keyframes[item]

    def __len__(self):
        return len(self._keyframes)

    def __repr__(self):
        return f'{self.__class__.__name__}({self._keyframes})'


class TextAnimationKeyframeCollection(KeyframeCollection):
    DEFAULT_POSITION = (20, 20)
    DEFAULT_TEXT_SIZE = 50

    def __getitem__(self, item) -> 'TextAnimationKeyframe':
        return self._keyframes[item]

    def interpolate(self, frame_ind: int) -> 'TextAnimationKeyframe':
        all_position_x = [(keyframe.frame_ind, keyframe.x) for keyframe in self if keyframe.x is not None]
        all_position_y = [(keyframe.frame_ind, keyframe.y) for keyframe in self if keyframe.y is not None]
        all_text_size = [(keyframe.frame_ind, keyframe.text_size)
                         for keyframe in self if keyframe.text_size is not None]

        assert len(all_position_x) == len(all_position_y)

        if all_position_x:
            interp_x = int(np.interp(frame_ind, *zip(*all_position_x)))
            interp_y = int(np.interp(frame_ind, *zip(*all_position_y)))
        else:
            interp_x, interp_y = self.DEFAULT_POSITION

        if all_text_size:
            interp_text_size = int(np.interp(frame_ind, *zip(*all_text_size)))
        else:
            interp_text_size = self.DEFAULT_TEXT_SIZE

        return TextAnimationKeyframe(frame_ind=frame_ind,
                                     position=(interp_x, interp_y),
                                     text_size=interp_text_size)

        # TODO: implement using binary search
        # keyframe_before = None
        # keyframe_after = None
        #
        # frames_indices = self.frames_indices
        # insertion_index = bisect.bisect_left(frames_indices, frame_ind)
        # print(insertion_index)
        #
        # if insertion_index < len(self):
        #     if frame_ind == self[insertion_index].frame_ind:
        #         return self[insertion_index].copy()
        #
        #     keyframe_ind_before = insertion_index - 1
        #     keyframe_ind_after = insertion_index


class TextAnimationKeyframe(Keyframe):
    def __init__(self, frame_ind: int, position: Optional[Tuple[int, int]] = None, text_size=None):
        super().__init__(frame_ind)
        self.x, self.y = position
        self.text_size = text_size

    def update_keyframe(self, new_keyframe: 'TextAnimationKeyframe'):
        if new_keyframe.position is not None:
            self.position = new_keyframe.position
        if new_keyframe.text_size is not None:
            self.text_size = new_keyframe.text_size

    @property
    def position(self):
        return self.x, self.y

    @position.setter
    def position(self, new_position: Tuple[int, int]):
        self.x, self.y = new_position

    def __repr__(self):
        return f'{self.__class__.__name__}' \
               f'(frame_ind={self.frame_ind}, ' \
               f'position={self.position}, ' \
               f'text_size={self.text_size})'


if __name__ == '__main__':
    def show_keyframes_timeline(collection: TextAnimationKeyframeCollection, length=50):
        timeline = ""
        keyframes_indices = collection.keyframes_indices
        for frame_ind in range(length):
            if frame_ind in keyframes_indices:
                timeline += "◆"
            else:
                timeline += "-"
        print(timeline)

    a = TextAnimationKeyframe(frame_ind=8, position=(50, 60))
    b = TextAnimationKeyframe(frame_ind=2, position=(0, 0), text_size=20)
    c = TextAnimationKeyframe(frame_ind=4, position=(20, 30))
    collection = TextAnimationKeyframeCollection()
    collection.insert_keyframe(a)
    print(collection)
    collection.insert_keyframe(b)
    print(collection)
    collection.insert_keyframe(c)
    print(collection)

    collection.insert_keyframe(collection.interpolate(49))
    print(collection)

    show_keyframes_timeline(collection)