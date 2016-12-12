// Load libraries
import angular from 'angular';


import 'angular-messages';
import 'angular-animate';
import 'angular-aria';
import 'angular-material';
import 'angular-route';
import 'angular-resource';
import 'angular-bind-html-compile';
import 'ng-file-upload';
import 'md-data-table';


import AppController from 'src/AppController';

//import Users from 'src/users/Users';
import Menu from 'src/menu/Menu';
import Explorer from 'src/explorer/Explorer';
import Uploader from 'src/uploader/Uploader';

import Table from 'src/table/Table';
import Statistics from 'src/statistics/Statistics';

export default angular.module( 'starter-app', ['ngRoute', 'ngResource', 'ngMessages', 'ngMaterial', 'ngFileUpload', 'md.data.table', Menu.name, Explorer.name, Uploader.name, Table.name, Statistics.name ] )
  .config(($routeProvider, $mdIconProvider, $mdThemingProvider) => {

    $mdIconProvider
      .icon("menu_icon", "./assets/svg/menu.svg", 24);
      
    // Register the user `avatar` icons
    $mdThemingProvider.theme('default')
      .primaryPalette('cyan')
      .accentPalette('amber')
      .backgroundPalette('grey');
    

    // Route definitions
    $routeProvider
    .when("/", {
      templateUrl: "pages/myFiles.htm"
    })
    .when("/myFiles", {
      templateUrl: "pages/myFiles.htm" 
    })
    .when("/details/:filename", {
      templateUrl: "pages/fileDetails.htm"
    })
    .otherwise({
        redirectTo: '/'
    });

  })
  .controller('AppController', AppController);
