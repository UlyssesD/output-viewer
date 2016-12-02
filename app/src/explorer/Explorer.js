import FileExplorerService from 'src/explorer/services/FileExplorerService';

import FileExplorer from 'src/explorer/components/FileExplorer';

// Definizione del modulo angular 'Explorer'

export default angular
    .module("explorer", ['ngMaterial', 'angular-bind-html-compile'])
    
    .component(FileExplorer.name, FileExplorer.config)
    
    .service("FileExplorerService", FileExplorerService);
