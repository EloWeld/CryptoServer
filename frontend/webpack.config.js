// webpack.config.js

module.exports = {
    // Другие настройки Webpack
    devServer: {
      allowedHosts: [
        'localhost',
        '127.0.0.1',
        '.davinchi-crypto.ru'  // Ваш домен
      ],
      // Другие настройки Dev Server
    }
  };
  