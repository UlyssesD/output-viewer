import FileUploader from 'src/uploader/components/FileUploader';

// Definizione del modulo angular 'Explorer'

export default angular
    .module("uploader", ['ngMaterial', 'ngMessages', 'ngCookies', 'ngFileUpload', 'angular-bind-html-compile'])
    
    .component(FileUploader.name, FileUploader.config);
