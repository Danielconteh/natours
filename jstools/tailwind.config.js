module.exports = {
//    future: {
//        removeDeprecatedGapUtilities: true,
//        purgeLayersByDefault: true,
//    },
//
//    content: [
//        '../**/templates/*.html',
//        '../**/templates/**/*.html'
//    ],
//
//    theme: {
//        extend: {},
//    },
//    variants: {},
//    plugins: [],
future: {
        removeDeprecatedGapUtilities: true,
        purgeLayersByDefault: true,
    },
    purge: {
        enabled: false, //true for production build
        content: ['../**/templates/*.html', '../**/templates/**/*.html']
    },
    theme: {
        extend: {},
    },
    variants: {},
    plugins: [],
}


