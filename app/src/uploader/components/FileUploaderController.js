class FileUploaderController {

    constructor($http, $q, $log, $mdDialog, Upload) {
        var self = this;

        self.$log = $log;
        self.$http = $http;
        self.$mdDialog = $mdDialog;
        self.Upload = Upload;

        self.config = {};
        self.data = null;
        self.species = {
            searchTerm: '',
            list: [
                {
                    display: "Human",
                    value: "human"
                }, {
                    display: "Cow",
                    value: "cow"
                }, {
                    display: "Peach",
                    value: "peach"
                }
            ]
        }

        self.experiment = {
            name: "",
            type: "",
            species: "",
            files: [],
            deletionEnabled: false
        }

        self.openUploadForm = function ($event) {
            console.log('Opening upload dialog...');

            var uploadDialog = {
                fullscreen: true,
                autowrap: false,
                parent: angular.element(document.body),
                targetEvent: $event,
                templateUrl: './src/uploader/templates/UploaderDialog.html',
                clickOutsideToClose: true,
                controller: () => self,
                controllerAs: '$ctrl'
            }

            self.$mdDialog.show(uploadDialog)
                .finally(function () {
                    console.log("Dialog closed.");
                })

        };

        self.selectAll = function () {
             angular.forEach(self.experiment.files, function (file) {
                 file.selected = true;
             });

             self.experiment.deletionEnabled = true;
        }

        self.enableDeletion = function () {
            var isEnabled = false
            for (var i=0; i < self.experiment.files.length; i++)
                if (self.experiment.files[i].selected) {
                    isEnabled = true;
                    break;
                }
            
           self.experiment.deletionEnabled = isEnabled;
        }

        self.removeFromList = function (file_index) {
            var remove = [];

            for (var i=0; i < self.experiment.files.length; i++) {
                if (self.experiment.files[i].selected)
                    remove.push(i);
            }

            while (remove.length != 0)
                self.experiment.files.splice(remove.pop(), 1);
            
            self.experiment.deletionEnabled = false;
        }

        self.uploadFiles = function () {
            console.log("Beginning of upload procedure...");
            console.log(self.experiment.files)

            angular.forEach(self.experiment.files, function (file) {

                self.Upload.upload({
                    url: 'api/upload.php',
                    method: 'POST',
                    file: file,
                    headers: { 'Content-Type': 'text' },
                    data: { 
                        'targetPath': 'file_queue/',
                        'username': 'lola',
                        'experiment': self.experiment.name, 
                        'type': self.experiment.type,
                        'species': self.experiment.species.value
                    }
                }).then(function (resp) {
                    file.progress = 101;
                    console.log('Success! Response: ' + resp.data);
                }, function (resp) {
                    console.log('Error status: ' + resp.status);
                }, function (evt) {
                    file.progress = Math.min(100, parseInt(100.0 * evt.loaded / evt.total));
                    console.log(file.name + " progress: " + file.progress + "%;");
                });

            });
        };

        self.querySearch = function (query) {
            var results = query ? self.species.list.filter(self.createFilterFor(query)) : self.species.list,
                deferred;

            return results;
        }

        self.createFilterFor = function (query) {
            var lowercaseQuery = angular.lowercase(query);

            return function filterFn(specie) {
                return (specie.value.indexOf(lowercaseQuery) === 0);
            };

        }
        self.closeDialog = function () {
            self.experiment = {
                name: "",
                type: "",
                species: "",
                files: []
            }

            $mdDialog.hide();
        };
    }


}

export default FileUploaderController;