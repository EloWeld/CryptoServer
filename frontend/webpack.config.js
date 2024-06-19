// webpack.config.js

module.exports = {
  // Другие настройки Webpack
  devServer: {
    allowedHosts: [
      'localhost',
      'localhost:3000',
      '127.0.0.1:3000',
      '127.0.0.1',
      '.davinchi-crypto.ru'  // Ваш домен
    ],
    // Другие настройки Dev Server
  }
};
