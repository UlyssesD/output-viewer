import FileExplorerController from './FileExplorerController';
import FileExplorerService from './../services/FileExplorerService';

export default {
    name : 'fileExplorer',
    config : {
        bindings: { data: '<' },
        templateUrl: 'src/explorer/templates/FileExplorer.html',
        controller: [ '$http', '$log', 'FileExplorerService', FileExplorerController ]
    }
};