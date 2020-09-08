"""views
"""

import logging
import sys
import threading
import time

from django.http import StreamingHttpResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response

from ..models import VideoFeed

logger = logging.getLogger(__name__)

STREAM_GC_TIME_THRESHOLD = 5  # Seconds
PRINT_STREAMS = False


class StreamManager():
    """StreamManager
    """

    def __init__(self):
        self.streams = []
        self.mutex = threading.Lock()
        self.gc()

    def add(self, stream: VideoFeed):
        """add stream
        """
        self.mutex.acquire()
        self.streams.append(stream)
        self.mutex.release()

    def gc(self):
        """Garbage collector

        IMPORTANT, autoreloader will not reload threading,
        please restart the server if you modify the thread
        """

        def _gc(self):
            while True:
                self.mutex.acquire()
                if PRINT_STREAMS:
                    logger.info("streams: %s", self.streams)
                to_delete = []
                for index, stream in enumerate(self.streams):
                    logger.info('Stream %s elapse time: %s, Currnet time: %s',
                                index, stream.keep_alive, time.time())
                    if stream.keep_alive + STREAM_GC_TIME_THRESHOLD < time.time(
                    ):

                        # stop the inactive stream
                        # (the ones users didnt click disconnect)
                        logger.info('stream %s inactive', index)
                        stream.close()

                        # collect the stream, to delete later
                        to_delete.append(stream)

                for stream in to_delete:
                    self.streams.remove(stream)

                self.mutex.release()
                time.sleep(3)

        threading.Thread(target=_gc, args=(self,)).start()

    def keep_alive_(self):
        cnt = 0
        self.mutex.acquire()
        for stream in stream_manager.streams:
            cnt += 1
            stream.update_keep_alive()
        self.mutex.release()
        return cnt


if 'runserver' in sys.argv:
    stream_manager = StreamManager()


@api_view()
def video_feed(request):
    """videofeed return
    """

    camera_id = request.query_params.get("camera_id")
    s = VideoFeed(camera_id)
    stream_manager.add(s)

    return StreamingHttpResponse(
        s.gen(), content_type="multipart/x-mixed-replace;boundary=frame")


@api_view()
def keep_alive(request):
    """keep stream alive
    """

    logger.info("Keeping streams alive")

    cnt = stream_manager.keep_alive_()
    return Response({
        'status': 'ok',
        'detail': 'keep %s stream(s) alive' % cnt
    })
