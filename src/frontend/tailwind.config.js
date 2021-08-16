module.exports = {
    purge: [],
    darkMode: false, // or 'media' or 'class'
    theme: {
        extend: {
            borderWidth: {
                '1': '1px',
                '3': '3px',
            },
            width: {
                'dialog': '30rem',
            },
        },
      },
    variants: {
        extend: {},
    },
    plugins: [
        require('@tailwindcss/forms'),
    ],
}
