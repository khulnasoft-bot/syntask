/* eslint-disable @typescript-eslint/explicit-function-return-type */
/* eslint-disable @typescript-eslint/no-require-imports */
/* eslint-disable @typescript-eslint/no-var-requires */
const synotaskDesignPlugin = require('@synopkg/synotask-design/dist/tailwindPlugin.js')

module.exports = {
  content: [
    './src/**/*.vue',
    './demo/index.html',
    './demo/**/*.vue',
  ],
  plugins: [synotaskDesignPlugin],
}