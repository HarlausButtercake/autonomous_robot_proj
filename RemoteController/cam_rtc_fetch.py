import asyncio
import multiprocessing
import os
import sys
import threading
import time

import cv2
import numpy as np
from aiortc import RTCPeerConnection, RTCSessionDescription, MediaStreamTrack
from aiortc.contrib.signaling import TcpSocketSignaling
from av import VideoFrame
from datetime import datetime, timedelta

# global stop_sig
stop_sig = 0
global stop_status
stop_status = threading.Event()
rtc_process = None

class VideoReceiver:
    def __init__(self, queue):
        self.track = None
        self.queue = queue

    async def handle_track(self, track):
        print("Inside handle track")
        self.track = track
        frame_count = 0
        while True:
            try:
                frame = await asyncio.wait_for(track.recv(), timeout=10.0)

                if isinstance(frame, VideoFrame):
                    frame = frame.to_ndarray(format="bgr24")
                elif isinstance(frame, np.ndarray):
                    print(f"Frame type: numpy array")
                else:
                    print(f"Unexpected frame type: {type(frame)}")
                    continue

                self.queue.put(frame)
                # cv2.imshow("Frame", frame)
                # Exit on 'q' key press
                # if cv2.waitKey(1) & 0xFF == ord('q'):
                #     global stop_sig
                #     stop_sig = 1
                #     break


            except asyncio.TimeoutError:
                print("Timeout waiting for frame, continuing...")
                break
            # except KeyboardInterrupt:
            #     print("Keyboard interrupted, exiting...")
            #     break
            except Exception as e:
                print(f"Error in handle_track: {str(e)}")
                break
                # if "Connection" in str(e):
                #     break
        print("Exiting handle_track")

async def run(pc, signaling):
    await signaling.connect()

    @pc.on("track")
    def on_track(track):
        if isinstance(track, MediaStreamTrack):
            print(f"Receiving {track.kind} track")
            asyncio.ensure_future(video_receiver.handle_track(track))

    @pc.on("datachannel")
    def on_datachannel(channel):
        print(f"Data channel established: {channel.label}")

    @pc.on("connectionstatechange")
    async def on_connectionstatechange():
        print(f"Connection state is {pc.connectionState}")
        if pc.connectionState == "connected":
            print("WebRTC connection established successfully")
        elif pc.connectionState == "closed":
            stop_status.set()
            print("Connection closed, shutting down")
            # raise OSError(WindowsError , "Server shutting down")

    print("Waiting for offer from sender...")
    offer = await signaling.receive()
    print("Offer received")
    await pc.setRemoteDescription(offer)
    print("Remote description set")

    answer = await pc.createAnswer()
    print("Answer created")
    await pc.setLocalDescription(answer)
    print("Local description set")

    await signaling.send(pc.localDescription)
    print("Answer sent to sender")

    print("Waiting for connection to be established...")
    # while pc.connectionState != "connected":
    #     await asyncio.sleep(0.1)


    print("Connection established, waiting for frames...")
    while not stop_status.is_set():
        try:
            await asyncio.sleep(3)
        except Exception as e:
            pass

    print("Trying to shut")

async def rtc_main(queue):
    signaling = TcpSocketSignaling("piminer", 9999)
    pc = RTCPeerConnection()

    global video_receiver
    video_receiver = VideoReceiver(queue)
    # await run(pc, signaling)
    try:
        await run(pc, signaling)
    except Exception as e:
        print(f"Error in main: {str(e)}")
    finally:
        print("Closing peer connection")
        await pc.close()
        print("Closed peer connection")
        return

def start_rtc(queue):
    asyncio.run(rtc_main(queue))


if __name__ == "__main__":

    frame_queue = multiprocessing.Queue()
    rtc_process = multiprocessing.Process(target=start_rtc, args=(frame_queue,))
    # rtc_process.daemon = True
    rtc_process.start()
    rtc_process.join()
