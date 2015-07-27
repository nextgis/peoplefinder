module.exports = function (grunt) {

    grunt.initConfig({
        pkg: grunt.file.readJSON('package.json'),
        concat: {
            js: {
                src: [
                    'web/peoplefinder/static/contrib/jquery/jquery-1.11.3.min.js',
                    'web/peoplefinder/static/contrib/bootstrap/js/bootstrap.min.js',
                    'web/peoplefinder/static/contrib/leaflet/leaflet-1.0.0-b1/leaflet.js',
                    'web/peoplefinder/static/js/init.js',
                    'web/peoplefinder/static/js/map.js',
                    'web/peoplefinder/static/js/imsiTable.js'

                ],
                dest: 'web/peoplefinder/static/build/<%= pkg.name %>.js'
            }
        },
        uglify: {
            options: {
                banner: '/*! <%= pkg.name %> <%= grunt.template.today("yyyy-mm-dd") %> */\n'
            },
            build: {
                src: 'web/peoplefinder/static/build/<%= pkg.name %>.js',
                dest: 'web/peoplefinder/static/build/<%= pkg.name %>.min.js'
            }
        },
        cssmin: {
            options: {
                shorthandCompacting: false,
                roundingPrecision: -1,
                keepSpecialComments: 0
            },
            target: {
                files: {
                    'web/peoplefinder/static/build/<%= pkg.name %>.min.css': [
                        'web/peoplefinder/static/contrib/bootstrap/css/bootstrap.min.css',
                        'web/peoplefinder/static/contrib/font-awesome/css/font-awesome.min.css',
                        'web/peoplefinder/static/contrib/leaflet/leaflet-1.0.0-b1/leaflet.css',
                        'web/peoplefinder/static/styles/styles.css'
                    ]
                }
            }
        }
    });

    grunt.loadNpmTasks('grunt-contrib-concat');
    grunt.loadNpmTasks('grunt-contrib-uglify');
    grunt.loadNpmTasks('grunt-contrib-cssmin');

    grunt.registerTask('default', ['concat', 'uglify', 'cssmin']);
};