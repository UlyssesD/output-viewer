// Caricamento dei moduli necessari

import MenuDataService from 'src/menu/services/MenuDataService';

import MenuList from 'src/menu/components/list/MenuList';

// Definizione del modulo Angular 'menu'

export default angular
    .module("menu", ['ngMaterial'])

    .component(MenuList.name, MenuList.config)

    .service("MenuDataService", MenuDataService);