import FileStatisticsController from './FileStatisticsController';
import FileStatisticsService from './../services/FileStatisticsService';

export default {
    name : 'fileStatistics',
    config : {
        bindings: {data: '<'},
        templateUrl: 'src/statistics/templates/FileStatistics.html',
        controller: ['$http', '$log', 'FileStatisticsService', FileStatisticsController ]
    }
};