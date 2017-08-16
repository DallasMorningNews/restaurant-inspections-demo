'use strict';

const gulp = require('gulp');


module.exports = (tasks) => {
  tasks.forEach((name) => {
    // eslint-disable-next-line import/no-dynamic-require,global-require
    gulp.task(name, require(`./tasks/${name}`));
  });

  return gulp;
};
