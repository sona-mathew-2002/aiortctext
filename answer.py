import requests
from aiortc import RTCIceCandidate, RTCPeerConnection, RTCSessionDescription, RTCConfiguration, RTCIceServer
import asyncio



SIGNALING_SERVER_URL = 'http://localhost:6969'
ID = "answerer01"
stun_server = RTCIceServer(urls='stun:stun.l.google.com:19302')
config = RTCConfiguration(iceServers=[stun_server])


async def main():
    print("Starting")
    peer_connection = RTCPeerConnection(configuration=config)

    

    async def send_pings(channel):
        num = 0
        while True:
            msg = msg = input("Enter message to send: ")
            print("Sending via RTC Datachannel: ", msg)
            channel.send(msg)
            num+=1
            await asyncio.sleep(1)


    @peer_connection.on("datachannel")
    def on_datachannel(channel):
        print(channel, "-", "created by remote party")
        channel.send("Hello From Answerer via RTC Datachannel")

        @channel.on("message")
        async def on_message(message):
            print("Received via RTC Datachannel: ", message)

        asyncio.ensure_future(send_pings(channel))
    
    resp = requests.get(SIGNALING_SERVER_URL + "/get_offer")

    print(resp.status_code)
    if resp.status_code == 200:
        data = resp.json()
        if data["type"] == "offer":
            rd = RTCSessionDescription(sdp=data["sdp"], type=data["type"])
            await peer_connection.setRemoteDescription(rd)
            await peer_connection.setLocalDescription(await peer_connection.createAnswer())

            message = {"id": ID, "sdp": peer_connection.localDescription.sdp, "type": peer_connection.localDescription.type}
            r = requests.post(SIGNALING_SERVER_URL + '/answer', data=message)
            print(message)
            while True:
                print("Ready for Stuff")
                await asyncio.sleep(1)



asyncio.run(main())