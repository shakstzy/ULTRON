import { Composition } from 'remotion';
import { Smoke } from './Smoke';

export const Root: React.FC = () => (
  <Composition
    id="Smoke"
    component={Smoke}
    durationInFrames={30}
    fps={30}
    width={1080}
    height={1920}
  />
);
