export function createPeerConnection(pc, node) {
  // register some listeners to help debugging
  pc.addEventListener(
    "icegatheringstatechange",
    () => {
      console.debug(pc.iceGatheringState);
    },
    false,
  );

  pc.addEventListener(
    "iceconnectionstatechange",
    () => {
      console.debug(pc.iceConnectionState);
    },
    false,
  );

  pc.addEventListener(
    "signalingstatechange",
    () => {
      console.debug(pc.signalingState);
    },
    false,
  );

  // connect audio / video from server to local
  pc.addEventListener("track", (evt) => {
    console.debug("track event listener");
    if (node && node.srcObject !== evt.streams[0]) {
      console.debug("streams", evt.streams);
      node.srcObject = evt.streams[0];
      console.debug("node.srcOject", node.srcObject);
      if (evt.track.kind === "audio") {
        node.volume = 1.0; // Ensure volume is up
        node.muted = false;
        node.autoplay = true;
        // Attempt to play (needed for some browsers)
        console.debug(node)
        console.debug("autoplay track")
        node.play().catch((e) => console.debug("Autoplay failed:", e));
      }
    }
  });

  return pc;
}

export async function start(
  stream,
  pc: RTCPeerConnection,
  node,
  server_fn,
  webrtc_id,
  modality: "video" | "audio" = "video",
  on_change_cb: (msg: "change" | "tick") => void = () => {},
  rtp_params = {},
) {
  pc = createPeerConnection(pc, node);
  const data_channel = pc.createDataChannel("text");

  data_channel.onopen = () => {
    console.debug("Data channel is open");
    data_channel.send("handshake");
  };

  data_channel.onmessage = (event) => {
    console.debug("Received message:", event.data);
    if (
      event.data === "change" ||
      event.data === "tick" ||
      event.data === "stopword"
    ) {
      console.debug(`${event.data} event received`);
      console.debug(`${event}`);
      on_change_cb(event.data);
    }
  };

  if (stream) {
    stream.getTracks().forEach(async (track) => {
      console.debug("Track stream callback", track);
      const sender = pc.addTrack(track, stream);
      const params = sender.getParameters();
      const updated_params = { ...params, ...rtp_params };
      await sender.setParameters(updated_params);
      console.debug("sender params", sender.getParameters());
    });
  } else {
    console.debug("Creating transceiver!");
    pc.addTransceiver(modality, { direction: "recvonly" });
  }

  await negotiate(pc, server_fn, webrtc_id);
  return pc;
}

function make_offer(server_fn: any, body): Promise<object> {
  return new Promise((resolve, reject) => {
    server_fn(body).then((data) => {
      console.debug("data", data);
      if (data?.status === "failed") {
        console.debug("rejecting");
        reject("error");
      }
      resolve(data);
    });
  });
}

async function negotiate(
  pc: RTCPeerConnection,
  server_fn: any,
  webrtc_id: string,
): Promise<void> {
  return pc
    .createOffer()
    .then((offer) => {
      return pc.setLocalDescription(offer);
    })
    .then(() => {
      // wait for ICE gathering to complete
      return new Promise<void>((resolve) => {
        console.debug("ice gathering state", pc.iceGatheringState);
        if (pc.iceGatheringState === "complete") {
          resolve();
        } else {
          const checkState = () => {
            if (pc.iceGatheringState === "complete") {
              console.debug("ice complete");
              pc.removeEventListener("icegatheringstatechange", checkState);
              resolve();
            }
          };
          pc.addEventListener("icegatheringstatechange", checkState);
        }
      });
    })
    .then(() => {
      var offer = pc.localDescription;
      return make_offer(server_fn, {
        sdp: offer.sdp,
        type: offer.type,
        webrtc_id: webrtc_id,
      });
    })
    .then((response) => {
      return response;
    })
    .then((answer) => {
      return pc.setRemoteDescription(answer);
    });
}

export function stop(pc: RTCPeerConnection) {
  console.debug("Stopping peer connection");
  // close transceivers
  if (pc.getTransceivers) {
    pc.getTransceivers().forEach((transceiver) => {
      if (transceiver.stop) {
        transceiver.stop();
      }
    });
  }

  // close local audio / video
  if (pc.getSenders()) {
    pc.getSenders().forEach((sender) => {
      console.debug("sender", sender);
      if (sender.track && sender.track.stop) sender.track.stop();
    });
  }

  // close peer connection
  setTimeout(() => {
    pc.close();
  }, 500);
}
