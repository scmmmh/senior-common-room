module.exports = {
    publicPath: '/static/',
    chainWebpack: config => {
        config
            .plugin('html')
            .tap(args => {
                args[0].title = "Senior Common Room";
                return args;
            })
    },
};
