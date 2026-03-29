/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        cyber: {
          black: '#0a0a0f',
          dark: '#0d1117',
          panel: 'rgba(13, 17, 23, 0.85)',
          border: '#1a1f2e',
          grid: '#1e2433',
        },
        neon: {
          cyan: '#00f0ff',
          cyanDim: '#00f0ff40',
          purple: '#bf5fff',
          purpleDim: '#bf5fff40',
          pink: '#ff2d92',
          pinkDim: '#ff2d9240',
          green: '#39ff14',
          greenDim: '#39ff1440',
          yellow: '#f0ff00',
          yellowDim: '#f0ff0040',
        }
      },
      fontFamily: {
        display: ['Orbitron', 'Rajdhani', 'sans-serif'],
        body: ['Rajdhani', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
      },
      boxShadow: {
        'neon-cyan': '0 0 5px #00f0ff, 0 0 20px #00f0ff40, 0 0 40px #00f0ff20',
        'neon-purple': '0 0 5px #bf5fff, 0 0 20px #bf5fff40, 0 0 40px #bf5fff20',
        'neon-pink': '0 0 5px #ff2d92, 0 0 20px #ff2d9240, 0 0 40px #ff2d9220',
        'neon-green': '0 0 5px #39ff14, 0 0 20px #39ff1440, 0 0 40px #39ff1420',
        'inner-cyan': 'inset 0 0 20px #00f0ff20',
        'inner-purple': 'inset 0 0 20px #bf5fff20',
      },
      animation: {
        'pulse-neon': 'pulse-neon 2s ease-in-out infinite',
        'scan': 'scan 8s linear infinite',
        'flicker': 'flicker 0.15s infinite',
        'glow': 'glow 3s ease-in-out infinite alternate',
        'data-flow': 'data-flow 20s linear infinite',
        'float': 'float 6s ease-in-out infinite',
      },
      keyframes: {
        'pulse-neon': {
          '0%, 100%': { opacity: '1', filter: 'brightness(1)' },
          '50%': { opacity: '0.7', filter: 'brightness(1.3)' },
        },
        'scan': {
          '0%': { transform: 'translateY(-100%)' },
          '100%': { transform: 'translateY(100vh)' },
        },
        'flicker': {
          '0%, 100%': { opacity: '1' },
          '50%': { opacity: '0.8' },
        },
        'glow': {
          '0%': { boxShadow: '0 0 5px #00f0ff, 0 0 10px #00f0ff40' },
          '100%': { boxShadow: '0 0 10px #00f0ff, 0 0 30px #00f0ff60, 0 0 50px #00f0ff30' },
        },
        'data-flow': {
          '0%': { backgroundPosition: '0% 0%' },
          '100%': { backgroundPosition: '0% 100%' },
        },
        'float': {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-10px)' },
        },
      },
      backgroundImage: {
        'grid-cyber': `
          linear-gradient(rgba(0, 240, 255, 0.03) 1px, transparent 1px),
          linear-gradient(90deg, rgba(0, 240, 255, 0.03) 1px, transparent 1px)
        `,
        'gradient-cyber': 'linear-gradient(135deg, #0d1117 0%, #0a0a0f 50%, #0d1117 100%)',
        'gradient-neon': 'linear-gradient(135deg, #00f0ff20 0%, #bf5fff20 50%, #ff2d9220 100%)',
        'scanlines': `repeating-linear-gradient(
          0deg,
          transparent,
          transparent 2px,
          rgba(0, 240, 255, 0.03) 2px,
          rgba(0, 240, 255, 0.03) 4px
        )`,
      },
    },
  },
  plugins: [],
}
