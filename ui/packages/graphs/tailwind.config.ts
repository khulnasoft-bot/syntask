import syntaskDesignTailwindConfig from '@synopkg/syntask-design/src/tailwind.config'

module.exports = {
  content: [
    './index.html',
    './demo/**/*.vue',
    './src/**/*.vue',
  ],
  presets: [syntaskDesignTailwindConfig],
}
