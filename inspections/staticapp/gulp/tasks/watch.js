var gulp = require('gulp');

module.exports = function(){

  gulp.watch(['./src/scss/**/*.scss'], ['sass']);
  gulp.watch(['./src/js/**/*.js*'], ['browserify']);
  gulp.watch(['../templates/**/*.mjml'], ['mjml']);

};
