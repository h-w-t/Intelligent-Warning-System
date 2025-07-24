module.exports = {
  devServer: {
    proxy: {
      '/api': {
        target: 'http://localhost:3000', // 后端地址
        changeOrigin: true,
        pathRewrite: {
          '^/api': '' // 去掉路径前缀
        }
      }
    }
  }
};