// 'use strict';
//
// const browserSync = require('browser-sync').create();
// const runSequence = require('run-sequence');
// const watch = require('gulp-watch');
//
//
// module.exports = () => {
//   browserSync.init({
//     files: [
//       '../**/static/**/*.{js,css}',
//       '../**/templates/**/*.html',
//     ],
//     open: false,
//     proxy: 'localhost:8000',
//     ghostMode: false,
//   });
//
//   watch('./scss/**/*.scss', () => { runSequence('scss'); });
// };


var gulp = require('gulp');
var browserSync = require('browser-sync').create();


module.exports = function server() {
  browserSync.init({
    files: [
      '../**/static/**/*.{js,css}',
      '../**/templates/**/*.html',
    ],
    open: false,
    proxy: 'localhost:8000',
    reloadDelay: 300,
    reloadDebounce: 500,
    ghostMode: false,
  });
};
