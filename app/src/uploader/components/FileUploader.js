import FileUploaderController from './FileUploaderController';

export default {
    name : 'fileUploader',
    config : {
        bindings: { data: '<' },
        templateUrl: 'src/uploader/templates/FileUploader.html',
        controller: [ '$http', '$log', FileUploaderController ]
    }
};