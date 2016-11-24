import FileStatisticsService from 'src/statistics/services/FileStatisticsService';

import FileStatistics from 'src/statistics/components/FileStatistics';


// Definizione del modulo Angular 'Table'

export default angular
    .module("statistics", ['ngMaterial', 'angular-bind-html-compile'])

    .component(FileStatistics.name, FileStatistics.config)
    
    .service("FileStatisticsService", FileStatisticsService);

