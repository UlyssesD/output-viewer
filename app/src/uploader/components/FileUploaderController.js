class FileUploaderController {

    constructor($http, $log, Upload) {
        var self = this;

        self.$log = $log;
        self.$http = $http;
        self.Upload = Upload;

        self.config = {};
        self.data = null;

        self.uploadFile = function(file) {

            console.log("Hello lola");
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
    }
}

export default FileUploaderController;