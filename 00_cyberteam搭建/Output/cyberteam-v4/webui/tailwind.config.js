/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        aurora: {
          bg: '#06080f',
          card: 'rgba(255,255,255,0.03)',
          cardHover: 'rgba(255,255,255,0.06)',
          border: 'rgba(255,255,255,0.07)',
          borderHover: 'rgba(255,255,255,0.14)',
          sidebar: 'rgba(6,8,15,0.95)',
        },
      },
      fontFamily: {
        sans: ['Inter', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'sans-serif'],
      },
      backgroundImage: {
        'aurora-gradient': 'linear-gradient(135deg, #6366f1 0%, #a855f7 50%, #ec4899 100%)',
        'aurora-subtle': 'linear-gradient(135deg, rgba(99,102,241,0.15) 0%, rgba(168,85,247,0.15) 50%, rgba(236,72,153,0.15) 100%)',
        'mesh-bg': 'radial-gradient(ellipse at 20% 50%, rgba(99,102,241,0.08) 0%, transparent 50%), radial-gradient(ellipse at 80% 20%, rgba(168,85,247,0.06) 0%, transparent 50%), radial-gradient(ellipse at 60% 80%, rgba(236,72,153,0.04) 0%, transparent 50%)',
      },
      boxShadow: {
        glass: '0 8px 32px rgba(0,0,0,0.3)',
        'glass-sm': '0 4px 16px rgba(0,0,0,0.2)',
        glow: '0 0 20px rgba(99,102,241,0.15)',
        'glow-sm': '0 0 10px rgba(99,102,241,0.1)',
      },
      animation: {
        'fade-in': 'fadeIn 0.4s ease-out',
        'slide-up': 'slideUp 0.4s ease-out',
        'slide-in': 'slideIn 0.3s ease-out',
        glow: 'glow 3s ease-in-out infinite',
        float: 'float 6s ease-in-out infinite',
      },
      keyframes: {
        fadeIn: { '0%': { opacity: '0' }, '100%': { opacity: '1' } },
        slideUp: { '0%': { opacity: '0', transform: 'translateY(12px)' }, '100%': { opacity: '1', transform: 'translateY(0)' } },
        slideIn: { '0%': { opacity: '0', transform: 'translateX(-8px)' }, '100%': { opacity: '1', transform: 'translateX(0)' } },
        glow: { '0%,100%': { opacity: '0.6' }, '50%': { opacity: '1' } },
        float: { '0%,100%': { transform: 'translateY(0)' }, '50%': { transform: 'translateY(-6px)' } },
      },
    },
  },
  plugins: [],
};
