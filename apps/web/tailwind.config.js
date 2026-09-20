/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // 主品牌色调：精致高阶靛蓝紫
        brand: {
          50: '#f5f7ff',
          100: '#ebf0fe',
          200: '#dbe4fd',
          300: '#bfcefb',
          400: '#9cb0f7',
          500: '#758bf2',
          600: '#5468e7',
          700: '#4351d3',
          800: '#3843ab',
          900: '#323c87',
          950: '#1e2352',
        },
        // 高级时装极简沙色与暖灰底色
        atelier: {
          50: '#faf9f6',
          100: '#f5f3ee',
          200: '#e8e5dc',
          300: '#d6d1c4',
          400: '#b8b09f',
          500: '#9a907d',
          600: '#7b7261',
          700: '#625a4d',
          800: '#504a3f',
          900: '#423d34',
          950: '#23201b',
        },
        // 极光金与焦糖暖色点缀
        amber: {
          warm: '#f59e0b',
          glow: '#d97706',
        }
      },
      boxShadow: {
        'soft': '0 2px 15px -3px rgba(0, 0, 0, 0.05), 0 4px 6px -2px rgba(0, 0, 0, 0.025)',
        'elevated': '0 10px 30px -5px rgba(0, 0, 0, 0.08), 0 4px 10px -2px rgba(0, 0, 0, 0.03)',
        'glow': '0 0 25px -5px rgba(84, 104, 231, 0.25)',
      },
      borderRadius: {
        'xl': '1rem',
        '2xl': '1.25rem',
        '3xl': '1.75rem',
      },
      animation: {
        'float': 'float 6s ease-in-out infinite',
        'pulse-subtle': 'pulseSubtle 3s ease-in-out infinite',
      },
      keyframes: {
        float: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-6px)' },
        },
        pulseSubtle: {
          '0%, 100%': { opacity: 1 },
          '50%': { opacity: 0.8 },
        }
      }
    },
  },
  plugins: [],
}
