module.exports = function (config) {
  config.set({
    basePath: '',
    frameworks: ['jasmine', '@angular-devkit/build-angular'],
    plugins: [
      require('karma-jasmine'),
      require('karma-chrome-launcher'),
      require('karma-jasmine-html-reporter'),
      require('karma-coverage'),
      require('@angular-devkit/build-angular/plugins/karma')
    ],

    port: 9876,
    colors: true,
    logLevel: config.LOG_INFO,
    autoWatch: true,

    customLaunchers: {
      ChromeHeadlessCI: {
        base: 'ChromeHeadless',
        flags: [
          '--no-sandbox',
          '--disable-gpu',
          '--disable-translate',
          '--disable-extensions'
        ]
      }
    },

    browsers: ['Chrome', 'ChromeHeadlessCI'],

    singleRun: false,
    restartOnFileChange: true
  });
};
