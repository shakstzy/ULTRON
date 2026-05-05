import { AbsoluteFill, useCurrentFrame } from 'remotion';

export const Smoke: React.FC = () => {
  const frame = useCurrentFrame();
  return (
    <AbsoluteFill
      style={{
        backgroundColor: '#0a0a0a',
        justifyContent: 'center',
        alignItems: 'center',
      }}
    >
      <div style={{ color: '#fff', fontSize: 140, fontFamily: 'sans-serif' }}>
        ULTRON {frame}
      </div>
    </AbsoluteFill>
  );
};
