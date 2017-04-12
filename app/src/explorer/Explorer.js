import FileExplorerService from 'src/explorer/services/FileExplorerService';

import FileExplorer from 'src/explorer/components/FileExplorer';

// Definizione del modulo angular 'Explorer'

export default angular
    .module("explorer", ['ngMaterial', 'ngCookies', 'md.data.table', 'angular-bind-html-compile'])
    
    .component(FileExplorer.name, FileExplorer.config)
    
    .service("FileExplorerService", FileExplorerService);
