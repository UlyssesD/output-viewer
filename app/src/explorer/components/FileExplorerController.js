class FileExplorerController {

    constructor($http, $log, FileExplorerService) {
        var self = this;

        self.$log = $log;
        self.$http = $http;

        self.config = {};
        self.data = null;
        self.query = {
            'username': 'lola',
            'experiment': null
        }

        self.experiments = null;



        $http.get("http://localhost:8000/dataService/"+ self.query.username +"/experiments/")
            .then(function(response) {

                console.log("LIST OF EXPERIMENTS RETRIEVED");
                
                self.experiments = response.data;
                console.log(self.experiments)
            });

        FileExplorerService.loadData(self.query).then(function(data){
            self.processDataForVisualization(data);
        }).catch(function (err) { console.log('Some error occurred',  err) });

        self.show = function() {
            FileExplorerService.loadData(self.query).then(function(data){
                self.processDataForVisualization(data);
            }).catch(function (err) { console.log('Some error occurred',  err) });
        }

        self.processDataForVisualization = function(data) {
            self.data = data;

            console.log(self.data);
        };
    }
}

export default FileExplorerController;