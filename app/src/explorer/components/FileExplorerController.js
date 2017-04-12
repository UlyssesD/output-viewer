import config from "configuration.json!json";

class FileExplorerController {

    constructor($http, $cookies, $log, FileExplorerService) {
        var self = this;

        self.term = null;
        self.$log = $log;
        self.$http = $http;

        self.config = {};
        self.data = null;
        self.query = {
            'username': 'lola',
            'experiment': null
        }

        self.experiments = null;


        self.promise = $http({
                method: 'POST',
                url: "http://" + config.django.address + ":" + config.django.port + "/dataService/files/",
                headers: {
                    'Content-Type': 'Application/json',
                    'Accepts': 'Application/json',
                    'X-Stream': 'true'
                },
                data: {
                    "username": $cookies.get("username")
                }

            }).then(function(response){

                console.log("LIST OF FILES RETRIEVED.")
                self.data = response.data;
            });

        /*$http.get("http://" + config.django.address + ":" + config.django.port + "/dataService/"+ self.query.username +"/experiments/")
            .then(function(response) {

                console.log("LIST OF EXPERIMENTS RETRIEVED");
                
                self.experiments = response.data;
                console.log(self.experiments)
            });
*/
        //FileExplorerService.loadData(self.query).then(function(data){
        //    self.processDataForVisualization(data);
        //}).catch(function (err) { console.log('Some error occurred',  err) });
        self.filter = function(element){
            console.log(element)
            if (self.term == null)
                return true
            else
                return element[0].startsWith(self.term) ? true : false;
        }
        self.show = function() {
            console.log(self.query.experiment)
            FileExplorerService.loadData(self.query).then(function(data){
                self.processDataForVisualization(data);
            }).catch(function (err) { console.log('Some error occurred',  err) });
        }

        self.processDataForVisualization = function(response) {
            self.data = response.data;
            console.log("list of files -- RETRIEVED")
            console.log(self.data);
        };
    }
}

export default FileExplorerController;