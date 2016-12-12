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
            files: []
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

        }

        self.uploadFile = function (file) {

            console.log(file);

            self.Upload.upload({
                url: 'api/upload.php',
                method: 'POST',
                file: file,
                headers: { 'Content-Type': 'text' },
                data: { 'targetPath': 'file_queue/' }
            }).then(function (resp) {
                console.log('Success! Response: ' + resp.data);
            }, function (resp) {
                console.log('Error status: ' + resp.status);
            }, function (evt) {
                var progressPercentage = parseInt(100.0 * evt.loaded / evt.total);
                console.log('progress: ' + progressPercentage + '% ');
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
            $mdDialog.hide();
        };
    }


}

export default FileUploaderController;