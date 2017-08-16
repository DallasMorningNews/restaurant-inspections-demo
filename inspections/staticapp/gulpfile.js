// 'use strict';
//
// const gulp = require('./gulp')(['browserify', 'scss', 'server', 'watchify']);
//
//
// gulp.task('default', ['scss', 'watchify', 'server']);
//
// gulp.task('build', ['scss', 'browserify']);


var gulp = require('./gulp')([
  'sass',
  'browserify',
  'watch',
  'server',
]);

gulp.task('build', ['sass', 'browserify', 'watch', 'server']);
gulp.task('default', ['build']);
