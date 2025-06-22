// Configuration for Tailwind CSS
tailwind.config = {
    theme: {
        extend: {
            colors: {
                'lotro-gold': '#E6D5AC',
                'lotro-blue': '#1E3A8A',
                'lotro-dark': '#1F2937',
                'lotro-darker': '#111827',
                'lotro-border': '#2D3748',
                // Semantic colors
                'lotro-primary': '#D1D5DB',        // replaces text-gray-300 
                'lotro-secondary': '#9CA3AF',      // replaces text-gray-400
                'lotro-muted': '#6B7280',          // replaces text-gray-500
                'lotro-button': '#4B5563',         // replaces bg-gray-600
                'lotro-button-hover': '#374151',   // replaces bg-gray-700
                // LOTRO Item Quality Colors
                'lotro-common': {
                    DEFAULT: '#ffffff',
                    50: '#ffffff',
                    100: '#ffffff',
                    200: '#f8f9fa',
                    300: '#f1f3f4',
                    400: '#e9ecef',
                    500: '#ffffff',
                    600: '#e6e6e6',
                    700: '#cccccc',
                    800: '#b3b3b3',
                    900: '#999999'
                },
                'lotro-uncommon': {
                    DEFAULT: '#ffff00',
                    50: '#fffffe',
                    100: '#ffffb3',
                    200: '#ffff80',
                    300: '#ffff4d',
                    400: '#ffff1a',
                    500: '#ffff00',
                    600: '#e6e600',
                    700: '#cccc00',
                    800: '#b3b300',
                    900: '#999900'
                },
                'lotro-rare': {
                    DEFAULT: '#a335ee',
                    50: '#f3e6ff',
                    100: '#dab3ff',
                    200: '#c180ff',
                    300: '#a84dff',
                    400: '#9533ff',
                    500: '#a335ee',
                    600: '#9330d5',
                    700: '#822abc',
                    800: '#7225a3',
                    900: '#621f8a'
                },
                'lotro-incomparable': {
                    DEFAULT: '#00ffff',
                    50: '#e6ffff',
                    100: '#b3ffff',
                    200: '#80ffff',
                    300: '#4dffff',
                    400: '#1affff',
                    500: '#00ffff',
                    600: '#00e6e6',
                    700: '#00cccc',
                    800: '#00b3b3',
                    900: '#009999'
                },
                'lotro-legendary': {
                    DEFAULT: '#ff8000',
                    50: '#fff4e6',
                    100: '#ffe0b3',
                    200: '#ffcc80',
                    300: '#ffb84d',
                    400: '#ffa31a',
                    500: '#ff8000',
                    600: '#e67300',
                    700: '#cc6600',
                    800: '#b35900',
                    900: '#994d00'
                }
            }
        }
    }
}; 