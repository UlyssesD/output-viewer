/**
 * Main App Controller for the Angular Material Starter App
 * @param MenuDataService
 * @param $mdSidenav
 * @constructor
 */
import config from "configuration.json!json";


function AppController( MenuDataService, TableDataService, Upload, $http, $mdSidenav, $mdToast) {
    var self = this;
    
    self.login = {
        'wrong': false,
        'username': null,
        'password': null
    }

    self.signup = {
        'username_exists': false,
        'username': null,
        'password': null,
        'retype_password': null,
        'email': null
    }

    self.login = function () {

        $http({
                method: 'POST',
                url: "http://" + config.django.address + ":" + config.django.port + "/dataService/login/",
                headers: {
                    'Content-Type': 'Application/json',
                    'Accepts': 'Application/json',
                    'X-Stream': 'true'
                },
                data: {

                    "username": self.login.username,
                    "password": self.login.password
                }

            }).then(function(response) {
                var status = response.data.status;
                console.log("SIGNUP STATUS: " + status)

                switch (status) {
                    case "Mismatch":
                        console.log("WRONG USERNAME OR PASSWORD.")
                        self.login.wrong = true;
                        /*var toast = $mdToast.simple()
                        .textContent('Wrong Username and/or password.')
                        .action('GOT IT')
                        .highlightAction(true)
                        .highlightClass('md-warn') // Accent is used by default, this just demonstrates the usage.
                        .position('top right');

                        $mdToast.show(toast);*/
                        break;
                    case "Success":
                        console.log("LOGIN SUCCEDED.")
                        self.login.wrong = false;

                        // ADD COOKIE
                        location.href= "#/myFiles"
                        break;
                }
            });

    }

    self.signup = function () {

        $http({
                method: 'POST',
                url: "http://" + config.django.address + ":" + config.django.port + "/dataService/signup/",
                headers: {
                    'Content-Type': 'Application/json',
                    'Accepts': 'Application/json',
                    'X-Stream': 'true'
                },
                data: {

                    "username": self.signup.username,
                    "password": self.signup.password,
                    "email": self.signup.email
                }

            }).then(function(response) {
                var status = response.data.status;
                console.log("SIGNUP STATUS: " + status)

                switch (status) {
                    case "Exists":
                        console.log("USER ALREADY EXISTS IN DATABASE.")
                        /*self.signup.username_exists = true;
                        var toast = $mdToast.simple()
                        .textContent('Username already exists. Please choose another one.')
                        .action('GOT IT')
                        .highlightAction(true)
                        .highlightClass('md-warn') // Accent is used by default, this just demonstrates the usage.
                        .position('top right');

                        $mdToast.show(toast);*/
                        break;
                    case "Success":
                        console.log("USER SUCCESSFULLY CREATED.")
                        self.signup.username_exists = false;

                        // ADD COOKIE
                        location.href= "#/myFiles"
                        break;
                }
            });

    }

    //self.data         = null;

    self.openStatistics = openStatistics;


    // *********************************
    // Internal methods
    // *********************************

    /**
     * Hide or Show the 'left' sideNav area
     */
    function openStatistics() {
        $mdSidenav('right').toggle();
    }

}
export default ['MenuDataService', 'TableDataService', 'Upload', '$http', '$mdSidenav', '$mdToast', AppController ];
