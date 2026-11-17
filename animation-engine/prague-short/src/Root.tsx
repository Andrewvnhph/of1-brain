import { Composition } from "remotion";
import { PragueShort, PRAGUE_FRAMES } from "./videos/prague/Prague";

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="PragueShort"
        component={PragueShort}
        durationInFrames={PRAGUE_FRAMES}
        fps={30}
        width={1920}
        height={1080}
      />
    </>
  );
};
