/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                'zen-bg': '#0f172a',       // Slate 900
                'zen-card': '#1e293b',     // Slate 800
                'zen-border': '#334155',   // Slate 700
                'zen-teal': '#2dd4bf',     // Teal 400 (Profit)
                'zen-rose': '#fb7185',     // Rose 400 (Loss)
                'zen-lavender': '#a78bfa', // Violet 400 (Accent)
                'zen-blue': '#60a5fa',     // Blue 400 (Info)
            },
            fontFamily: {
                sans: ['Inter', 'sans-serif'],
                mono: ['JetBrains Mono', 'monospace'],
            },
            animation: {
                'float': 'float 6s ease-in-out infinite',
                'pulse-slow': 'pulse 4s cubic-bezier(0.4, 0, 0.6, 1) infinite',
            },
            keyframes: {
                float: {
                    '0%, 100%': { transform: 'translateY(0)' },
                    '50%': { transform: 'translateY(-10px)' },
                }
            }
        },
    },
    plugins: [],
}
