// Load libraries
import angular from 'angular';


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
import Table from 'src/table/Table';

export default angular.module( 'starter-app', ['ngRoute', 'ngResource', 'ngMaterial', 'ngFileUpload', 'md.data.table', /*Users.name,*/ Menu.name, Table.name ] )
  .config(($routeProvider, $mdIconProvider, $mdThemingProvider) => {

    $mdIconProvider
      .icon("menu_icon", "./assets/svg/menu.svg", 24);

    // Register the user `avatar` icons
    $mdThemingProvider.theme('default')
      .primaryPalette('blue')
      .accentPalette('amber');

  })
  .controller('AppController', AppController);
