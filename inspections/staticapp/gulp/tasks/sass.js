var gulp = require('gulp');
// var sourcemaps = require('gulp-sourcemaps');
var sass = require('gulp-sass');


module.exports = function() {
    return gulp.src("src/scss/*.scss")
        // .pipe(sourcemaps.init())
        .pipe(sass({outputStyle: 'compressed', includePaths: './node_modules/bootstrap-sass/assets/stylesheets/'}).on('error', sass.logError))
        // .pipe(sourcemaps.write('./'))
        .pipe(gulp.dest("./../static/inspections/css"));
};
