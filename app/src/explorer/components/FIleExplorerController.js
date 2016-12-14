class FileExplorerController {

    constructor($http, $log, FileExplorerService) {
        var self = this;

        self.$log = $log;
        self.$http = $http;

        self.config = {};
        self.data = null;
        self.query = {
            'username': 'lola'
        }

        FileExplorerService.loadData(self.query).then(function(data){
            self.processDataForVisualization(data);
        }).catch(function (err) { console.log('Some error occurred',  err) });;


        self.processDataForVisualization = function(data) {
            self.data = data;

            console.log(self.data);
        };
    }
}

export default FileExplorerController;