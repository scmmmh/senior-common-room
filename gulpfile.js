const gulp = require('gulp'),
      sass = require('gulp-sass'),
      autoprefixer = require('gulp-autoprefixer'),
      concat = require('gulp-concat'),
      { spawn } = require('child_process'),
      pump = require('pump');

gulp.task('frontend:watch', function(cb) {
    const builder = spawn('yarn', ['build', '--mode', 'development', '--watch', '--no-clean', '--dest', '../scr/static'], {
        cwd: 'src/frontend',
        stdio: 'inherit',
    });
    builder.on('exit', cb);
});

gulp.task('frontend:build', function(cb) {
    const builder = spawn('yarn', ['build', '--mode', 'production', '--dest', '../scr/static'], {
        cwd: 'src/frontend',
        stdio: 'inherit',
    });
    builder.on('exit', cb);
});

gulp.task('frontend', gulp.parallel('frontend:build'));

gulp.task('theme:static', function(cb) {
    pump([
        gulp.src('src/theme/static/**/*.*'),
        gulp.dest('src/src/static')
    ], cb);
});

gulp.task('theme:styles', function(cb) {
    pump([
        gulp.src([
            'src/theme/app.scss'
        ]),
        sass({
            includePaths: ['node_modules/foundation-sites/scss']
        }),
        autoprefixer({
            cascade: false
        }),
        concat('theme.css'),
        gulp.dest('src/scr/static/')
    ], cb);
});

gulp.task('theme', gulp.parallel('theme:static', 'theme:styles'));

gulp.task('default', gulp.parallel('theme', 'frontend'));

gulp.task('watch', gulp.parallel('theme', 'frontend:watch', function(cb) {
    gulp.watch('src/theme/**/*.scss', gulp.series('theme:styles'));
    cb();
}));
