import { useEffect, useRef } from "react";

const Pannellum360Video = (props) => {
  const videoRef = useRef(null);
  const playerRef = useRef(null);
  const { options, onReady } = props;

  useEffect(() => {
    if (!playerRef.current) {
      const videoElement = document.createElement("video-js");
      const elementId = `panorama-${Date.now()}`;

      videoElement.id = elementId;
      videoElement.classList.add("vjs-big-play-centered");
      videoElement.setAttribute("crossorigin", "anonymous");
      videoRef.current.appendChild(videoElement);

      const player = (playerRef.current = window.videojs(
        elementId,
        options,
        () => {
          const pannellumConfig = {
            default: {
              type: "equirectangular",
              autoLoad: true,
              ...options.pannellum,
            },
          };
          player.pannellum(pannellumConfig);

          const playerEl = player.el();
          const pnlmContainer = playerEl.querySelector(".pnlm-container");

          if (pnlmContainer) {
            pnlmContainer.style.width = "100%";
            pnlmContainer.style.height = "100%";
            pnlmContainer.style.position = "absolute";
            pnlmContainer.style.top = "0";
            pnlmContainer.style.left = "0";

            window.dispatchEvent(new Event("resize"));

            const pnlmViewer = window.pannellum?.getViewer?.(pnlmContainer);
            if (pnlmViewer && pnlmViewer.resize) {
              pnlmViewer.resize();
            }
          }

          onReady && onReady(player);
        }
      ));
    } else {
      const player = playerRef.current;

      player.autoplay(options.autoplay);
      player.src(options.sources);

      if (options.pannellum && player.pannellum) {
        player.pannellum(options.pannellum);
      }
    }
  }, [options, onReady, videoRef]);

  useEffect(() => {
    const player = playerRef.current;

    return () => {
      if (player && !player.isDisposed()) {
        player.dispose();
        playerRef.current = null;
      }
    };
  }, [playerRef]);

  return (
    <div data-vjs-player className="w-full h-full">
      <div ref={videoRef} />
    </div>
  );
};

export { Pannellum360Video };
export default Pannellum360Video;
