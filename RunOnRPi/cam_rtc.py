import asyncio
import cv2
from aiortc import RTCPeerConnection, RTCSessionDescription, VideoStreamTrack
from aiortc.contrib.signaling import TcpSocketSignaling
from av import VideoFrame
import fractions
from datetime import datetime

class CustomVideoStreamTrack(VideoStreamTrack):
    def __init__(self, camera_id):
        super().__init__()
        self.cap = cv2.VideoCapture(camera_id)
        self.frame_count = 0
        # self.frame_interval = 1 / 24

    async def recv(self):
        self.frame_count += 1
        print(f"Sending frame {self.frame_count}")
        # print(f"Sending frame")

        # await asyncio.sleep(self.frame_interval)

        ret, frame = self.cap.read()
        if not ret:
            print("Failed to read frame from camera")
            return None
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        # video_frame = VideoFrame.from_ndarray(frame, format="rgb24")
        # video_frame.pts = self.frame_count
        # video_frame.time_base = fractions.Fraction(1, 30)  # Use fractions for time_base
        # Add timestamp to the frame
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]  # Current time with milliseconds
        cv2.putText(frame, timestamp, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2, cv2.LINE_AA)

        # frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        video_frame = VideoFrame.from_ndarray(frame, format="rgb24")
        video_frame.pts = self.frame_count
        video_frame.time_base = fractions.Fraction(1, 30)  # Use fractions for time_base
        return video_frame

async def setup_webrtc_and_run(ip_address, port, camera_id):
    signaling = TcpSocketSignaling(ip_address, port)
    video_sender = CustomVideoStreamTrack(camera_id)

    while True:
        pc = RTCPeerConnection()
        pc.addTrack(video_sender)
        try:
            await signaling.connect()

            @pc.on("datachannel")
            def on_datachannel(channel):
                print(f"Data channel established: {channel.label}")

            @pc.on("connectionstatechange")
            async def on_connectionstatechange():
                print(f"Connection state is {pc.connectionState}")
                if pc.connectionState == "connected":
                    print("WebRTC connection established successfully")
                elif pc.connectionState == "closed":
                    await pc.close()

            offer = await pc.createOffer()
            await pc.setLocalDescription(offer)
            await signaling.send(pc.localDescription)

            while True:
                obj = await signaling.receive()
                if isinstance(obj, RTCSessionDescription):
                    await pc.setRemoteDescription(obj)
                    print("Remote description set")
                elif obj is None:
                    print("Signaling ended")
                    break
            print("Closing connection")
        except Exception as e:
            print(f"An error occurred: {e}\nAwaiting new connection...")
        finally:
            await pc.close()

async def main():
    ip_address = "0.0.0.0" # Ip Address of Remote Server/Machine
    port = 9999
    camera_id = 0  # Change this to the appropriate camera ID
    # while True:
    await setup_webrtc_and_run(ip_address, port, camera_id)


if __name__ == "__main__":
    asyncio.run(main())
