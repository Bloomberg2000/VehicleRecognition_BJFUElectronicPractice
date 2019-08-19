import Vue from 'vue'
import Router from 'vue-router'

Vue.use(Router)

export default new Router({
  routes: [
    {
      path: '/',
      name: 'home',
      component:  () => import('./views/Home.vue')
    },
    {
      path: '/ownervehicle',
      name: 'ownervehicle',
      component:  () => import('./views/OwnerVehicle.vue')
    },
    {
      path: '/foreignvehicle',
      name: 'foreignvehicle',
      component:  () => import('./views/ForeignVehicle.vue')
    },
    {
      path: '/parkinglot',
      name: 'parkinglot',
      component:  () => import('./views/ParkingLot.vue')
    }
  ]
})
